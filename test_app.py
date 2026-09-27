import pytest

from app import app, bills


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    bills.clear()

    with app.test_client() as test_client:
        yield test_client

    bills.clear()


def test_health_route(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_add_bill_and_show_on_home_page(client):
    response = client.post(
        "/bills",
        data={
            "name": "Netflix",
            "amount": "499",
            "due_date": "2026-10-01",
            "category": "Subscription",
            "status": "Pending",
            "notes": "Monthly",
        },
    )

    assert response.status_code == 302

    page = client.get("/")

    assert b"Netflix" in page.data
    assert b"499.00" in page.data


def test_invalid_bill_is_rejected(client):
    response = client.post(
        "/bills",
        data={
            "name": "",
            "amount": "-20",
            "due_date": "",
            "category": "Subscription",
            "status": "Pending",
        },
    )

    assert response.status_code == 400
    assert b"required" in response.data.lower()


def test_past_due_date_is_rejected(client):
    response = client.post(
        "/bills",
        data={
            "name": "Old Bill",
            "amount": "500",
            "due_date": "2020-01-01",
            "category": "Utility",
            "status": "Pending",
        },
    )

    assert response.status_code == 400
    assert b"due date cannot be in the past" in response.data.lower()


def test_api_returns_bills_and_summary(client):
    client.post(
        "/bills",
        data={
            "name": "Electricity",
            "amount": "1200",
            "due_date": "2026-10-05",
            "category": "Utility",
            "status": "Pending",
        },
    )

    response = client.get("/api/bills")

    assert response.status_code == 200
    assert response.json["bills"][0]["name"] == "Electricity"
    assert response.json["summary"]["total_due"] == 1200.0


def test_delete_bill_removes_data(client):
    client.post(
        "/bills",
        data={
            "name": "Rent",
            "amount": "15000",
            "due_date": "2026-10-01",
            "category": "Rent",
            "status": "Pending",
        },
    )

    bill_id = bills[0]["id"]

    response = client.post(
        f"/bills/{bill_id}/delete"
    )

    assert response.status_code == 302
    assert client.get("/api/bills").json["bills"] == []


def test_single_bill_api(client):
    response = client.post(
        "/bills",
        data={
            "name": "Netflix",
            "amount": "649",
            "due_date": "2030-01-15",
            "category": "Subscription",
            "status": "Pending",
            "notes": "Monthly subscription",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    response = client.get("/api/bills")

    assert response.status_code == 200

    bills_data = response.get_json()["bills"]

    netflix_bill = next(
        bill for bill in bills_data
        if bill["name"] == "Netflix"
    )

    response = client.get(
        f"/api/bills/{netflix_bill['id']}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["name"] == "Netflix"
    assert data["amount"] == 649.0
    assert data["category"] == "Subscription"


def test_single_bill_api_not_found(client):
    response = client.get("/api/bills/999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Bill not found."
    
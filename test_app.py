import pytest

import app


@pytest.fixture()
def client():
    app.app.config["TESTING"] = True
    app.bills.clear()
    app.next_id = 1

    with app.app.test_client() as test_client:
        yield test_client

    app.bills.clear()
    app.next_id = 1


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

    bill_id = app.bills[0]["id"]

    response = client.post(
        f"/bills/{bill_id}/delete"
    )

    assert response.status_code == 302
    assert client.get("/api/bills").json["bills"] == []


def test_single_bill_api(client):
    client.post(
        "/bills",
        data={
            "name": "Netflix",
            "amount": "649",
            "due_date": "2030-01-15",
            "category": "Subscription",
            "status": "Pending",
            "notes": "Monthly subscription",
        },
    )

    response = client.get("/api/bills")

    assert response.status_code == 200

    bills_data = response.get_json()["bills"]

    netflix_bill = next(
        bill
        for bill in bills_data
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


def test_update_bill_api(client):
    client.post(
        "/bills",
        data={
            "name": "Netflix",
            "amount": "649",
            "due_date": "2030-01-15",
            "category": "Subscription",
            "status": "Pending",
            "notes": "Monthly subscription",
        },
    )

    response = client.get("/api/bills")

    assert response.status_code == 200

    bill_id = response.get_json()["bills"][0]["id"]

    response = client.put(
        f"/api/bills/{bill_id}",
        json={
            "amount": 799,
            "status": "Paid",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["amount"] == 799.0
    assert data["status"] == "Paid"
    assert data["name"] == "Netflix"


def test_update_bill_api_not_found(client):
    response = client.put(
        "/api/bills/999",
        json={
            "amount": 500,
        },
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Bill not found."


def test_search_bills(client):
    client.post(
        "/bills",
        data={
            "name": "Netflix",
            "amount": "649",
            "due_date": "2026-12-15",
            "category": "Entertainment",
            "status": "Pending",
        },
        follow_redirects=True,
    )

    client.post(
        "/bills",
        data={
            "name": "Electricity",
            "amount": "1200",
            "due_date": "2026-12-20",
            "category": "Utilities",
            "status": "Pending",
        },
        follow_redirects=True,
    )

    response = client.get("/?search=Netflix")

    assert response.status_code == 200
    assert b"Netflix" in response.data
    assert b"Electricity" not in response.data


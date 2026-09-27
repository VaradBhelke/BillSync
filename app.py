import os
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

# In-memory store is intentional for this mini-project.
bills = []
next_id = 1

COMMIT = os.getenv(
    "RENDER_GIT_COMMIT",
    os.getenv("GIT_SHA", "local"),
)[:7]


def get_commit():
    return COMMIT


def calculate_summary():
    total = sum(
        float(bill["amount"])
        for bill in bills
        if bill["status"] != "Paid"
    )

    overdue = sum(
        1
        for bill in bills
        if bill["status"] == "Overdue"
    )

    return {
        "count": len(bills),
        "total_due": round(total, 2),
        "overdue": overdue,
    }


def validate_bill(form):
    name = form.get("name", "").strip()
    amount_raw = str(form.get("amount", "")).strip()
    due_date = form.get("due_date", "").strip()
    category = form.get("category", "Other").strip()
    status = form.get("status", "Pending").strip()
    notes = form.get("notes", "").strip()

    errors = []

    try:
        amount = float(amount_raw)

        if amount <= 0:
            errors.append("Amount must be greater than 0.")

    except ValueError:
        amount = 0
        errors.append("Amount must be a valid number.")

    if not name:
        errors.append("Bill name is required.")

    try:
        parsed_date = datetime.strptime(
            due_date,
            "%Y-%m-%d",
        )

        if parsed_date.date() < datetime.today().date():
            errors.append(
                "Due date cannot be in the past."
            )

    except ValueError:
        errors.append(
            "A valid due date is required."
        )

    allowed_categories = {
        "Subscription",
        "Utility",
        "Rent",
        "Insurance",
        "Loan/EMI",
        "Other",
    }

    allowed_statuses = {
        "Pending",
        "Paid",
        "Overdue",
    }

    if category not in allowed_categories:
        errors.append("Invalid category.")

    if status not in allowed_statuses:
        errors.append(
            "Invalid payment status."
        )

    return errors, {
        "name": name,
        "amount": round(amount, 2),
        "due_date": due_date,
        "category": category,
        "status": status,
        "notes": notes,
    }


@app.get("/")
def home():
    ordered = sorted(
        bills,
        key=lambda bill: bill["due_date"],
    )

    return render_template(
        "index.html",
        bills=ordered,
        summary=calculate_summary(),
        commit=get_commit(),
        error=None,
        form_data={},
    )


@app.post("/bills")
def add_bill():
    global next_id

    errors, data = validate_bill(
        request.form
    )

    if errors:
        ordered = sorted(
            bills,
            key=lambda bill: bill["due_date"],
        )

        return render_template(
            "index.html",
            bills=ordered,
            summary=calculate_summary(),
            commit=get_commit(),
            error=" ".join(errors),
            form_data=request.form,
        ), 400

    data["id"] = next_id
    next_id += 1

    bills.append(data)

    return redirect(
        url_for("home")
    )


@app.post("/bills/<int:bill_id>/delete")
def delete_bill(bill_id):
    global bills

    bills = [
        bill
        for bill in bills
        if bill["id"] != bill_id
    ]

    return redirect(
        url_for("home")
    )


@app.get("/api/bills")
def api_bills():
    return jsonify(
        {
            "bills": bills,
            "summary": calculate_summary(),
        }
    )


@app.get("/api/bills/<int:bill_id>")
def api_bill(bill_id):
    bill = next(
        (
            bill
            for bill in bills
            if bill["id"] == bill_id
        ),
        None,
    )

    if bill is None:
        return jsonify(
            {"error": "Bill not found."}
        ), 404

    return jsonify(bill)


@app.put("/api/bills/<int:bill_id>")
def update_bill_api(bill_id):
    bill = next(
        (
            bill
            for bill in bills
            if bill["id"] == bill_id
        ),
        None,
    )

    if bill is None:
        return jsonify(
            {"error": "Bill not found."}
        ), 404

    payload = request.get_json(
        silent=True
    )

    if not payload:
        return jsonify(
            {
                "error": (
                    "JSON request body is required."
                )
            }
        ), 400

    updated_data = {
        "name": payload.get(
            "name",
            bill["name"],
        ),
        "amount": payload.get(
            "amount",
            bill["amount"],
        ),
        "due_date": payload.get(
            "due_date",
            bill["due_date"],
        ),
        "category": payload.get(
            "category",
            bill["category"],
        ),
        "status": payload.get(
            "status",
            bill["status"],
        ),
        "notes": payload.get(
            "notes",
            bill["notes"],
        ),
    }

    errors, validated_data = validate_bill(
        updated_data
    )

    if errors:
        return jsonify(
            {"errors": errors}
        ), 400

    bill.update(validated_data)

    return jsonify(bill)


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "commit": get_commit(),
        }
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(
            os.getenv("PORT", "5000")
        ),
    )

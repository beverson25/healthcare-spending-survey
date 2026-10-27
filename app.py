"""
app.py
Author: Brittney Everson
Project: Healthcare Product Launch - Income & Spending Survey

Flask web app that collects participant data and stores it in MongoDB.

Run locally:  python app.py   -> http://127.0.0.1:5000
Run on AWS:   gunicorn --bind 127.0.0.1:8000 app:app  (see deploy/)
"""

import os

from flask import Flask, redirect, render_template, request, url_for

from db import get_collection
from user import CATEGORY_LABELS, EXPENSE_CATEGORIES, GENDER_OPTIONS, User

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")


def parse_form(form):
    """Turn the submitted form into a User object plus a list of errors."""
    errors = []

    try:
        age = int(form.get("age", ""))
    except ValueError:
        age = 0
        errors.append("Please enter your age as a whole number.")

    try:
        income = float(form.get("total_income", ""))
    except ValueError:
        income = 0
        errors.append("Please enter your total income as a number.")

    gender = form.get("gender", "")

    # Only checked categories count. A checked box needs an amount.
    expenses = {}
    checked = form.getlist("categories")
    for cat in EXPENSE_CATEGORIES:
        if cat in checked:
            raw = form.get(f"amount_{cat}", "").strip()
            if raw == "":
                errors.append(f"Enter an amount for {CATEGORY_LABELS[cat]} or uncheck it.")
                continue
            try:
                expenses[cat] = float(raw)
            except ValueError:
                errors.append(f"{CATEGORY_LABELS[cat]} amount must be a number.")
        else:
            expenses[cat] = 0

    user = User(age=age, gender=gender, total_income=income, expenses=expenses)
    if not errors:
        errors.extend(user.validate())
    return user, errors


@app.route("/", methods=["GET", "POST"])
def survey():
    errors = []
    if request.method == "POST":
        user, errors = parse_form(request.form)
        if not errors:
            get_collection().insert_one(user.to_document())
            return redirect(url_for("thank_you"))
    return render_template(
        "index.html",
        categories=EXPENSE_CATEGORIES,
        labels=CATEGORY_LABELS,
        genders=GENDER_OPTIONS,
        errors=errors,
        form=request.form,
    )


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


@app.route("/health")
def health():
    """Simple check used after deploying to AWS."""
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")

"""
tests/test_app.py
Author: Brittney Everson

Run with:  MONGO_URI=mongomock://localhost python -m pytest -q
Uses an in-memory fake MongoDB, so no database is needed.
"""

import csv
import os
import sys

os.environ["MONGO_URI"] = "mongomock://localhost"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from app import app  # noqa: E402
from db import get_collection  # noqa: E402
from export_to_csv import load_users, write_csv  # noqa: E402
from user import User  # noqa: E402


@pytest.fixture
def client():
    get_collection().delete_many({})
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_form_loads(client):
    page = client.get("/")
    assert page.status_code == 200
    for word in [b"Utilities", b"Entertainment", b"School Fees", b"Shopping", b"Healthcare"]:
        assert word in page.data


def test_valid_submission_is_saved(client):
    resp = client.post("/", data={
        "age": "34", "gender": "Female", "total_income": "5200",
        "categories": ["utilities", "healthcare"],
        "amount_utilities": "300", "amount_healthcare": "150",
        "amount_shopping": "999",  # not ticked, so it must be ignored
    })
    assert resp.status_code == 302
    doc = get_collection().find_one()
    assert doc["age"] == 34
    assert doc["expenses"]["utilities"] == 300
    assert doc["expenses"]["healthcare"] == 150
    assert doc["expenses"]["shopping"] == 0


def test_checked_box_without_amount_is_rejected(client):
    resp = client.post("/", data={
        "age": "40", "gender": "Male", "total_income": "4000",
        "categories": ["shopping"], "amount_shopping": "",
    })
    assert resp.status_code == 200
    assert b"Enter an amount for Shopping" in resp.data
    assert get_collection().count_documents({}) == 0


def test_bad_age_is_rejected(client):
    resp = client.post("/", data={"age": "12", "gender": "Male", "total_income": "100"})
    assert b"Age must be between 18 and 100" in resp.data


def test_export_loops_to_csv(client, tmp_path):
    for age in (25, 45):
        get_collection().insert_one(
            User(age, "Female", 3000, {"utilities": 200}).to_document())
    out = write_csv(load_users(get_collection()), tmp_path / "out.csv")
    rows = list(csv.DictReader(open(out)))
    assert len(rows) == 2
    assert rows[0]["utilities"] == "200.0"
    assert rows[0]["total_expenses"] == "200.0"

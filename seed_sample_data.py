"""
seed_sample_data.py
Author: Brittney Everson

OPTIONAL. Inserts realistic test participants into MongoDB so the
analysis has enough rows to chart before real responses come in.
Every record still goes through the User class and its validation.

Usage:
    python seed_sample_data.py            # adds 200 sample participants
    python seed_sample_data.py --n 50
    python seed_sample_data.py --clear    # deletes all participants first
"""

import argparse
import random
from datetime import datetime, timedelta, timezone

from db import get_collection
from user import EXPENSE_CATEGORIES, User

GENDER_WEIGHTS = {"Female": 0.48, "Male": 0.46, "Non-binary": 0.04, "Prefer not to say": 0.02}

# How likely each category is to be ticked, and its typical share of income.
CATEGORY_RULES = {
    "utilities":     (0.95, 0.08),
    "entertainment": (0.75, 0.05),
    "school_fees":   (0.35, 0.10),
    "shopping":      (0.90, 0.09),
    "healthcare":    (0.70, 0.06),
}


def income_for_age(age, rng):
    """Monthly income rises into the late 40s / 50s, then levels off."""
    peak = 9500
    curve = max(0.30, 1 - ((age - 50) / 32) ** 2)
    return round(max(1200, rng.gauss(peak * curve, 1500)), -1)


def make_user(rng):
    age = rng.randint(18, 75)
    gender = rng.choices(list(GENDER_WEIGHTS), weights=GENDER_WEIGHTS.values())[0]
    income = income_for_age(age, rng)
    expenses = {}
    for cat in EXPENSE_CATEGORIES:
        chance, share = CATEGORY_RULES[cat]
        if cat == "school_fees" and not 25 <= age <= 55:
            chance = 0.12  # fewer school-age dependants outside this range
        if cat == "healthcare" and age >= 55:
            share *= 1.6   # older participants spend more on health
        if gender == "Female" and cat == "healthcare":
            share *= 1.15
        if gender == "Male" and cat == "entertainment":
            share *= 1.2
        if rng.random() < chance:
            expenses[cat] = round(income * share * rng.uniform(0.6, 1.4), 2)
    submitted = datetime.now(timezone.utc) - timedelta(minutes=rng.randint(0, 60 * 24 * 14))
    return User(age=age, gender=gender, total_income=income,
                expenses=expenses, submitted_at=submitted)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    col = get_collection()
    if args.clear:
        col.delete_many({})
    rng = random.Random(args.seed)
    docs = []
    for _ in range(args.n):
        user = make_user(rng)
        assert not user.validate(), user.validate()
        docs.append(user.to_document())
    col.insert_many(docs)
    print(f"Inserted {len(docs)} sample participants. Total now: {col.count_documents({})}")


if __name__ == "__main__":
    main()

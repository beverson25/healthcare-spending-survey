"""
user.py
Author: Brittney Everson
Project: Healthcare Product Launch - Income & Spending Survey

Defines the User class. Every survey response moves through this class:
  - the Flask app builds a User from the web form and saves it to MongoDB
  - export_to_csv.py loads each MongoDB document back into a User
    and writes it to a CSV row
"""

from datetime import datetime, timezone

# The five expense categories required by the assignment.
EXPENSE_CATEGORIES = [
    "utilities",
    "entertainment",
    "school_fees",
    "shopping",
    "healthcare",
]

# Human-friendly labels for the form and charts.
CATEGORY_LABELS = {
    "utilities": "Utilities",
    "entertainment": "Entertainment",
    "school_fees": "School Fees",
    "shopping": "Shopping",
    "healthcare": "Healthcare",
}

GENDER_OPTIONS = ["Female", "Male", "Non-binary", "Prefer not to say"]


class User:
    """One survey participant: age, gender, total income and expenses."""

    def __init__(self, age, gender, total_income, expenses=None,
                 user_id=None, submitted_at=None):
        self.user_id = str(user_id) if user_id is not None else None
        self.age = int(age)
        self.gender = str(gender)
        self.total_income = round(float(total_income), 2)
        # Make sure every category exists; unchecked categories are 0.
        expenses = expenses or {}
        self.expenses = {
            cat: round(float(expenses.get(cat, 0) or 0), 2)
            for cat in EXPENSE_CATEGORIES
        }
        self.submitted_at = submitted_at or datetime.now(timezone.utc)

    # ---------- validation ----------
    def validate(self):
        """Return a list of error messages (empty list = valid)."""
        errors = []
        if not 18 <= self.age <= 100:
            errors.append("Age must be between 18 and 100.")
        if self.gender not in GENDER_OPTIONS:
            errors.append("Please choose a valid gender option.")
        if self.total_income < 0:
            errors.append("Total income cannot be negative.")
        for cat, amount in self.expenses.items():
            if amount < 0:
                errors.append(f"{CATEGORY_LABELS[cat]} amount cannot be negative.")
        return errors

    # ---------- derived values ----------
    @property
    def total_expenses(self):
        return round(sum(self.expenses.values()), 2)

    @property
    def spending_ratio(self):
        """Share of income spent across the five categories."""
        if self.total_income == 0:
            return 0.0
        return round(self.total_expenses / self.total_income, 4)

    # ---------- conversions ----------
    def to_document(self):
        """Dictionary shaped for MongoDB storage."""
        return {
            "age": self.age,
            "gender": self.gender,
            "total_income": self.total_income,
            "expenses": dict(self.expenses),
            "submitted_at": self.submitted_at,
        }

    @classmethod
    def from_document(cls, doc):
        """Build a User from a MongoDB document."""
        return cls(
            age=doc["age"],
            gender=doc["gender"],
            total_income=doc["total_income"],
            expenses=doc.get("expenses", {}),
            user_id=doc.get("_id"),
            submitted_at=doc.get("submitted_at"),
        )

    @staticmethod
    def csv_headers():
        return (["user_id", "age", "gender", "total_income"]
                + EXPENSE_CATEGORIES
                + ["total_expenses", "spending_ratio", "submitted_at"])

    def to_csv_row(self):
        """Flat dictionary, one key per CSV column."""
        row = {
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "total_income": self.total_income,
        }
        row.update(self.expenses)
        row["total_expenses"] = self.total_expenses
        row["spending_ratio"] = self.spending_ratio
        ts = self.submitted_at
        row["submitted_at"] = ts.isoformat() if hasattr(ts, "isoformat") else ts
        return row

    def __repr__(self):
        return (f"User(age={self.age}, gender='{self.gender}', "
                f"income={self.total_income}, expenses={self.total_expenses})")

"""
export_to_csv.py
Author: Brittney Everson

Loops through every participant in MongoDB, turns each document
into a User object, and writes the result to a CSV file.

Usage:
    python export_to_csv.py                      # writes data/survey_data.csv
    python export_to_csv.py --out my_file.csv
"""

import argparse
import csv
import os

from db import get_collection
from user import User

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "data", "survey_data.csv")


def load_users(collection):
    """Loop through the collection and build a list of User objects."""
    users = []
    for doc in collection.find().sort("submitted_at", 1):
        users.append(User.from_document(doc))
    return users


def write_csv(users, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=User.csv_headers())
        writer.writeheader()
        for user in users:
            writer.writerow(user.to_csv_row())
    return path


def main():
    parser = argparse.ArgumentParser(description="Export survey data to CSV")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output CSV path")
    args = parser.parse_args()

    users = load_users(get_collection())
    write_csv(users, args.out)
    print(f"Exported {len(users)} participants to {args.out}")


if __name__ == "__main__":
    main()

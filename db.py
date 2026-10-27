"""
db.py
Author: Brittney Everson

One place to connect to MongoDB. Settings come from environment
variables (or a .env file), so no passwords live in the code.

MONGO_URI examples
  Local MongoDB:   mongodb://localhost:27017
  MongoDB Atlas:   mongodb+srv://<user>:<password>@<cluster>.mongodb.net
  Testing only:    mongomock://localhost   (in-memory fake database)
"""

import os

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "healthcare_survey")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "participants")

_client = None


def get_client():
    global _client
    if _client is None:
        if MONGO_URI.startswith("mongomock://"):
            import mongomock  # only needed for tests / offline demo
            _client = mongomock.MongoClient()
        else:
            from pymongo import MongoClient
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_collection():
    return get_client()[DB_NAME][COLLECTION_NAME]

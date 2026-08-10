"""
db/mongo.py — Connessione condivisa a MongoDB.

Funziona sia dentro Docker Compose (MONGO_URI=mongodb://mongo:27017/)
sia in locale (MONGO_URI=mongodb://localhost:27017/ oppure non impostata).
"""

import os
import uuid
from pymongo import MongoClient


_app_name  = f"myapp-{uuid.uuid4().hex[:8]}"
_mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")


if "?" in _mongo_uri:
    _uri = f"{_mongo_uri}&appName={_app_name}"
else:
    _uri = f"{_mongo_uri}?appName={_app_name}"

client = MongoClient(_uri)
db     = client["myapp"]

users      = db["users"]
images     = db["images"]
nuovi_dati = db["nuovi_dati"]

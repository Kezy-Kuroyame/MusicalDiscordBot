import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_DIR = os.path.join(BASE_DIR, "secrets")

with open(os.path.join(SECRETS_DIR, "config.json"), encoding="utf-8") as f:
    data = json.load(f)

TOKEN = data["token"]
PREFIX = data.get("prefix", "!")
DATABASE_URL = data.get("database_url", "sqlite:///db.sqlite3")
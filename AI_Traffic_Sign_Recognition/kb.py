"""Knowledge-base access layer: MongoDB first, JSON file fallback."""
import json
import os

import config


def _mongo_db():
    try:
        from pymongo import MongoClient
        client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=1500)
        client.admin.command("ping")
        return client[config.DB_NAME]
    except Exception:
        return None


class KnowledgeBase:
    def __init__(self):
        self.backend = "JSON file (MongoDB not available)"
        signs, rules = None, None
        db = _mongo_db()
        if db is not None and db.signs.count_documents({}) > 0:
            signs = list(db.signs.find({}, {"_id": 0}))
            rules = list(db.rules.find({}, {"_id": 0}))
            self.backend = "MongoDB"
        if not signs:
            with open(os.path.join(config.DATA_DIR, "knowledge_base.json"), encoding="utf-8") as f:
                signs = json.load(f)
            with open(os.path.join(config.DATA_DIR, "rules.json"), encoding="utf-8") as f:
                rules = json.load(f)
        self.signs = {s["sign_id"]: s for s in signs}
        self.rules = rules

    def get(self, sign_id):
        return self.signs.get(sign_id)

    def categories(self):
        seen = []
        for s in self.signs.values():
            if s["category"] not in seen:
                seen.append(s["category"])
        return seen

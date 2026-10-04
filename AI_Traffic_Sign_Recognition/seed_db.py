"""
seed_db.py - store the knowledge base and IF-THEN rules
Run:  python seed_db.py
Writes data/knowledge_base.json + data/rules.json and, if MongoDB is
running, the collections  traffic_sign_db.signs  and  traffic_sign_db.rules.
"""
import json
import os

import config
import knowledge_base_data as kbd


def main():
    signs = kbd.build_signs()
    rules = kbd.build_rules(signs)
    os.makedirs(config.DATA_DIR, exist_ok=True)
    for name, data in (("knowledge_base.json", signs), ("rules.json", rules)):
        with open(os.path.join(config.DATA_DIR, name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"JSON files written: {len(signs)} signs, {len(rules)} rules")

    try:
        from pymongo import MongoClient
        client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        db = client[config.DB_NAME]
        db.signs.delete_many({}); db.rules.delete_many({})
        db.signs.insert_many([dict(s) for s in signs])
        db.rules.insert_many([dict(r) for r in rules])
        db.signs.create_index("sign_id", unique=True)
        print(f"MongoDB '{config.DB_NAME}' seeded: {db.signs.count_documents({})} signs, "
              f"{db.rules.count_documents({})} rules")
    except Exception as e:
        print("MongoDB not available (", type(e).__name__, ") - JSON fallback will be used.")


if __name__ == "__main__":
    main()

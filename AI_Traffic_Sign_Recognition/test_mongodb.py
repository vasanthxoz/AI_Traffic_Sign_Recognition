"""Checks the MongoDB connection and the stored knowledge base.  Run: python test_mongodb.py"""
import config

try:
    from pymongo import MongoClient
except ImportError:
    raise SystemExit("pymongo is not installed:  pip install pymongo")

try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command("ping")
except Exception as e:
    raise SystemExit(f"Cannot connect to MongoDB at {config.MONGO_URI}: {e}\n"
                     "Start MongoDB (mongod) and run:  python seed_db.py")

db = client[config.DB_NAME]
print("Connected to MongoDB")
print("signs :", db.signs.count_documents({}))
print("rules :", db.rules.count_documents({}))
s = db.signs.find_one({"sign_id": "stop"}, {"_id": 0})
print("sample record ->", s["name"], "|", s["category"], "|", s["instruction"] if s else "run seed_db.py first")

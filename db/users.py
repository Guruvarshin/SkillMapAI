import bcrypt
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from db.mongo import get_db


def register(name: str, email: str, password: str) -> dict:
    db = get_db()
    name = name.strip()
    email = email.strip().lower()
    password = password.strip()
    if not name:
        return "Name cannot be empty."
    if not email or "@" not in email:
        return "Please enter a valid email address."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user_doc = {
        "name": name,
        "email": email,
        "password_hash": password_hash.decode("utf-8"),
        "created_at": datetime.now(timezone.utc),
        "roadmap_ids": [],
    }
    try:
        result = db.users.insert_one(user_doc)
        return {
            "_id": str(result.inserted_id),
            "name": name,
            "email": email,
            "created_at": user_doc["created_at"],
            "roadmap_ids": [],
        }
    except DuplicateKeyError:
        return f"An account with email '{email}' already exists. Please log in."


def login(email: str, password: str) -> dict | None:
    db = get_db()
    email = email.strip().lower()
    user = db.users.find_one({"email": email})
    if not user:
        return None
    password_matches = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8"),
    )
    if not password_matches:
        return None
    return _clean_user(user)


def get_user_by_id(user_id: str) -> dict | None:
    db = get_db()
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    user = db.users.find_one({"_id": oid})
    if not user:
        return None
    return _clean_user(user)


def _clean_user(user: dict) -> dict:
    return {
        "_id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "created_at": user.get("created_at"),
        "roadmap_ids": [str(rid) for rid in user.get("roadmap_ids", [])],
    }

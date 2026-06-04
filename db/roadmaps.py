from datetime import datetime, timezone
from bson import ObjectId
from pymongo import DESCENDING
from db.mongo import get_db
def save_roadmap(user_id: str, skill: str, level: str) -> str:
    db = get_db()
    roadmap_doc = {
        "user_id": user_id,                                                       
        "skill": skill.strip(),
        "level": level,
        "status": "generating",                                                 
        "created_at": datetime.now(timezone.utc),
        "timeline": None,
        "budget": None,
        "major_project": None,
        "final_quiz": None,
        "topics": None,
    }
    result = db.roadmaps.insert_one(roadmap_doc)
    roadmap_id = str(result.inserted_id)
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"roadmap_ids": roadmap_id}},
    )
    return roadmap_id
def update_roadmap(roadmap_id: str, data: dict) -> bool:
    db = get_db()
    result = db.roadmaps.update_one(
        {"_id": ObjectId(roadmap_id)},
        {
            "$set": {
                "status": "done",
                "completed_at": datetime.now(timezone.utc),
                "topics": data.get("topics"),
                "timeline": data.get("timeline"),
                "budget": data.get("budget"),
                "major_project": data.get("major_project"),
                "final_quiz": data.get("final_quiz"),
            }
        },
    )
    return result.modified_count > 0
def update_status(roadmap_id: str, status: str, error_message: str = None) -> None:
    db = get_db()
    fields = {"status": status}
    if error_message:
        fields["error_message"] = error_message
    db.roadmaps.update_one(
        {"_id": ObjectId(roadmap_id)},
        {"$set": fields},
    )
def get_roadmap(roadmap_id: str) -> dict | None:
    db = get_db()
    try:
        oid = ObjectId(roadmap_id)
    except Exception:
        return None
    doc = db.roadmaps.find_one({"_id": oid})
    if not doc:
        return None
    return _clean_roadmap(doc)
def list_user_roadmaps(user_id: str) -> list[dict]:
    db = get_db()
    cursor = db.roadmaps.find(
        {"user_id": user_id},
        {
            "skill": 1,
            "level": 1,
            "status": 1,
            "created_at": 1,
            "completed_at": 1,
            "error_message": 1,
        },
    ).sort("created_at", DESCENDING)                          
    return [_clean_roadmap(doc) for doc in cursor]
def delete_roadmap(roadmap_id: str, user_id: str) -> bool:
    db = get_db()
    try:
        oid = ObjectId(roadmap_id)
    except Exception:
        return False
    result = db.roadmaps.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return False                        
    db.progress.delete_one({"roadmap_id": roadmap_id})
    db.quizzes.delete_many({"roadmap_id": roadmap_id})
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"roadmap_ids": roadmap_id}},
    )
    return True
def _clean_roadmap(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc

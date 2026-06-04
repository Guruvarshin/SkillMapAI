from datetime import datetime, timezone
from db.mongo import get_db
def get_progress(user_id: str, roadmap_id: str) -> dict:
    db = get_db()
    doc = db.progress.find_one({
        "user_id": user_id,
        "roadmap_id": roadmap_id,
    })
    if doc:
        doc["_id"] = str(doc["_id"])
        return doc
    return _empty_progress(user_id, roadmap_id)
def mark_subtopic_done(
    user_id: str,
    roadmap_id: str,
    subtopic_id: str,
    total_subtopics: int,
) -> float:
    db = get_db()
    db.progress.update_one(
        {"user_id": user_id, "roadmap_id": roadmap_id},
        {
            "$addToSet": {"completed_subtopics": subtopic_id},
            "$set": {"last_updated": datetime.now(timezone.utc)},
            "$setOnInsert": {
                "quiz_scores": {},
                "final_quiz_score": None,
                "overall_pct": 0.0,
            },
        },
        upsert=True,                                       
    )
    doc = db.progress.find_one(
        {"user_id": user_id, "roadmap_id": roadmap_id},
        {"completed_subtopics": 1},
    )
    completed_count = len(doc.get("completed_subtopics", []))
    new_pct = round(completed_count / total_subtopics, 4) if total_subtopics > 0 else 0.0
    db.progress.update_one(
        {"user_id": user_id, "roadmap_id": roadmap_id},
        {"$set": {"overall_pct": new_pct}},
    )
    return new_pct
def mark_subtopic_undone(
    user_id: str,
    roadmap_id: str,
    subtopic_id: str,
    total_subtopics: int,
) -> float:
    db = get_db()
    db.progress.update_one(
        {"user_id": user_id, "roadmap_id": roadmap_id},
        {
            "$pull": {"completed_subtopics": subtopic_id},
            "$set": {"last_updated": datetime.now(timezone.utc)},
        },
    )
    doc = db.progress.find_one(
        {"user_id": user_id, "roadmap_id": roadmap_id},
        {"completed_subtopics": 1},
    )
    if not doc:
        return 0.0
    completed_count = len(doc.get("completed_subtopics", []))
    new_pct = round(completed_count / total_subtopics, 4) if total_subtopics > 0 else 0.0
    db.progress.update_one(
        {"user_id": user_id, "roadmap_id": roadmap_id},
        {"$set": {"overall_pct": new_pct}},
    )
    return new_pct
def save_quiz_score(
    user_id: str,
    roadmap_id: str,
    subtopic_id: str,
    score: int,
    total: int,
) -> None:
    db = get_db()
    passed = (score / total) >= 0.7 if total > 0 else False
    db.progress.update_one(
        {"user_id": user_id, "roadmap_id": roadmap_id},
        {
            "$set": {
                f"quiz_scores.{subtopic_id}": {
                    "score": score,
                    "total": total,
                    "passed": passed,
                },
                "last_updated": datetime.now(timezone.utc),
            },
            "$setOnInsert": {
                "completed_subtopics": [],
                "final_quiz_score": None,
                "overall_pct": 0.0,
            },
        },
        upsert=True,
    )
def save_final_quiz_score(
    user_id: str,
    roadmap_id: str,
    score: int,
    total: int,
) -> None:
    db = get_db()
    db.progress.update_one(
        {"user_id": user_id, "roadmap_id": roadmap_id},
        {
            "$set": {
                "final_quiz_score": score,
                "final_quiz_total": total,
                "final_quiz_passed": (score / total) >= 0.7 if total > 0 else False,
                "last_updated": datetime.now(timezone.utc),
            },
            "$setOnInsert": {
                "completed_subtopics": [],
                "quiz_scores": {},
                "overall_pct": 0.0,
            },
        },
        upsert=True,
    )
def _empty_progress(user_id: str, roadmap_id: str) -> dict:
    return {
        "_id": None,
        "user_id": user_id,
        "roadmap_id": roadmap_id,
        "completed_subtopics": [],
        "quiz_scores": {},
        "final_quiz_score": None,
        "final_quiz_total": None,
        "final_quiz_passed": None,
        "overall_pct": 0.0,
        "last_updated": None,
    }
def count_total_subtopics(roadmap: dict) -> int:
    topics = roadmap.get("topics") or []
    return sum(len(t.get("subtopics", [])) for t in topics)

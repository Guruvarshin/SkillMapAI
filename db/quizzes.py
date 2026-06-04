\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\

from db.mongo import get_db

def save_quizzes(roadmap_id: str, quizzes_data: dict) -> None:
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\

    db = get_db()

    db.quizzes.delete_many({"roadmap_id": roadmap_id})

    docs = []

    for subtopic_id, questions in quizzes_data.get("subtopics", {}).items():
        docs.append({
            "roadmap_id": roadmap_id,
            "subtopic_id": subtopic_id,
            "type": "subtopic",
            "questions": questions,
        })

    final_questions = quizzes_data.get("final", [])
    if final_questions:
        docs.append({
            "roadmap_id": roadmap_id,
            "subtopic_id": "final",
            "type": "final",
            "questions": final_questions,
        })

    if docs:
        db.quizzes.insert_many(docs)

def save_single_quiz(
    roadmap_id: str,
    subtopic_id: str,
    questions: list,
    quiz_type: str = "subtopic",
) -> None:
\
\
\
\
\
\
\
\
\
\
\

    db = get_db()

    db.quizzes.replace_one(
        {"roadmap_id": roadmap_id, "subtopic_id": subtopic_id},
        {
            "roadmap_id": roadmap_id,
            "subtopic_id": subtopic_id,
            "type": quiz_type,
            "questions": questions,
        },
        upsert=True,
    )

def get_quiz(roadmap_id: str, subtopic_id: str) -> list:
\
\
\
\
\
\
\
\
\
\
\
\

    db = get_db()

    doc = db.quizzes.find_one(
        {"roadmap_id": roadmap_id, "subtopic_id": subtopic_id},
        {"questions": 1, "_id": 0},
    )

    return doc.get("questions", []) if doc else []

def get_final_quiz(roadmap_id: str) -> list:
\
\
\
\
\
\
\
\

    return get_quiz(roadmap_id, "final")

def get_all_quizzes(roadmap_id: str) -> dict:
\
\
\
\
\
\
\
\

    db = get_db()

    cursor = db.quizzes.find(
        {"roadmap_id": roadmap_id},
        {"subtopic_id": 1, "questions": 1, "_id": 0},
    )

    return {doc["subtopic_id"]: doc["questions"] for doc in cursor}

def delete_quizzes(roadmap_id: str) -> None:
\
\
\
\

    db = get_db()
    db.quizzes.delete_many({"roadmap_id": roadmap_id})

def ensure_quiz_indexes() -> None:
\
\
\
\

    db = get_db()
    db.quizzes.create_index(
        [("roadmap_id", 1), ("subtopic_id", 1)],
        unique=True,
    )

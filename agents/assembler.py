import math
from pydantic import ValidationError
from utils.validators import RoadmapOutput
from utils.helpers import slugify
from db.roadmaps import update_roadmap, update_status
from db.quizzes import save_quizzes
def run_assembler(state) -> dict:
    try:
        hours_map = _build_hours_map(
            state.topic_tree,
            state.timeline_budget_data.get("timeline", {}),
        )
        topics = _merge_topics(
            topic_tree=state.topic_tree,
            videos_data=state.videos_data,
            courses_data=state.courses_data,
            projects_data=state.projects_data,
            hours_map=hours_map,
        )
        timeline = state.timeline_budget_data.get("timeline", {})
        budget = state.timeline_budget_data.get("budget", {})
        major_project = state.projects_data.get("major_project", {})
        try:
            roadmap_output = RoadmapOutput(
                topics=topics,
                timeline=timeline,
                budget=budget,
                major_project=major_project,
            )
            final_dict = roadmap_output.to_mongo_dict()
        except ValidationError as e:
            print(f"[Assembler] Pydantic validation errors: {e}")
            final_dict = {
                "topics": topics,
                "timeline": timeline or {},
                "budget": budget or {},
                "major_project": major_project or {},
            }
        updated = update_roadmap(state.roadmap_id, final_dict)
        if not updated:
            raise RuntimeError(
                f"update_roadmap() returned False for id={state.roadmap_id}. "
                "Document may not exist."
            )
        if state.quiz_data:
            save_quizzes(state.roadmap_id, state.quiz_data)
        return final_dict
    except Exception as e:
        try:
            update_status(state.roadmap_id, "failed", str(e))
        except Exception:
            pass                                               
        raise RuntimeError(f"Assembler failed: {e}") from e
def _build_hours_map(topic_tree: dict, timeline: dict) -> dict:
    hours_map = {}
    per_topic = {
        entry["topic"]: entry.get("hours", 0)
        for entry in timeline.get("per_topic", [])
    }
    for topic in topic_tree.get("topics", []):
        topic_name = topic.get("name", "")
        subtopics = topic.get("subtopics", [])
        subtopic_count = len(subtopics)
        if subtopic_count == 0:
            continue
        topic_hours = per_topic.get(topic_name, subtopic_count * 4)
        hours_per_sub = max(1, math.ceil(topic_hours / subtopic_count))
        for sub in subtopics:
            sub_id = sub.get("id", "")
            if sub_id:
                hours_map[sub_id] = hours_per_sub
    return hours_map
def _merge_topics(
    topic_tree: dict,
    videos_data: dict,
    courses_data: dict,
    projects_data: dict,
    hours_map: dict,
) -> list:
    sub_projects = projects_data.get("subtopics", {})
    merged_topics = []
    for topic in topic_tree.get("topics", []):
        merged_subtopics = []
        for sub in topic.get("subtopics", []):
            sub_id = sub.get("id", slugify(sub.get("name", "topic")))
            vid = videos_data.get(sub_id, {})
            course = courses_data.get(sub_id, {})
            proj = sub_projects.get(sub_id, {})
            hours = hours_map.get(sub_id, 4)
            videos = []
            if vid.get("video", {}).get("url"):
                videos.append(vid["video"])
            if vid.get("playlist", {}).get("url"):
                videos.append(vid["playlist"])
            merged_subtopic = {
                "id": sub_id,
                "name": sub.get("name", ""),
                "description": sub.get("description", ""),
                "hours_estimate": hours,
                "videos": videos,
                "text_resource": course.get("text_resource", _fallback_text(sub.get("name", ""), "")),
                "free_course": course.get("free_course", _fallback_free_course(sub.get("name", ""))),
                "paid_course": course.get("paid_course", _fallback_paid_course(sub.get("name", ""))),
                "mini_project": proj.get("mini_project", _fallback_mini_project(sub.get("name", ""))),
                "capstone_project": proj.get("capstone_project", _fallback_capstone(sub.get("name", ""), topic.get("name", ""))),
            }
            merged_subtopics.append(merged_subtopic)
        merged_topics.append({
            "name": topic.get("name", ""),
            "subtopics": merged_subtopics,
        })
    return merged_topics
def _fallback_text(sub_name: str, skill: str) -> dict:
    import urllib.parse
    q = urllib.parse.quote_plus(f"{skill} {sub_name} tutorial documentation".strip())
    return {
        "title": f"Search: {sub_name} documentation",
        "url": f"https://www.google.com/search?q={q}",
        "type": "article",
    }
def _fallback_free_course(sub_name: str) -> dict:
    import urllib.parse
    q = urllib.parse.quote_plus(sub_name)
    return {
        "name": f"freeCodeCamp: {sub_name}",
        "platform": "freeCodeCamp",
        "url": f"https://www.freecodecamp.org/search?query={q}",
        "certificate": False,
    }
def _fallback_paid_course(sub_name: str) -> dict:
    import urllib.parse
    q = urllib.parse.quote_plus(sub_name)
    return {
        "name": f"Udemy: {sub_name}",
        "platform": "Udemy",
        "url": f"https://www.udemy.com/courses/search/?q={q}",
        "price": "~$15",
        "rating": "",
    }
def _fallback_mini_project(sub_name: str) -> dict:
    return {
        "title": f"Practice: {sub_name}",
        "use_case": f"Apply {sub_name} concepts in a small real-world scenario.",
        "tutorial_video_url": "",
    }
def _fallback_capstone(sub_name: str, topic_name: str) -> dict:
    return {
        "title": f"{topic_name} Capstone",
        "description": f"Build a project combining {sub_name} with other {topic_name} skills.",
        "use_case": f"Consolidate {topic_name} knowledge",
    }

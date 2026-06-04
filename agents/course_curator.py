import json
import urllib.parse
from utils.helpers import slugify
from tools.tavily_tool import TavilyTool


def run_course_curator(topic_tree: dict, skill: str) -> dict:
    tool = TavilyTool()
    results = {}
    for topic in topic_tree.get("topics", []):
        for subtopic in topic.get("subtopics", []):
            sub_id = subtopic.get("id", slugify(subtopic.get("name", "topic")))
            sub_name = subtopic.get("name", "")
            try:
                raw = tool._run(
                    query=f"{skill} {sub_name} tutorial documentation guide",
                    search_type="resource",
                )
                text_resource = json.loads(raw)
            except Exception:
                text_resource = _fallback_text(sub_name, skill)
            try:
                raw = tool._run(
                    query=f"{skill} {sub_name} free course certificate",
                    search_type="free_course",
                )
                free_course = json.loads(raw)
            except Exception:
                free_course = _fallback_free_course(sub_name)
            try:
                raw = tool._run(
                    query=f"{skill} {sub_name} course Udemy",
                    search_type="paid_course",
                )
                paid_course = json.loads(raw)
            except Exception:
                paid_course = _fallback_paid_course(sub_name, skill)
            results[sub_id] = {
                "text_resource": text_resource,
                "free_course": free_course,
                "paid_course": paid_course,
            }
    return results


def _fallback_text(sub_name: str, skill: str) -> dict:
    q = urllib.parse.quote_plus(f"{skill} {sub_name} tutorial documentation")
    return {
        "title": f"Search: {sub_name} documentation",
        "url": f"https://www.google.com/search?q={q}",
        "type": "article",
        "source": "google_fallback",
    }


def _fallback_free_course(sub_name: str) -> dict:
    q = urllib.parse.quote_plus(sub_name)
    return {
        "name": f"freeCodeCamp: {sub_name}",
        "platform": "freeCodeCamp",
        "url": f"https://www.freecodecamp.org/search?query={q}",
        "certificate": False,
        "source": "fcc_fallback",
    }


def _fallback_paid_course(sub_name: str, skill: str) -> dict:
    q = urllib.parse.quote_plus(f"{skill} {sub_name}")
    return {
        "name": f"Udemy: {skill} {sub_name}",
        "platform": "Udemy",
        "url": f"https://www.udemy.com/courses/search/?q={q}",
        "price": "~$15",
        "rating": "",
        "source": "udemy_fallback",
    }


def build_course_fallbacks(topic_tree: dict, skill: str) -> dict:
    fallbacks = {}
    for topic in topic_tree.get("topics", []):
        for sub in topic.get("subtopics", []):
            sub_id = sub.get("id", slugify(sub.get("name", "topic")))
            sub_name = sub.get("name", "")
            fallbacks[sub_id] = {
                "text_resource": _fallback_text(sub_name, skill),
                "free_course": _fallback_free_course(sub_name),
                "paid_course": _fallback_paid_course(sub_name, skill),
            }
    return fallbacks

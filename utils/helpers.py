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

import re
import os
import yaml
from pathlib import Path
from datetime import datetime, timezone

_CONFIG_DIR = Path(__file__).parent.parent / "agents" / "config"

def load_agent_config(agent_name: str) -> dict:
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

    with open(_CONFIG_DIR / "agents.yaml", encoding="utf-8") as f:
        all_agents = yaml.safe_load(f)
    if agent_name not in all_agents:
        raise KeyError(f"Agent '{agent_name}' not found in agents.yaml")
    return all_agents[agent_name]

def load_task_config(task_name: str) -> dict:
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

    with open(_CONFIG_DIR / "tasks.yaml", encoding="utf-8") as f:
        all_tasks = yaml.safe_load(f)
    if task_name not in all_tasks:
        raise KeyError(f"Task '{task_name}' not found in tasks.yaml")
    return all_tasks[task_name]

def get_mechanical_llm():
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

    from crewai import LLM

    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    if groq_key and groq_key != "your_groq_api_key_here":
        return LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=groq_key,
            temperature=0.1,
        )

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    haiku_model = os.environ.get("HAIKU_MODEL", "anthropic/claude-haiku-4-5")

    return LLM(
        model=haiku_model,
        api_key=anthropic_key,
        temperature=0.1,
    )

def get_reasoning_llm():
\
\
\
\
\
\
\
\

    from crewai import LLM

    sonnet_model = os.environ.get("SONNET_MODEL", "anthropic/claude-sonnet-4-5")

    return LLM(
        model=sonnet_model,
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        temperature=0.3,
    )

def extract_crew_result(result) -> dict | list | None:
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

    import json as _json

    if result.pydantic is not None:
        try:
            return result.pydantic.model_dump()
        except Exception:
            pass

    raw = getattr(result, "raw", None) or str(result)
    if raw:
        try:
            cleaned = extract_json(raw)
            return _json.loads(cleaned)
        except (_json.JSONDecodeError, ValueError):
            pass

    return None

def slugify(text: str) -> str:
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

    if not text:
        return "untitled"

    slug = text.lower().strip()

    slug = slug.replace("&", " and ").replace("+", " and ")

    slug = re.sub(r"[^a-z0-9\s-]", "", slug)

    slug = re.sub(r"\s+", "-", slug)

    slug = re.sub(r"-+", "-", slug)

    slug = slug.strip("-")

    return slug or "untitled"

def format_hours(hours: int | float) -> str:
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

    if not hours or hours <= 0:
        return "< 1 hour"
    if hours == 1:
        return "1 hour"

    if isinstance(hours, float) and hours != int(hours):
        return f"{hours} hours"
    return f"{int(hours)} hours"

def format_weeks(weeks: int) -> str:
\
\
\
\
\
\

    if not weeks or weeks <= 0:
        return "Unknown duration"
    return f"{weeks} week" if weeks == 1 else f"{weeks} weeks"

def format_date(dt: datetime | None) -> str:
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

    if not dt:
        return "Unknown date"
    return dt.strftime("%b %d, %Y")

def time_ago(dt: datetime | None) -> str:
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

    if not dt:
        return "Unknown"

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        m = seconds // 60
        return f"{m} minute ago" if m == 1 else f"{m} minutes ago"
    elif seconds < 86400:
        h = seconds // 3600
        return f"{h} hour ago" if h == 1 else f"{h} hours ago"
    elif seconds < 2592000:            
        d = seconds // 86400
        return f"{d} day ago" if d == 1 else f"{d} days ago"
    elif seconds < 31536000:            
        mo = seconds // 2592000
        return f"{mo} month ago" if mo == 1 else f"{mo} months ago"
    else:
        y = seconds // 31536000
        return f"{y} year ago" if y == 1 else f"{y} years ago"

def truncate_text(text: str, max_len: int = 120) -> str:
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

    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."

def format_level(level: str) -> str:
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

    mapping = {
        "beginner": "🟢 Beginner",
        "intermediate": "🟡 Intermediate",
        "advanced": "🔴 Advanced",
    }
    return mapping.get(level.lower(), level.capitalize())

def format_status(status: str) -> str:
\
\
\
\
\
\
\

    mapping = {
        "generating": "⏳ Generating...",
        "done": "✅ Ready",
        "failed": "❌ Failed",
    }
    return mapping.get(status, status)

def format_price(price_str: str) -> str:
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

    if not price_str:
        return "Price unavailable"

    price_str = price_str.strip()

    if price_str.lower() in ("free", "$0", "0", "0.00", "$0.00", "no cost"):
        return "Free"

    match = re.search(r"(\d+(?:\.\d+)?)", price_str)
    if match:
        amount = float(match.group(1))

        if amount == int(amount):
            return f"${int(amount)}"
        return f"${amount:.2f}"

    return price_str                                     

def extract_json(text: str) -> str:
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

    if not text:
        return "{}"

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json|python)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()

    start = -1
    open_char, close_char = "{", "}"
    for i, ch in enumerate(text):
        if ch == "{":
            start = i
            open_char, close_char = "{", "}"
            break
        elif ch == "[":
            start = i
            open_char, close_char = "[", "]"
            break

    if start == -1:
        return "{}"

    depth = 0
    in_string = False
    escape_next = False

    for i in range(start, len(text)):
        ch = text[i]

        if escape_next:
            escape_next = False
            continue

        if ch == "\\" and in_string:
            escape_next = True
            continue

        if ch == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:

                return text[start: i + 1].strip()

    return text[start:].strip()

def get_all_subtopic_ids(roadmap: dict) -> list[str]:
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

    ids = []
    for topic in roadmap.get("topics") or []:
        for subtopic in topic.get("subtopics") or []:
            if subtopic.get("id"):
                ids.append(subtopic["id"])
    return ids

def pct_to_display(pct: float) -> str:
\
\
\
\
\
\
\

    return f"{int(round(pct * 100))}%"

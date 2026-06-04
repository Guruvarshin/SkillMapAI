import json
from crewai import Agent, Task, Crew, Process
from utils.helpers import (
    load_agent_config,
    load_task_config,
    get_reasoning_llm,
    get_mechanical_llm,
    extract_json,
    extract_crew_result,
    slugify,
)
def _build_mini_capstone_agent() -> Agent:
    cfg = load_agent_config("project_designer")
    return Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        llm=get_mechanical_llm(),                           
        verbose=False,
        allow_delegation=False,
    )
def _build_major_project_agent() -> Agent:
    cfg = load_agent_config("project_designer")
    return Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        llm=get_reasoning_llm(),                               
        verbose=False,
        allow_delegation=False,
    )
def run_project_designer(topic_tree: dict, skill: str, level: str) -> dict:
    topics = topic_tree.get("topics", [])
    all_subtopic_projects = {}
    mini_agent = _build_mini_capstone_agent()
    for topic in topics:
        topic_name = topic.get("name", "Topic")
        subtopics = topic.get("subtopics", [])
        if not subtopics:
            continue
        try:
            batch = _run_mini_capstone_for_topic(mini_agent, topic, skill, level)
            if batch:
                normalised = {
                    slugify(k) if not k.replace("-", "").isalnum() else k: v
                    for k, v in batch.items()
                }
                all_subtopic_projects.update(normalised)
            else:
                for sub in subtopics:
                    sub_id = sub.get("id", slugify(sub.get("name", "topic")))
                    all_subtopic_projects[sub_id] = _fallback_subtopic_projects(
                        sub.get("name", ""), topic_name
                    )
        except Exception as e:
            print(f"[ProjectDesigner] Topic '{topic_name}' failed: {e}")
            for sub in subtopics:
                sub_id = sub.get("id", slugify(sub.get("name", "topic")))
                all_subtopic_projects[sub_id] = _fallback_subtopic_projects(
                    sub.get("name", ""), topic_name
                )
    major_project = _run_major_project(topic_tree, skill, level)
    return {
        "subtopics": all_subtopic_projects,
        "major_project": major_project,
    }
def _run_mini_capstone_for_topic(
    agent: Agent,
    topic: dict,
    skill: str,
    level: str,
) -> dict | None:
    topic_name = topic.get("name", "")
    subtopics = topic.get("subtopics", [])
    subtopic_list = "\n".join(
        f"- ID: {s.get('id', slugify(s.get('name', '')))} | Name: {s.get('name', '')} | Desc: {s.get('description', '')}"
        for s in subtopics
    )
    description = f"""Design projects for the topic "{topic_name}" in the skill "{skill}" ({level} level).
Subtopics to design projects for:
{subtopic_list}
For EACH subtopic above, design:
1. mini_project: A small project (1-3 hours) that specifically practices that subtopic.
   - Must be real-world motivated (not a toy example)
   - title: 3-5 words
   - use_case: 1 sentence explaining the real-world value
2. capstone_project: A half-day project linking this subtopic with others in "{topic_name}".
   - title: 3-5 words
   - description: 2 sentences
   - use_case: 1 sentence
Return ONLY valid JSON. No markdown. No explanation. No code fences.
Return format:
{{
  "subtopic-id": {{
    "mini_project": {{"title": "...", "use_case": "...", "tutorial_video_url": ""}},
    "capstone_project": {{"title": "...", "description": "...", "use_case": "..."}}
  }}
}}
Use the exact subtopic IDs shown above as keys."""
    task = Task(
        description=description,
        expected_output="Valid JSON object keyed by subtopic ID with mini_project and capstone_project for each.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    parsed = extract_crew_result(result)
    if not parsed or not isinstance(parsed, dict):
        return None
    clean = {}
    for sub_id, proj_data in parsed.items():
        if not isinstance(proj_data, dict):
            continue
        clean[sub_id] = {
            "mini_project": proj_data.get("mini_project") or _fallback_mini(sub_id),
            "capstone_project": proj_data.get("capstone_project") or _fallback_capstone(sub_id, topic_name),
        }
    return clean if clean else None
def _run_major_project(topic_tree: dict, skill: str, level: str) -> dict:
    agent = _build_major_project_agent()
    topics_summary = "\n".join(
        f"- {t.get('name', '')}: {', '.join(s.get('name', '') for s in t.get('subtopics', []))}"
        for t in topic_tree.get("topics", [])
    )
    description = f"""Design ONE major portfolio project for someone completing a {skill} roadmap ({level} level).
The roadmap covers these topics:
{topics_summary}
Requirements:
- title: Compelling project name (4-6 words)
- description: 3-4 sentences explaining what it does and why it's impressive to a hiring manager
- tech_stack: List of 4-6 specific technologies/libraries from the {skill} ecosystem
- features: List of 5-7 key features that demonstrate different parts of the roadmap
- github_structure: Suggested folder structure as a single string (e.g. "src/ components/ hooks/ api/ tests/")
This must be genuinely impressive — not a to-do app, not a tutorial clone.
It should solve a real problem and showcase advanced {skill} skills.
Return ONLY valid JSON. No markdown. No explanation. No code fences.
Return format:
{{"title": "...", "description": "...", "tech_stack": [...], "features": [...], "github_structure": "..."}}"""
    task = Task(
        description=description,
        expected_output="Valid JSON object with title, description, tech_stack, features, github_structure.",
        agent=agent,
    )
    try:
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        result = crew.kickoff()
        parsed = extract_crew_result(result)
        if parsed and isinstance(parsed, dict) and parsed.get("title"):
            return parsed
    except Exception as e:
        print(f"[ProjectDesigner] Major project failed: {e}")
    return _default_major_project(skill)
def _fallback_mini(sub_name: str) -> dict:
    return {
        "title": f"Practice: {sub_name}",
        "use_case": f"Apply {sub_name} concepts in a small real-world scenario.",
        "tutorial_video_url": "",
    }
def _fallback_capstone(sub_name: str, topic_name: str) -> dict:
    return {
        "title": f"{topic_name} Capstone",
        "description": f"Combine {sub_name} with other {topic_name} skills to build a complete mini-application.",
        "use_case": f"Consolidate {topic_name} knowledge",
    }
def _fallback_subtopic_projects(sub_name: str, topic_name: str) -> dict:
    return {
        "mini_project": _fallback_mini(sub_name),
        "capstone_project": _fallback_capstone(sub_name, topic_name),
    }
def _default_major_project(skill: str) -> dict:
    return {
        "title": f"Full-Stack {skill} Portfolio Application",
        "description": (
            f"A comprehensive application demonstrating mastery of {skill}. "
            "Implements core features from across the roadmap into a single "
            "deployable, portfolio-worthy project that solves a real problem."
        ),
        "tech_stack": [skill, "Git", "Testing", "Deployment"],
        "features": [
            "User authentication",
            "Core domain features",
            "Responsive UI",
            "Data persistence",
            "Testing suite",
            "CI/CD deployment",
        ],
        "github_structure": "src/ tests/ docs/ .github/ README.md",
    }
def _build_project_fallbacks(topic_tree: dict, skill: str) -> dict:
    subtopics = {}
    for topic in topic_tree.get("topics", []):
        topic_name = topic.get("name", "")
        for sub in topic.get("subtopics", []):
            sub_id = sub.get("id", slugify(sub.get("name", "topic")))
            subtopics[sub_id] = _fallback_subtopic_projects(sub.get("name", ""), topic_name)
    return {
        "subtopics": subtopics,
        "major_project": _default_major_project(skill),
    }

import json
from crewai import Agent, Task, Crew, Process
from utils.helpers import (
    load_agent_config,
    load_task_config,
    get_mechanical_llm,
    extract_json,
)


def build_timeline_budget_agent() -> Agent:
    cfg = load_agent_config("timeline_budget")
    return Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        llm=get_mechanical_llm(),
        verbose=cfg.get("verbose", False),
        allow_delegation=cfg.get("allow_delegation", False),
    )


def build_timeline_budget_task(
    agent: Agent,
    topic_tree: dict,
    skill: str,
    level: str,
) -> Task:
    cfg = load_task_config("timeline_budget_task")
    topic_tree_json = json.dumps(topic_tree, separators=(",", ":"))
    description = cfg["description"].format(
        skill=skill,
        level=level,
        topic_tree=topic_tree_json,
    )
    return Task(
        description=description,
        expected_output=cfg["expected_output"],
        agent=agent,
    )


def run_timeline_budget(topic_tree: dict, skill: str, level: str) -> dict:
    try:
        agent = build_timeline_budget_agent()
        task = build_timeline_budget_task(agent, topic_tree, skill, level)
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )
        result = crew.kickoff()
        from utils.helpers import extract_crew_result

        data = extract_crew_result(result) or {}
        if "timeline" not in data:
            data["timeline"] = {}
        if "budget" not in data:
            data["budget"] = {}
        tl = data["timeline"]
        if not tl.get("hours_per_week"):
            tl["hours_per_week"] = 10
        if not tl.get("total_weeks") and tl.get("total_hours"):
            import math

            tl["total_weeks"] = max(1, math.ceil(tl["total_hours"] / 10))
        if not tl.get("total_hours") and tl.get("per_topic"):
            tl["total_hours"] = sum(t.get("hours", 0) for t in tl.get("per_topic", []))
        return data
    except Exception as e:
        print(f"[TimelineBudget] Failed: {e}")
        return _build_fallback(topic_tree, level)


def _build_fallback(topic_tree: dict, level: str) -> dict:
    import math

    hours_per_subtopic = {"beginner": 4, "intermediate": 6, "advanced": 9}
    base_hours = hours_per_subtopic.get(level, 5)
    topics = topic_tree.get("topics", [])
    per_topic = []
    total_hours = 0
    for topic in topics:
        subtopic_count = len(topic.get("subtopics", []))
        topic_hours = subtopic_count * base_hours
        total_hours += topic_hours
        per_topic.append(
            {
                "topic": topic.get("name", "Topic"),
                "hours": topic_hours,
            }
        )
    total_weeks = max(1, math.ceil(total_hours / 10))
    return {
        "timeline": {
            "total_weeks": total_weeks,
            "hours_per_week": 10,
            "total_hours": total_hours,
            "per_topic": per_topic,
        },
        "budget": {
            "free_path_total": "$0",
            "paid_path_total": "~$30–60",
            "items": [
                {
                    "name": "Core Learning",
                    "free": "YouTube + freeCodeCamp + Official Docs",
                    "paid_price": "~$15 (Udemy on sale)",
                },
                {
                    "name": "Practice Projects",
                    "free": "GitHub + personal projects",
                    "paid_price": "$0",
                },
                {
                    "name": "Supplementary",
                    "free": "Blogs, Stack Overflow, Discord",
                    "paid_price": "~$15–45 (optional)",
                },
            ],
        },
    }

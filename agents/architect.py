import json
from crewai import Agent, Task, Crew, Process
from utils.helpers import (
    extract_json,
    extract_crew_result,
    load_agent_config,
    load_task_config,
    get_reasoning_llm,
    slugify,
)


def build_architect_agent() -> Agent:
    cfg = load_agent_config("architect")
    return Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        llm=get_reasoning_llm(),
        verbose=cfg.get("verbose", False),
        allow_delegation=cfg.get("allow_delegation", False),
    )


def build_architect_task(agent: Agent, skill: str, level: str) -> Task:
    cfg = load_task_config("architect_task")
    description = cfg["description"].format(skill=skill, level=level)
    expected_output = cfg["expected_output"]
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )


def run_architect(skill: str, level: str) -> dict:
    agent = build_architect_agent()
    for attempt in range(1, 3):
        try:
            task = build_architect_task(agent, skill, level)
            if attempt == 2:
                task.description += (
                    "\n\nCRITICAL: Your previous response was not valid JSON. "
                    "Return ONLY a raw JSON object starting with { and ending with }. "
                    "No text before or after. No markdown code fences. No explanation."
                )
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False,
            )
            result = crew.kickoff()
            parsed = extract_crew_result(result)
            if isinstance(parsed, list) and parsed:
                parsed = {"topics": parsed}
            topics = parsed.get("topics", []) if parsed else []
            total_subtopics = sum(len(t.get("subtopics", [])) for t in topics)
            if not topics or total_subtopics == 0:
                raw_preview = str(getattr(result, "raw", ""))[:400]
                print(
                    f"[Architect] Invalid output (topics={len(topics)}, subtopics={total_subtopics}). Raw:\n{raw_preview}"
                )
                raise ValueError(
                    f"Architect returned {len(topics)} topics with {total_subtopics} subtopics,need at least 1 subtopic"
                )
            validated_tree = _ensure_subtopic_ids(parsed)
            return validated_tree
        except Exception as e:
            if attempt == 2:
                raise RuntimeError(f"Architect agent failed after {attempt} attempts: {e}") from e
            print(f"[Architect] Attempt {attempt} failed: {e}. Retrying...")


def _ensure_subtopic_ids(topic_tree: dict) -> dict:
    seen_ids = set()
    for topic in topic_tree.get("topics", []):
        for subtopic in topic.get("subtopics", []):
            raw_id = subtopic.get("id", "").strip()
            if not raw_id:
                raw_id = slugify(subtopic.get("name", "untitled"))
            candidate = raw_id
            counter = 2
            while candidate in seen_ids:
                candidate = f"{raw_id}-{counter}"
                counter += 1
            subtopic["id"] = candidate
            seen_ids.add(candidate)
    return topic_tree

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
\
\
\

import json
from crewai import Agent, Task, Crew, Process

from utils.helpers import (
    load_agent_config,
    load_task_config,
    get_mechanical_llm,
    extract_json,
    slugify,
)

def build_quiz_generator_agent() -> Agent:
\
\
\
\
\
\
\
\

    cfg = load_agent_config("quiz_generator")

    return Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        llm=get_mechanical_llm(),
        verbose=cfg.get("verbose", False),
        allow_delegation=cfg.get("allow_delegation", False),
    )

def build_quiz_task_for_topic(
    agent: Agent,
    topic: dict,
    skill: str,
) -> Task:
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

    cfg = load_task_config("quiz_generator_task")

    single_topic_tree = json.dumps(
        {"topics": [topic]}, separators=(",", ":")
    )

    description = cfg["description"].format(
        skill=skill,
        topic_tree=single_topic_tree,
    )

    description += (
        "\n\nIMPORTANT: Generate EXACTLY 5 questions per subtopic "
        "(3 MCQ + 2 open-ended) for the subtopics in this single topic only. "
        "Do NOT generate the final_quiz in this call — "
        "return an empty list [] for the 'final' key."
    )

    return Task(
        description=description,
        expected_output=cfg["expected_output"],
        agent=agent,

    )

def build_final_quiz_task(
    agent: Agent,
    topic_tree: dict,
    skill: str,
) -> Task:
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

    cfg = load_task_config("quiz_generator_task")

    topic_tree_json = json.dumps(topic_tree, separators=(",", ":"))

    description = (
        f"Generate a comprehensive final quiz for the skill: '{skill}'.\n\n"
        f"Full topic tree for context:\n{topic_tree_json}\n\n"
        "Generate EXACTLY 10 questions that cover the most important concepts "
        "across ALL topics in the roadmap.\n"
        "Mix: 7 MCQ + 3 open-ended.\n"
        "MCQ wrong options must be plausible misconceptions.\n"
        "Open-ended answers must be 2-3 sentences.\n"
        "Return ONLY valid JSON. No markdown. No explanation. No code fences.\n\n"
        "Return format:\n"
        '{"subtopics": {}, "final": [<10 questions>]}'
    )

    return Task(
        description=description,
        expected_output=cfg["expected_output"],
        agent=agent,

    )

def run_quiz_generator(topic_tree: dict, skill: str) -> dict:
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

    topics = topic_tree.get("topics", [])
    if not topics:
        return {"subtopics": {}, "final": []}

    agent = build_quiz_generator_agent()
    all_subtopic_questions = {}
    final_questions = []

    for topic in topics:
        topic_name = topic.get("name", "Unknown")
        try:
            task = build_quiz_task_for_topic(agent, topic, skill)
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False,
            )
            result = crew.kickoff()

            batch = _extract_quiz_result(result)
            if batch and batch.get("subtopics"):

                normalised = {
                    slugify(k) if not k.replace("-", "").isalnum() else k: v
                    for k, v in batch["subtopics"].items()
                }
                all_subtopic_questions.update(normalised)
            else:

                fallback = _build_subtopic_fallbacks(topic, skill)
                all_subtopic_questions.update(fallback)

        except Exception as e:
            print(f"[QuizGenerator] Topic '{topic_name}' failed: {e}")
            fallback = _build_subtopic_fallbacks(topic, skill)
            all_subtopic_questions.update(fallback)

    try:
        final_task = build_final_quiz_task(agent, topic_tree, skill)
        final_crew = Crew(
            agents=[agent],
            tasks=[final_task],
            process=Process.sequential,
            verbose=False,
        )
        final_result = final_crew.kickoff()
        final_batch = _extract_quiz_result(final_result)
        final_questions = final_batch.get("final", [])

        if len(final_questions) < 5:
            print(f"[QuizGenerator] Final quiz only has {len(final_questions)} questions, using fallback")
            final_questions = _build_final_quiz_fallback(topic_tree, skill)

    except Exception as e:
        print(f"[QuizGenerator] Final quiz failed: {e}")
        final_questions = _build_final_quiz_fallback(topic_tree, skill)

    return {
        "subtopics": all_subtopic_questions,
        "final": final_questions,
    }

def _extract_quiz_result(result) -> dict:
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

    from utils.helpers import extract_crew_result
    return extract_crew_result(result) or {}

def _build_subtopic_fallbacks(topic: dict, skill: str) -> dict:
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

    fallback = {}

    for sub in topic.get("subtopics", []):
        sub_id = sub.get("id", slugify(sub.get("name", "topic")))
        sub_name = sub.get("name", sub_id)

        fallback[sub_id] = [
            {
                "question": f"Which of the following best describes {sub_name}?",
                "type": "mcq",
                "options": [
                    f"A fundamental concept in {skill}",
                    f"An optional feature rarely used in {skill}",
                    f"A third-party library for {skill}",
                    f"A deprecated feature of {skill}",
                ],
                "answer": "a",
            },
            {
                "question": f"What problem does {sub_name} solve in {skill}?",
                "type": "mcq",
                "options": [
                    f"It improves code organisation and maintainability",
                    f"It only works with paid {skill} tools",
                    f"It replaces the need to learn {skill} fundamentals",
                    f"It is only relevant for large enterprise projects",
                ],
                "answer": "a",
            },
            {
                "question": f"Which scenario is a common use case for {sub_name}?",
                "type": "mcq",
                "options": [
                    f"Building production {skill} applications",
                    f"Replacing all other {skill} concepts",
                    f"Only for academic {skill} research",
                    f"Debugging unrelated programming languages",
                ],
                "answer": "a",
            },
            {
                "question": f"What is the primary purpose of {sub_name} in {skill}?",
                "type": "open",
                "options": [],
                "answer": (
                    f"{sub_name} is a core concept in {skill} that enables "
                    f"developers to build more effective applications. "
                    f"Understanding it is essential for professional {skill} development."
                ),
            },
            {
                "question": f"When would you use {sub_name} in a real-world {skill} project?",
                "type": "open",
                "options": [],
                "answer": (
                    f"{sub_name} is used when applying its core principles "
                    f"in a {skill} project. It is particularly valuable in scenarios "
                    f"that require structured, maintainable code."
                ),
            },
        ]

    return fallback

def _build_final_quiz_fallback(topic_tree: dict, skill: str) -> list:
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

    questions = []

    for topic in topic_tree.get("topics", []):
        topic_name = topic.get("name", "")
        if not topic_name:
            continue

        questions.append({
            "question": f"Explain the key concepts covered in '{topic_name}' for {skill}.",
            "type": "open",
            "options": [],
            "answer": (
                f"'{topic_name}' covers the essential skills needed for {skill} "
                f"in this area. A strong understanding of these concepts is "
                f"required for professional-level {skill} development."
            ),
        })

        if len(questions) >= 10:
            break

    return questions

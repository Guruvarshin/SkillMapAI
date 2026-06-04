import asyncio
import sys
import nest_asyncio

# Fix WinError 10054 — Windows ProactorEventLoop teardown noise.
# SelectorEventLoop does not have this issue.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from crewai.flow.flow import Flow, start, listen
from agents.state import RoadmapState
from agents.architect import run_architect
from agents.video_hunter import run_video_hunter, build_video_fallbacks
from agents.course_curator import run_course_curator, build_course_fallbacks
from agents.project_designer import run_project_designer, _build_project_fallbacks
from agents.quiz_generator import run_quiz_generator
from agents.timeline_budget import run_timeline_budget, _build_fallback as tb_fallback
from agents.assembler import run_assembler
from db.roadmaps import update_status

nest_asyncio.apply()
_progress_log: list[str] = []


def get_progress_updates() -> list[str]:
    return _progress_log.copy()


def _push_update(message: str) -> None:
    _progress_log.append(message)
    print(f"[Flow] {message}")


class SkillMapFlow(Flow[RoadmapState]):
    @start()
    def architect_step(self) -> None:
        _push_update("🏗️ Stage 1: Building your learning roadmap structure...")
        try:
            topic_tree = run_architect(
                skill=self.state.skill,
                level=self.state.level,
            )
            self.state.topic_tree = topic_tree
            subtopic_count = self.state.get_subtopic_count()
            _push_update(
                f"✅ Stage 1 complete: {len(topic_tree.get('topics', []))} topics, "
                f"{subtopic_count} subtopics"
            )
            self.state.log(f"Architect complete: {subtopic_count} subtopics")
        except Exception as e:
            error_msg = f"Architect agent failed: {e}"
            _push_update(f"❌ Stage 1 failed: {error_msg}")
            self.state.add_error(error_msg)
            update_status(self.state.roadmap_id, "failed", error_msg)
            raise RuntimeError(error_msg) from e

    @listen(architect_step)
    async def stage_2_parallel(self) -> None:
        _push_update("🔍 Stage 2: Searching for resources, projects, quizzes...")
        if not self.state.has_topic_tree():
            _push_update("⚠️  Stage 2 skipped — no topic tree from Stage 1")
            return
        topic_tree = self.state.topic_tree
        skill = self.state.skill
        level = self.state.level
        results = await asyncio.gather(
            asyncio.to_thread(self._run_video_hunter, topic_tree, skill),
            asyncio.to_thread(self._run_course_curator, topic_tree, skill),
            asyncio.to_thread(self._run_project_designer, topic_tree, skill, level),
            asyncio.to_thread(self._run_quiz_generator, topic_tree, skill),
            asyncio.to_thread(self._run_timeline_budget, topic_tree, skill, level),
            return_exceptions=True,
        )
        videos, courses, projects, quizzes, timeline_budget = results
        self.state.videos_data = (
            videos if isinstance(videos, dict) else build_video_fallbacks(topic_tree, skill)
        )
        self.state.courses_data = (
            courses if isinstance(courses, dict) else build_course_fallbacks(topic_tree, skill)
        )
        self.state.projects_data = (
            projects if isinstance(projects, dict) else _build_project_fallbacks(topic_tree, skill)
        )
        self.state.quiz_data = (
            quizzes if isinstance(quizzes, dict) else {"subtopics": {}, "final": []}
        )
        self.state.timeline_budget_data = (
            timeline_budget if isinstance(timeline_budget, dict) else tb_fallback(topic_tree, level)
        )
        worker_names = [
            "VideoHunter",
            "CourseCurator",
            "ProjectDesigner",
            "QuizGenerator",
            "TimelineBudget",
        ]
        for name, result in zip(worker_names, results):
            if isinstance(result, Exception):
                self.state.add_error(f"{name} failed: {result}")
                _push_update(f"⚠️  {name} failed — using fallback data")
        _push_update("✅ Stage 2 complete: all resources gathered")

    @listen(stage_2_parallel)
    def assembler_step(self) -> None:
        _push_update("🔧 Stage 3: Assembling your roadmap...")
        try:
            final_roadmap = run_assembler(self.state)
            self.state.final_roadmap = final_roadmap
            subtopic_count = self.state.get_subtopic_count()
            _push_update(
                f"✅ Roadmap complete! {subtopic_count} subtopics with "
                f"videos, courses, projects, and quizzes."
            )
            self.state.log("Assembler complete — roadmap saved to MongoDB")
        except Exception as e:
            error_msg = f"Assembler failed: {e}"
            _push_update(f"❌ Stage 3 failed: {error_msg}")
            self.state.add_error(error_msg)
            raise RuntimeError(error_msg) from e

    def _run_video_hunter(self, topic_tree: dict, skill: str) -> dict:
        _push_update("  📹 Searching YouTube for tutorial videos...")
        try:
            result = run_video_hunter(topic_tree, skill)
            _push_update("  📹 Videos found")
            return result or build_video_fallbacks(topic_tree, skill)
        except Exception as e:
            _push_update(f"  ⚠️  Video search failed, using search URLs")
            return build_video_fallbacks(topic_tree, skill)

    def _run_course_curator(self, topic_tree: dict, skill: str) -> dict:
        _push_update("  📚 Searching for courses and resources...")
        try:
            result = run_course_curator(topic_tree, skill)
            _push_update("  📚 Courses found")
            return result or build_course_fallbacks(topic_tree, skill)
        except Exception as e:
            _push_update(f"  ⚠️  Course search failed, using search URLs")
            return build_course_fallbacks(topic_tree, skill)

    def _run_project_designer(self, topic_tree: dict, skill: str, level: str) -> dict:
        _push_update("  🔨 Designing projects...")
        try:
            result = run_project_designer(topic_tree, skill, level)
            _push_update("  🔨 Projects designed")
            return result or _build_project_fallbacks(topic_tree, skill)
        except Exception as e:
            _push_update(f"  ⚠️  Project designer failed, using templates")
            return _build_project_fallbacks(topic_tree, skill)

    def _run_quiz_generator(self, topic_tree: dict, skill: str) -> dict:
        _push_update("  ❓ Generating quiz questions...")
        try:
            result = run_quiz_generator(topic_tree, skill)
            _push_update("  ❓ Quizzes generated")
            return result or {"subtopics": {}, "final": []}
        except Exception as e:
            _push_update(f"  ⚠️  Quiz generator failed, using placeholder questions")
            return {"subtopics": {}, "final": []}

    def _run_timeline_budget(self, topic_tree: dict, skill: str, level: str) -> dict:
        _push_update("  🗓️  Estimating timeline and budget...")
        try:
            result = run_timeline_budget(topic_tree, skill, level)
            _push_update("  🗓️  Timeline and budget ready")
            return result or tb_fallback(topic_tree, level)
        except Exception as e:
            _push_update(f"  ⚠️  Timeline agent failed, using estimates")
            return tb_fallback(topic_tree, level)


def run_skillmap_flow(
    skill: str,
    level: str,
    roadmap_id: str,
    user_id: str,
) -> dict:
    global _progress_log
    _progress_log = []
    _push_update(f"🚀 Starting generation for: {skill} ({level})")
    flow = SkillMapFlow()
    flow.kickoff(
        inputs={
            "skill": skill,
            "level": level,
            "roadmap_id": roadmap_id,
            "user_id": user_id,
        }
    )
    if not flow.state.final_roadmap:
        raise RuntimeError(
            "Flow completed but final_roadmap is empty. " f"Errors: {flow.state.errors}"
        )
    return flow.state.final_roadmap

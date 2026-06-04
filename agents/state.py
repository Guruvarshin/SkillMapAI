from typing import Any, Callable, Optional
from pydantic import BaseModel, Field
class RoadmapState(BaseModel):
    skill: str = Field(default="")
    level: str = Field(default="beginner")
    roadmap_id: str = Field(default="")
    user_id: str = Field(default="")
    topic_tree: dict = Field(default_factory=dict)
    videos_data: dict = Field(default_factory=dict)
    courses_data: dict = Field(default_factory=dict)
    projects_data: dict = Field(default_factory=dict)
    quiz_data: dict = Field(default_factory=dict)
    timeline_budget_data: dict = Field(default_factory=dict)
    final_roadmap: dict = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    progress_log: list[str] = Field(default_factory=list)
    def log(self, message: str) -> None:
        self.progress_log.append(message)
    def add_error(self, error: str) -> None:
        self.errors.append(error)
    def has_topic_tree(self) -> bool:
        return bool(self.topic_tree.get("topics"))
    def get_all_subtopic_ids(self) -> list[str]:
        ids = []
        for topic in self.topic_tree.get("topics", []):
            for sub in topic.get("subtopics", []):
                if sub.get("id"):
                    ids.append(sub["id"])
        return ids
    def get_subtopic_count(self) -> int:
        return len(self.get_all_subtopic_ids())
    def stage_2_complete(self) -> bool:
        return all([
            bool(self.videos_data),
            bool(self.courses_data),
            bool(self.projects_data),
            bool(self.quiz_data),
            bool(self.timeline_budget_data),
        ])
    def get_topic_tree_json(self) -> str:
        import json
        return json.dumps(self.topic_tree, separators=(",", ":"))

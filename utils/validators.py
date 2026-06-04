from typing import Any
from pydantic import BaseModel, Field, field_validator, model_validator
class QuizQuestion(BaseModel):
    question: str = Field(default="Question not available")
    type: str = Field(default="open")                           
    options: list[str] = Field(default_factory=list)
    answer: str = Field(default="")
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        v = v.lower().strip()
        if v in ("mcq", "multiple_choice", "multiple choice", "mc"):
            return "mcq"
        return "open"
    @field_validator("options", mode="before")
    @classmethod
    def ensure_options_list(cls, v: Any) -> list:
        if v is None:
            return []
        if isinstance(v, str):
            return [opt.strip() for opt in v.split(",") if opt.strip()]
        return list(v)
class VideoResource(BaseModel):
    title: str = Field(default="Video not available")
    url: str = Field(default="")
    channel: str = Field(default="")
    type: str = Field(default="video")                           
    @field_validator("url", mode="before")
    @classmethod
    def clean_url(cls, v: Any) -> str:
        if not v:
            return ""
        return str(v).strip()
    @field_validator("type")
    @classmethod
    def validate_video_type(cls, v: str) -> str:
        return "playlist" if "playlist" in v.lower() else "video"
class TextResource(BaseModel):
    title: str = Field(default="Resource not available")
    url: str = Field(default="")
    type: str = Field(default="article")                                       
    @field_validator("url", mode="before")
    @classmethod
    def clean_url(cls, v: Any) -> str:
        return str(v).strip() if v else ""
class CourseResource(BaseModel):
    name: str = Field(default="Course not available")
    platform: str = Field(default="")
    url: str = Field(default="")
    certificate: bool = Field(default=False)
    @field_validator("certificate", mode="before")
    @classmethod
    def coerce_certificate(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "yes", "1", "available")
        return bool(v)
class PaidCourseResource(BaseModel):
    name: str = Field(default="Course not available")
    platform: str = Field(default="")
    url: str = Field(default="")
    price: str = Field(default="Price unavailable")
    rating: str = Field(default="")
    @field_validator("price", mode="before")
    @classmethod
    def clean_price(cls, v: Any) -> str:
        if not v:
            return "Price unavailable"
        return str(v).strip()
class MiniProject(BaseModel):
    title: str = Field(default="Project not available")
    use_case: str = Field(default="")
    tutorial_video_url: str = Field(default="")
class CapstonProject(BaseModel):
    title: str = Field(default="Capstone not available")
    description: str = Field(default="")
    use_case: str = Field(default="")
class MajorProject(BaseModel):
    title: str = Field(default="Project not available")
    description: str = Field(default="")
    tech_stack: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    github_structure: str = Field(default="")
    @field_validator("tech_stack", "features", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> list:
        if not v:
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return list(v)
class Subtopic(BaseModel):
    id: str = Field(default="")                                             
    name: str = Field(default="Subtopic")
    description: str = Field(default="")
    hours_estimate: int = Field(default=3)
    videos: list[VideoResource] = Field(default_factory=list)
    text_resource: TextResource = Field(default_factory=TextResource)
    free_course: CourseResource = Field(default_factory=CourseResource)
    paid_course: PaidCourseResource = Field(default_factory=PaidCourseResource)
    mini_project: MiniProject = Field(default_factory=MiniProject)
    capstone_project: CapstonProject = Field(default_factory=CapstonProject)
    @field_validator("hours_estimate", mode="before")
    @classmethod
    def coerce_hours(cls, v: Any) -> int:
        if isinstance(v, int):
            return max(1, v)
        if isinstance(v, float):
            return max(1, int(v))
        if isinstance(v, str):
            match = __import__("re").search(r"\d+", v)
            return int(match.group()) if match else 3
        return 3
    @field_validator("videos", mode="before")
    @classmethod
    def ensure_videos_list(cls, v: Any) -> list:
        if not v:
            return []
        return v if isinstance(v, list) else [v]
    @model_validator(mode="after")
    def ensure_id(self) -> "Subtopic":
        if not self.id and self.name:
            from utils.helpers import slugify
            self.id = slugify(self.name)
        return self
class Topic(BaseModel):
    name: str = Field(default="Topic")
    subtopics: list[Subtopic] = Field(default_factory=list)
    @field_validator("subtopics", mode="before")
    @classmethod
    def ensure_subtopics(cls, v: Any) -> list:
        if not v:
            return []
        return v
class TimelineEntry(BaseModel):
    topic: str = Field(default="")
    hours: int = Field(default=0)
class Timeline(BaseModel):
    total_weeks: int = Field(default=8)
    hours_per_week: int = Field(default=10)
    per_topic: list[TimelineEntry] = Field(default_factory=list)
    @field_validator("total_weeks", "hours_per_week", mode="before")
    @classmethod
    def coerce_int(cls, v: Any) -> int:
        try:
            return max(1, int(v))
        except (TypeError, ValueError):
            return 8
class BudgetItem(BaseModel):
    name: str = Field(default="")
    free: str = Field(default="Free")
    paid_price: str = Field(default="")
class Budget(BaseModel):
    free_path_total: str = Field(default="$0 (completely free)")
    paid_path_total: str = Field(default="")
    items: list[BudgetItem] = Field(default_factory=list)
class RoadmapOutput(BaseModel):
    topics: list[Topic] = Field(default_factory=list)
    timeline: Timeline = Field(default_factory=Timeline)
    budget: Budget = Field(default_factory=Budget)
    major_project: MajorProject = Field(default_factory=MajorProject)
    @field_validator("topics", mode="before")
    @classmethod
    def ensure_topics(cls, v: Any) -> list:
        if not v:
            return []
        return v
    def to_mongo_dict(self) -> dict:
        return self.model_dump(mode="python")

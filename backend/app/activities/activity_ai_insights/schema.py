from pydantic import BaseModel


class ActivityAIInsight(BaseModel):
    id: int | None = None
    activity_id: int | None = None
    insight_text: str | None = None
    model_used: str | None = None
    created_at: str | None = None

    model_config = {"from_attributes": True}


class ActivityAIInsightCreate(BaseModel):
    activity_id: int
    insight_text: str | None = None
    model_used: str | None = None

    model_config = {"from_attributes": True}


class ActivityAIInsightEdit(BaseModel):
    id: int
    insight_text: str | None = None
    model_used: str | None = None

    model_config = {"from_attributes": True}


__all__ = [
    "ActivityAIInsight",
    "ActivityAIInsightCreate",
    "ActivityAIInsightEdit",
]

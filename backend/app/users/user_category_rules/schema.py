from pydantic import BaseModel


class UserCategoryRule(BaseModel):
    id: int | None = None
    user_id: int | None = None
    activity_type_id: int | None = None
    category_id: int | None = None
    min_distance: float | None = None
    max_distance: float | None = None
    min_hr: float | None = None
    max_hr: float | None = None
    min_elevation_gain: float | None = None
    max_elevation_gain: float | None = None
    created_at: str | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}


class UserCategoryRuleCreate(BaseModel):
    user_id: int
    activity_type_id: int
    category_id: int
    min_distance: float | None = None
    max_distance: float | None = None
    min_hr: float | None = None
    max_hr: float | None = None
    min_elevation_gain: float | None = None
    max_elevation_gain: float | None = None

    model_config = {"from_attributes": True}


class UserCategoryRuleEdit(BaseModel):
    id: int
    min_distance: float | None = None
    max_distance: float | None = None
    min_hr: float | None = None
    max_hr: float | None = None
    min_elevation_gain: float | None = None
    max_elevation_gain: float | None = None

    model_config = {"from_attributes": True}


__all__ = [
    "UserCategoryRule",
    "UserCategoryRuleCreate",
    "UserCategoryRuleEdit",
]

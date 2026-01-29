from pydantic import BaseModel


class UserActivityStats(BaseModel):
    id: int | None = None
    activity_type_id: int | None = None
    user_category_id: int | None = None
    avg_distance: float | None = None
    m2_distance: float | None = None
    avg_heart_rate: float | None = None
    m2_heart_rate: float | None = None
    avg_elevation_gain: float | None = None
    m2_elevation_gain: float | None = None
    avg_elevation_loss: float | None = None
    m2_elevation_loss: float | None = None
    total_count: int | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}


class UserActivityStatsCreate(BaseModel):
    activity_type_id: int
    user_category_id: int
    avg_distance: float | None = None
    m2_distance: float | None = None
    avg_heart_rate: float | None = None
    m2_heart_rate: float | None = None
    avg_elevation_gain: float | None = None
    m2_elevation_gain: float | None = None
    avg_elevation_loss: float | None = None
    m2_elevation_loss: float | None = None
    total_count: int | None = None

    model_config = {"from_attributes": True}


class UserActivityStatsEdit(BaseModel):
    id: int
    avg_distance: float | None = None
    m2_distance: float | None = None
    avg_heart_rate: float | None = None
    m2_heart_rate: float | None = None
    avg_elevation_gain: float | None = None
    m2_elevation_gain: float | None = None
    avg_elevation_loss: float | None = None
    m2_elevation_loss: float | None = None
    total_count: int | None = None

    model_config = {"from_attributes": True}


__all__ = [
    "UserActivityStats",
    "UserActivityStatsCreate",
    "UserActivityStatsEdit",
]

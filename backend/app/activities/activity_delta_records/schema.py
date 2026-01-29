from pydantic import BaseModel


class ActivityDeltaRecord(BaseModel):
    id: int | None = None
    activity_id: int | None = None
    user_category_id: int | None = None
    delta_distance: float | None = None
    delta_distance_pct: float | None = None
    delta_hr: float | None = None
    delta_hr_pct: float | None = None
    delta_elevation_gain: float | None = None
    delta_elevation_gain_pct: float | None = None
    delta_elevation_loss: float | None = None
    delta_elevation_loss_pct: float | None = None
    created_at: str | None = None

    model_config = {"from_attributes": True}


class ActivityDeltaRecordCreate(BaseModel):
    activity_id: int
    user_category_id: int
    delta_distance: float | None = None
    delta_distance_pct: float | None = None
    delta_hr: float | None = None
    delta_hr_pct: float | None = None
    delta_elevation_gain: float | None = None
    delta_elevation_gain_pct: float | None = None
    delta_elevation_loss: float | None = None
    delta_elevation_loss_pct: float | None = None

    model_config = {"from_attributes": True}


class ActivityDeltaRecordEdit(BaseModel):
    id: int
    delta_distance: float | None = None
    delta_distance_pct: float | None = None
    delta_hr: float | None = None
    delta_hr_pct: float | None = None
    delta_elevation_gain: float | None = None
    delta_elevation_gain_pct: float | None = None
    delta_elevation_loss: float | None = None
    delta_elevation_loss_pct: float | None = None

    model_config = {"from_attributes": True}


__all__ = [
    "ActivityDeltaRecord",
    "ActivityDeltaRecordCreate",
    "ActivityDeltaRecordEdit",
]

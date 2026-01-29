from pydantic import BaseModel


class ActivityType(BaseModel):
    id: int | None = None
    name: str
    display_name: str

    model_config = {"from_attributes": True}


class ActivityTypeCreate(BaseModel):
    name: str
    display_name: str

    model_config = {"from_attributes": True}


class ActivityTypeEdit(BaseModel):
    id: int
    name: str | None = None
    display_name: str | None = None

    model_config = {"from_attributes": True}


__all__ = [
    "ActivityType",
    "ActivityTypeCreate",
    "ActivityTypeEdit",
]

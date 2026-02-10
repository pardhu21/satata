from pydantic import BaseModel


class ActivityCategory(BaseModel):
    id: int | None = None
    name: str
    display_name: str

    model_config = {"from_attributes": True}


class ActivityCategoryCreate(BaseModel):
    name: str
    display_name: str

    model_config = {"from_attributes": True}


class ActivityCategoryEdit(BaseModel):
    id: int
    name: str | None = None
    display_name: str | None = None

    model_config = {"from_attributes": True}


__all__ = [
    "ActivityCategory",
    "ActivityCategoryCreate",
    "ActivityCategoryEdit",
]

from pydantic import BaseModel


class UserCategoryRule(BaseModel):
    id: int | None = None
    user_id: int | None = None
    activity_type_id: int | None = None
    category_id: int | None = None
    values: Dict[str, Any]
    created_at: str | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}


class UserCategoryRuleCreate(BaseModel):
    user_id: int
    activity_type_id: int
    category_id: int
    values: Dict[str, Any]

    model_config = {"from_attributes": True}


class UserCategoryRuleEdit(BaseModel):
    id: int
    values: Dict[str, Any]

    model_config = {"from_attributes": True}


__all__ = [
    "UserCategoryRule",
    "UserCategoryRuleCreate",
    "UserCategoryRuleEdit",
]

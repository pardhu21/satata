from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import activities.activity.dependencies as activities_dependencies
import activities.activity_ai_insights.crud as crud
import activities.activity_ai_insights.schema as schema

import auth.security as auth_security
import core.database as core_database


router = APIRouter()


@router.get(
    "/activity_id/{activity_id}",
    response_model=list[schema.ActivityAIInsight] | None,
)
async def read_insights_for_activity(
    activity_id: int,
    validate_id: Annotated[Callable, Depends(activities_dependencies.validate_activity_id)],
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes, scopes=["activities:read"])],
    token_user_id: Annotated[int, Depends(auth_security.get_sub_from_access_token)],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_insights_for_activity(activity_id, token_user_id, db)


@router.get(
    "/{insight_id}",
    response_model=schema.ActivityAIInsight | None,
)
async def read_insight_by_id(
    insight_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes, scopes=["activities:read"])],
    token_user_id: Annotated[int, Depends(auth_security.get_sub_from_access_token)],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_insight_by_id(insight_id, db)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.ActivityAIInsight,
)
async def create_insight(
    insight: schema.ActivityAIInsightCreate,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes, scopes=["activities:write"])],
    token_user_id: Annotated[int, Depends(auth_security.get_sub_from_access_token)],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    # Ensure the activity exists and the user owns it
    activity = activities_dependencies.validate_activity_id(insight.activity_id)
    # validate_activity_id returns a callable dependency in other routers; call activity_crud to verify ownership
    return crud.create_insight(insight, db)


@router.put(
    "/{insight_id}",
    response_model=schema.ActivityAIInsight,
)
async def update_insight(
    insight_id: int,
    insight_edit: schema.ActivityAIInsightEdit,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes, scopes=["activities:write"])],
    token_user_id: Annotated[int, Depends(auth_security.get_sub_from_access_token)],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.edit_insight(insight_id, insight_edit, token_user_id, db)


@router.delete("/{insight_id}")
async def delete_insight(
    insight_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes, scopes=["activities:write"])],
    token_user_id: Annotated[int, Depends(auth_security.get_sub_from_access_token)],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    crud.delete_insight(insight_id, token_user_id, db)
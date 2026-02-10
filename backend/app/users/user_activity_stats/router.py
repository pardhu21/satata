from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import users.user_activity_stats.crud as crud
import users.user_activity_stats.schema as schema

import auth.security as auth_security
import core.database as core_database


router = APIRouter()


@router.get("/", response_model=list[schema.UserActivityStats] | None)
async def read_user_activity_stats(
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_all_stats(db)


@router.get("/{stats_id}", response_model=schema.UserActivityStats | None)
async def read_user_activity_stats_by_id(
    stats_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_stats_by_id(stats_id, db)


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema.UserActivityStats)
async def create_user_activity_stats(
    stats_in: schema.UserActivityStatsCreate,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.create_stats(stats_in, db)


@router.put("/{stats_id}", response_model=schema.UserActivityStats)
async def update_user_activity_stats(
    stats_id: int,
    stats_edit: schema.UserActivityStatsEdit,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.edit_stats(stats_id, stats_edit, db)


@router.delete("/{stats_id}")
async def delete_user_activity_stats(
    stats_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    crud.delete_stats(stats_id, db)

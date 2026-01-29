from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import activities.activity_types.crud as crud
import activities.activity_types.schema as schema

import auth.security as auth_security
import core.database as core_database


router = APIRouter()


@router.get("/", response_model=list[schema.ActivityType] | None)
async def read_activity_types(
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_all_types(db)


@router.get("/{type_id}", response_model=schema.ActivityType | None)
async def read_activity_type(
    type_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_type_by_id(type_id, db)


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema.ActivityType)
async def create_activity_type(
    type_in: schema.ActivityTypeCreate,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.create_type(type_in, db)


@router.put("/{type_id}", response_model=schema.ActivityType)
async def update_activity_type(
    type_id: int,
    type_edit: schema.ActivityTypeEdit,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.edit_type(type_id, type_edit, db)


@router.delete("/{type_id}")
async def delete_activity_type(
    type_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    crud.delete_type(type_id, db)

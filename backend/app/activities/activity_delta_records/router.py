from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import activities.activity_delta_records.crud as crud
import activities.activity_delta_records.schema as schema

import auth.security as auth_security
import core.database as core_database


router = APIRouter()


@router.get("/", response_model=list[schema.ActivityDeltaRecord] | None)
async def read_delta_records(
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_all_delta_records(db)


@router.get("/{record_id}", response_model=schema.ActivityDeltaRecord | None)
async def read_delta_record(
    record_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_delta_by_id(record_id, db)


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema.ActivityDeltaRecord)
async def create_delta_record(
    record_in: schema.ActivityDeltaRecordCreate,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.create_delta(record_in, db)


@router.put("/{record_id}", response_model=schema.ActivityDeltaRecord)
async def update_delta_record(
    record_id: int,
    record_edit: schema.ActivityDeltaRecordEdit,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.edit_delta(record_id, record_edit, db)


@router.delete("/{record_id}")
async def delete_delta_record(
    record_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    crud.delete_delta(record_id, db)

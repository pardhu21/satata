from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import activities.activity_categories.crud as crud
import activities.activity_categories.schema as schema

import auth.security as auth_security
import core.database as core_database


router = APIRouter()


@router.get("/", response_model=list[schema.ActivityCategory] | None)
async def read_activity_categories(
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_all_categories(db)


@router.get("/{category_id}", response_model=schema.ActivityCategory | None)
async def read_activity_category(
    category_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_category_by_id(category_id, db)


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema.ActivityCategory)
async def create_activity_category(
    cat_in: schema.ActivityCategoryCreate,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.create_category(cat_in, db)


@router.put("/{category_id}", response_model=schema.ActivityCategory)
async def update_activity_category(
    category_id: int,
    cat_edit: schema.ActivityCategoryEdit,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.edit_category(category_id, cat_edit, db)


@router.delete("/{category_id}")
async def delete_activity_category(
    category_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["activities:write"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    crud.delete_category(category_id, db)

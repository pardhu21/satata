from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import users.user_category_rules.crud as crud
import users.user_category_rules.schema as schema

import auth.security as auth_security
import core.database as core_database


router = APIRouter()


@router.get("/", response_model=list[schema.UserCategoryRule] | None)
async def read_user_category_rules(
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_all_rules(db)


@router.get("/{rule_id}", response_model=schema.UserCategoryRule | None)
async def read_user_category_rule(
    rule_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:read"])],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.get_rule_by_id(rule_id, db)


@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schema.UserCategoryRule)
async def create_user_category_rule(
    rule_in: schema.UserCategoryRuleCreate,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:write"])],
    token_user_id: Annotated[int, Depends(auth_security.get_sub_from_access_token)],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    # ensure the creator is the same user
    if rule_in.user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create rule for another user",
        )
    return crud.create_rule(rule_in, db)


@router.put("/{rule_id}", response_model=schema.UserCategoryRule)
async def update_user_category_rule(
    rule_id: int,
    rule_edit: schema.UserCategoryRuleEdit,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:write"])],
    token_user_id: Annotated[int, Depends(auth_security.get_sub_from_access_token)],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    return crud.edit_rule(rule_id, rule_edit, token_user_id, db)


@router.delete("/{rule_id}")
async def delete_user_category_rule(
    rule_id: int,
    _check_scopes: Annotated[Callable, Security(auth_security.check_scopes,
                                              scopes=["users:write"])],
    token_user_id: Annotated[int, Depends(auth_security.get_sub_from_access_token)],
    db: Annotated[Session, Depends(core_database.get_db)],
):
    crud.delete_rule(rule_id, token_user_id, db)

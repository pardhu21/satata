import activities.activity_categories.models as models
import activities.activity_categories.schema as schema

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import core.logger as core_logger


def get_all_categories(db: Session):
    try:
        cats = db.query(models.ActivityCategories).all()
        return cats if cats else None
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_all_categories: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_category_by_id(category_id: int, db: Session):
    try:
        return (
            db.query(models.ActivityCategories)
            .filter(models.ActivityCategories.id == category_id)
            .first()
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_category_by_id: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_category(cat_in: schema.ActivityCategoryCreate, db: Session):
    try:
        db_obj = models.ActivityCategories(
            name=cat_in.name,
            display_name=cat_in.display_name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in create_category: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def edit_category(category_id: int, cat_edit: schema.ActivityCategoryEdit, db: Session):
    try:
        db_obj = get_category_by_id(category_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity category not found",
            )
        if cat_edit.name is not None:
            db_obj.name = cat_edit.name
        if cat_edit.display_name is not None:
            db_obj.display_name = cat_edit.display_name
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in edit_category: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def delete_category(category_id: int, db: Session):
    try:
        db_obj = get_category_by_id(category_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity category not found",
            )
        db.delete(db_obj)
        db.commit()
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in delete_category: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err

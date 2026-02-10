import activities.activity_types.models as models
import activities.activity_types.schema as schema

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import core.logger as core_logger


def get_all_types(db: Session):
    """
    Retrieve all activity types.

    Args:
        db: Database session.

    Returns:
        List of ActivityTypes or None.

    Raises:
        HTTPException: On internal server error.
    """
    try:
        types = db.query(models.ActivityTypes).all()
        return types if types else None
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_all_types: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_type_by_id(type_id: int, db: Session):
    try:
        return (
            db.query(models.ActivityTypes)
            .filter(models.ActivityTypes.id == type_id)
            .first()
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_type_by_id: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_type(type_in: schema.ActivityTypeCreate, db: Session):
    try:
        db_obj = models.ActivityTypes(
            name=type_in.name,
            display_name=type_in.display_name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in create_type: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def edit_type(type_id: int, type_edit: schema.ActivityTypeEdit, db: Session):
    try:
        db_obj = get_type_by_id(type_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity type not found",
            )
        if type_edit.name is not None:
            db_obj.name = type_edit.name
        if type_edit.display_name is not None:
            db_obj.display_name = type_edit.display_name
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in edit_type: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def delete_type(type_id: int, db: Session):
    try:
        db_obj = get_type_by_id(type_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity type not found",
            )
        db.delete(db_obj)
        db.commit()
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in delete_type: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err

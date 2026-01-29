import activities.activity_delta_records.models as models
import activities.activity_delta_records.schema as schema

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import core.logger as core_logger


def get_all_delta_records(db: Session):
    try:
        recs = db.query(models.ActivityDeltaRecords).all()
        return recs if recs else None
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_all_delta_records: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_delta_by_id(record_id: int, db: Session):
    try:
        return (
            db.query(models.ActivityDeltaRecords)
            .filter(models.ActivityDeltaRecords.id == record_id)
            .first()
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_delta_by_id: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_delta(record_in: schema.ActivityDeltaRecordCreate, db: Session):
    try:
        db_obj = models.ActivityDeltaRecords(
            activity_id=record_in.activity_id,
            user_category_id=record_in.user_category_id,
            delta_distance=record_in.delta_distance,
            delta_distance_pct=record_in.delta_distance_pct,
            delta_hr=record_in.delta_hr,
            delta_hr_pct=record_in.delta_hr_pct,
            delta_elevation_gain=record_in.delta_elevation_gain,
            delta_elevation_gain_pct=record_in.delta_elevation_gain_pct,
            delta_elevation_loss=record_in.delta_elevation_loss,
            delta_elevation_loss_pct=record_in.delta_elevation_loss_pct,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in create_delta: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def edit_delta(record_id: int, record_edit: schema.ActivityDeltaRecordEdit, db: Session):
    try:
        db_obj = get_delta_by_id(record_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delta record not found",
            )
        # apply provided updates
        for field in [
            "delta_distance",
            "delta_distance_pct",
            "delta_hr",
            "delta_hr_pct",
            "delta_elevation_gain",
            "delta_elevation_gain_pct",
            "delta_elevation_loss",
            "delta_elevation_loss_pct",
        ]:
            val = getattr(record_edit, field)
            if val is not None:
                setattr(db_obj, field, val)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in edit_delta: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def delete_delta(record_id: int, db: Session):
    try:
        db_obj = get_delta_by_id(record_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delta record not found",
            )
        db.delete(db_obj)
        db.commit()
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in delete_delta: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err

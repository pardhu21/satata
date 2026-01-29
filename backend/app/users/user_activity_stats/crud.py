import users.user_activity_stats.models as models
import users.user_activity_stats.schema as schema

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import core.logger as core_logger


def get_all_stats(db: Session):
    try:
        stats = db.query(models.UserActivityStats).all()
        return stats if stats else None
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_all_stats: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_stats_by_id(stats_id: int, db: Session):
    try:
        return (
            db.query(models.UserActivityStats)
            .filter(models.UserActivityStats.id == stats_id)
            .first()
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_stats_by_id: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_stats(stats_in: schema.UserActivityStatsCreate, db: Session):
    try:
        db_obj = models.UserActivityStats(
            activity_type_id=stats_in.activity_type_id,
            user_category_id=stats_in.user_category_id,
            avg_distance=stats_in.avg_distance,
            m2_distance=stats_in.m2_distance,
            avg_heart_rate=stats_in.avg_heart_rate,
            m2_heart_rate=stats_in.m2_heart_rate,
            avg_elevation_gain=stats_in.avg_elevation_gain,
            m2_elevation_gain=stats_in.m2_elevation_gain,
            avg_elevation_loss=stats_in.avg_elevation_loss,
            m2_elevation_loss=stats_in.m2_elevation_loss,
            total_count=stats_in.total_count or 0,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in create_stats: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def edit_stats(stats_id: int, stats_edit: schema.UserActivityStatsEdit, db: Session):
    try:
        db_obj = get_stats_by_id(stats_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User activity stats not found",
            )
        # apply updates
        for field in [
            "avg_distance",
            "m2_distance",
            "avg_heart_rate",
            "m2_heart_rate",
            "avg_elevation_gain",
            "m2_elevation_gain",
            "avg_elevation_loss",
            "m2_elevation_loss",
            "total_count",
        ]:
            val = getattr(stats_edit, field)
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
            f"Error in edit_stats: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def delete_stats(stats_id: int, db: Session):
    try:
        db_obj = get_stats_by_id(stats_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User activity stats not found",
            )
        db.delete(db_obj)
        db.commit()
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in delete_stats: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err

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
            user_id=stats_in.user_id,
            activity_type_id=stats_in.activity_type_id,
            category_id=stats_in.category_id,
            avg_distance=stats_in.avg_distance,
            m2_distance=stats_in.m2_distance,
            avg_heart_rate=stats_in.avg_heart_rate,
            m2_heart_rate=stats_in.m2_heart_rate,
            avg_pace=stats_in.avg_pace,
            m2_pace=stats_in.m2_pace,
            avg_duration=stats_in.avg_duration,
            m2_duration=stats_in.m2_duration,
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
        print(err)
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
            "avg_pace",
            "m2_pace",
            "avg_duration",
            "m2_duration",
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

def create_or_update_stats(
    stats_in: schema.UserActivityStatsCreate,
    db: Session,
):
    try:
        db_obj = (
            db.query(models.UserActivityStats)
            .filter(
                models.UserActivityStats.user_id == stats_in.user_id,
                models.UserActivityStats.activity_type_id == stats_in.activity_type_id,
                models.UserActivityStats.category_id == stats_in.category_id,
            )
            .one_or_none()
        )

        if db_obj:
            # update existing row
            for field in [
                "avg_distance",
                "m2_distance",
                "avg_heart_rate",
                "m2_heart_rate",
                "avg_pace",
                "m2_pace",
                "avg_duration",
                "m2_duration",
                "avg_elevation_gain",
                "m2_elevation_gain",
                "avg_elevation_loss",
                "m2_elevation_loss",
                "total_count",
            ]:
                val = getattr(stats_in, field)
                if val is not None:
                    setattr(db_obj, field, val)

        else:
            # create new row
            db_obj = models.UserActivityStats(
                user_id=stats_in.user_id,
                activity_type_id=stats_in.activity_type_id,
                category_id=stats_in.category_id,
                avg_distance=stats_in.avg_distance,
                m2_distance=stats_in.m2_distance,
                avg_heart_rate=stats_in.avg_heart_rate,
                m2_heart_rate=stats_in.m2_heart_rate,
                avg_pace=stats_in.avg_pace,
                m2_pace=stats_in.m2_pace,
                avg_duration=stats_in.avg_duration,
                m2_duration=stats_in.m2_duration,
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
            f"Error in create_or_update_stats: {err}", "error", exc=err
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


def user_stats_by_user_id_activity_type_category(
    user_id: int,
    activity_type_id: int,
    category_id: int,
    db: Session,
):
    try:
        return (
            db.query(models.UserActivityStats)
            .filter(
                models.UserActivityStats.user_id == user_id,
                models.UserActivityStats.activity_type_id == activity_type_id,
                models.UserActivityStats.category_id == category_id,
            )
            .first()
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in user_stats_by_user_id_activity_type_category: {err}",
            "error",
            exc=err,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err
    
def update_stats_on_activity_delete(activity, db: Session):
    try:
        stats = user_stats_by_user_id_activity_type_category(
            user_id=activity.user_id,
            activity_type_id=activity.activity_type_id,
            category_id=activity.category_id,
            db=db,
        )
        if not stats:
            core_logger.print_to_log(
                f"No stats found for user {activity.user_id}, "
                f"activity type {activity.activity_type_id}, "
                f"category {activity.category_id}. Skipping stats update on activity delete."
            )
            return

        # Here you would implement the logic to update the stats based on the deleted activity.
        # This is a placeholder and should be replaced with actual update logic.
        # For example, you might want to recalculate averages or decrement total_count.

        db.commit()
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in update_stats_on_activity_delete: {err}", "error", exc=err
        )
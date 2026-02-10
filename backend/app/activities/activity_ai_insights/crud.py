import activities.activity.models as activity_models
import activities.activity.crud as activity_crud
import activities.activity_ai_insights.models as models
import activities.activity_ai_insights.schema as schema

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import core.logger as core_logger


def get_all_insights(db: Session):
    """
    Retrieve all activity AI insights.

    Args:
        db: Database session.

    Returns:
        A list of ActivityAIInsights or None.

    Raises:
        HTTPException: On internal server error.
    """
    try:
        insights = db.query(models.ActivityAIInsights).all()
        return insights if insights else None
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_all_insights: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_insights_for_activity(activity_id: int, token_user_id: int, db: Session):
    """
    Retrieve AI insights for a specific activity.

    Args:
        activity_id: Activity primary key.
        token_user_id: ID of requesting user.
        db: Database session.

    Returns:
        A list of ActivityAIInsights or None.

    Raises:
        HTTPException: On internal server error.
    """
    try:
        activity = activity_crud.get_activity_by_id_from_user_id(
            activity_id, token_user_id, db
        )

        if not activity:
            return None

        insight = (
            db.query(models.ActivityAIInsights)
            .filter(models.ActivityAIInsights.activity_id == activity_id)
            .order_by(models.ActivityAIInsights.created_at.desc())
            .first()
        )

        if not insight:
            return None

        return insight
    except Exception as err:
        print(err)
        core_logger.print_to_log(
            f"Error in get_insights_for_activity: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_insight_by_id(insight_id: int, db: Session):
    """
    Retrieve a single AI insight by ID.

    Args:
        insight_id: Insight primary key.
        db: Database session.

    Returns:
        ActivityAIInsights instance or None.

    Raises:
        HTTPException: On internal server error.
    """
    try:
        insight = (
            db.query(models.ActivityAIInsights)
            .filter(models.ActivityAIInsights.id == insight_id)
            .first()
        )

        return insight
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_insight_by_id: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_insight(insight: schema.ActivityAIInsightCreate, db: Session):
    """
    Create a new AI insight record.

    Args:
        insight: Pydantic create schema.
        db: Database session.

    Returns:
        Created ActivityAIInsights instance.

    Raises:
        HTTPException: On internal server error.
    """
    try:
        db_insight = models.ActivityAIInsights(
            activity_id=insight.activity_id,
            insight_text=insight.insight_text,
            model_used=insight.model_used,
        )

        db.add(db_insight)
        db.commit()
        db.refresh(db_insight)

        return db_insight
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in create_insight: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def edit_insight(insight_id: int, insight_edit: schema.ActivityAIInsightEdit, token_user_id: int, db: Session):
    """
    Edit an existing AI insight.

    Args:
        insight_id: Insight primary key.
        insight_edit: Pydantic edit schema.
        token_user_id: ID of requesting user.
        db: Database session.

    Returns:
        Updated ActivityAIInsights instance.

    Raises:
        HTTPException: 404 if not found, 403 if not allowed, 500 on error.
    """
    try:
        db_insight = (
            db.query(models.ActivityAIInsights)
            .filter(models.ActivityAIInsights.id == insight_id)
            .first()
        )

        if not db_insight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI insight not found",
            )

        # Verify ownership of the parent activity
        activity = activity_crud.get_activity_by_id_from_user_id(
            db_insight.activity_id, token_user_id, db
        )

        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )

        if activity.user_id != token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this insight",
            )

        # Apply updates
        if insight_edit.insight_text is not None:
            db_insight.insight_text = insight_edit.insight_text
        if insight_edit.model_used is not None:
            db_insight.model_used = insight_edit.model_used

        db.commit()
        db.refresh(db_insight)

        return db_insight
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in edit_insight: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def delete_insight(insight_id: int, token_user_id: int, db: Session):
    """
    Delete an AI insight record.

    Args:
        insight_id: Insight primary key.
        token_user_id: ID of requesting user.
        db: Database session.

    Returns:
        None

    Raises:
        HTTPException: 404 if not found, 403 if not allowed, 500 on error.
    """
    try:
        db_insight = (
            db.query(models.ActivityAIInsights)
            .filter(models.ActivityAIInsights.id == insight_id)
            .first()
        )

        if not db_insight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI insight not found",
            )

        activity = activity_crud.get_activity_by_id_from_user_id(
            db_insight.activity_id, token_user_id, db
        )

        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )

        if activity.user_id != token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this insight",
            )

        db.delete(db_insight)
        db.commit()

    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in delete_insight: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err

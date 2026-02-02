import os
import requests
import json

import activities.activity_delta_records.models as models
import activities.activity_delta_records.schema as schema

import activities.activity.crud as activity_crud
import users.user_category_rules.crud as user_category_rules_crud

from users.user_activity_stats.schema import UserActivityStats
import users.user_activity_stats.crud as user_activity_stats_crud
import users.user_activity_stats.utils as user_stats_utils
import activities.activity_delta_records.utils as delta_utils
import activities.activity_ai_insights.crud as ai_insights_crud
import activities.activity_ai_insights.schema as ai_insights_schema

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
            user_id=record_in.user_id,
            activity_id=record_in.activity_id,
            activity_type_id=record_in.activity_type_id,
            category_id=record_in.category_id,
            delta_distance=record_in.delta_distance,
            delta_distance_pct=record_in.delta_distance_pct,
            delta_hr=record_in.delta_hr,
            delta_hr_pct=record_in.delta_hr_pct,
            delta_avg_pace=record_in.delta_avg_pace,
            delta_avg_pace_pct=record_in.delta_avg_pace_pct,
            delta_duration=record_in.delta_duration,
            delta_duration_pct=record_in.delta_duration_pct,
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
        print(err)
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
            "delta_avg_pace",
            "delta_avg_pace_pct",
            "delta_duration",
            "delta_duration_pct",
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


# def test(db: Session):
#     activities = activity_crud.get_all_activities(db)
#     run_activities = [x for x in activities if x.activity_type == 1]
#     rules = user_category_rules_crud.get_all_rules(db)
#     for activity in run_activities:
#         category_id = delta_utils.classify_activity_by_rule_vectors(activity, rules)
#         user_stats = user_activity_stats_crud.get_all_stats(db)
#         if user_stats:
#             user_stats = [
#                 x for x in user_stats
#                 if x.user_id == activity.user_id and
#                 x.activity_type_id == activity.activity_type and
#                 x.category_id == category_id
#             ]
#             user_stats = user_stats[0] if user_stats else None
#         activity_delta = delta_utils.compute_activity_delta(
#             category_id,
#             user_stats,
#             activity
#         )

#         print(activity_delta.__dict__)

#         create_delta(activity_delta, db)

#         activity_stats = user_stats_utils.update_user_category_stats(
#             category_id,
#             user_stats,
#             activity
#         )

#         user_activity_stats_crud.create_or_update_stats(activity_stats, db)
#         print(activity_stats.avg_distance, activity.distance, activity_stats.category_id)


#     return run_activities

def test(db: Session):
    records = get_all_delta_records(db)

    for record in records:
        # Set your OpenAI API key in env variable OPENAI_API_KEY
        url = "https://api.openai.com/v1/chat/completions"

        payload = {
            "model": "gpt-4.1-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a fitness analytics assistant that generates training insights from running data."
                },
                {
                    "role": "user",
                    "content": json.dumps(record.to_dict())
                }
            ]
        }

        headers = {
            # "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        print(response.json()["choices"][0]["message"]["content"])
        insights = response.json()["choices"][0]["message"]["content"]

        ai_insights_crud.create_insight(
            ai_insights_schema.ActivityAIInsightCreate(
                activity_id=record.activity_id,
                insight_text=insights
            ),
            db
        )

    return records

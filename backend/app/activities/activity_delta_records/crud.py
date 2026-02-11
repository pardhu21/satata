import os
import requests
import json

import core.config as core_config

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
from activities.activity_categories.utils import CANONICAL_ACTIVITY_CATEGORIES
from activities.activity.utils import ACTIVITY_ID_TO_NAME

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


def create_deltas_for_all_activities(db: Session):
    activities = activity_crud.get_all_activities(db)
    sorted_activities = sorted(activities, key=lambda x: x.start_time)

    rules = user_category_rules_crud.get_all_rules(db)
    for activity in sorted_activities:
        category_id = delta_utils.classify_activity_by_rule_vectors(activity, rules)
        user_stats = user_activity_stats_crud.get_all_stats(db)
        if user_stats:
            user_stats = [
                x for x in user_stats
                if x.user_id == activity.user_id and
                x.activity_type_id == activity.activity_type and
                x.category_id == category_id
            ]
            user_stats = user_stats[0] if user_stats else None
        activity_delta = delta_utils.compute_activity_delta(
            category_id,
            user_stats,
            activity
        )

        create_delta(activity_delta, db)

        activity_stats = user_stats_utils.update_user_category_stats(
            category_id,
            user_stats,
            activity
        )

        user_activity_stats_crud.create_or_update_stats(activity_stats, db)

    return sorted_activities

def create_ai_insights_for_all_activities(db: Session):
    records = get_all_delta_records(db)

    for record in records:
        # Set your OpenAI API key in env variable OPENAI_API_KEY

        url = "https://api.openai.com/v1/chat/completions"

        slug, display = CANONICAL_ACTIVITY_CATEGORIES.get(
            record.category_id,
            ("unknown", "Unknown"),
        )

        activity_type = ACTIVITY_ID_TO_NAME.get(record.activity_type_id, "Unknown")

        SYSTEM_PROMPT = f"""
        You are an endurance sports analytics assistant.

        You analyze delta metrics between two activities. The input contains changes in distance,
        duration, heart rate, pace/speed, and elevation.

        The current activity is:
        - activity_type: "{activity_type}"

        The workout intensity category is:
        - category_slug: "{slug}"
        - category_name: "{display}"

        Interpret the data in the context of BOTH:
        1) the sport type
        2) the workout category

        Guidelines:
        - Running / Walking / Hiking: pace and HR are primary signals.
        - Cycling / E-bike / MTB / Gravel: speed, elevation gain, and HR matter more than raw distance.
        - Swimming: duration and effort trends matter more than GPS distance.
        - Strength / HIIT / Crossfit / Workout: HR and duration dominate; distance may be irrelevant.
        - Skiing / Snowboarding / Surfing / Paddling: elevation, time moving, and HR are key.
        - Yoga / recovery-style activities should show low cardiovascular stress.

        Category expectations:
        - Recovery → very low stress
        - Easy / Steady → aerobic
        - Tempo / Threshold / VO₂ → high sustained effort
        - Long → extended duration
        - Race → maximal or near-maximal
        - Mixed → variable intensity

        Your job is to:
        - Identify improvements vs declines
        - Interpret effort vs efficiency
        - Detect fatigue or recovery signals
        - Explain terrain or modality effects when elevation changes sharply
        - Mention important percentage changes explicitly when making a claim
        - Round percentages to 1 decimal place

        OUTPUT FORMAT:
        - Plain text only (no JSON)
        - FIRST line MUST be: "Activity: <activity_type> | Category: <category_name> (<category_slug>)"
        - Then 1–2 sentence summary
        - Then 3–5 bullet points
        - End with a short training recommendation
        """

        # -------------------------------
        # Few-shot examples (TEXT)
        # -------------------------------

        EXAMPLES = [

            # -------------------------------------------------
            # Example 1 — Run / Easy (normal GPS metrics)
            # -------------------------------------------------
            {
                "role": "user",
                "content": json.dumps({
                    "id": 101,
                    "user_id": 1,
                    "activity_id": 9001,
                    "activity_type_id": 1,   # Run
                    "category_id": 2,        # Easy
                    "delta_distance_pct": 11.8,
                    "delta_hr_pct": -4.9,
                    "delta_avg_pace_pct": -3.5,
                    "delta_duration_pct": 9.6,
                    "delta_elevation_gain_pct": 4.0,
                }),
            },
            {
                "role": "assistant",
                "content": (
                    "Activity: Run | Category: Easy (easy)\n\n"
                    "You ran farther and faster with lower heart rate, indicating improved aerobic efficiency.\n\n"
                    "- Distance increased ~11.8%, boosting aerobic volume.\n"
                    "- Pace improved ~3.5% while HR dropped ~4.9%.\n"
                    "- Duration rose ~9.6%, increasing endurance stimulus.\n"
                    "- Slightly more climbing did not raise effort.\n\n"
                    "Recommendation: Maintain similar easy mileage and gradually extend one run per week."
                ),
            },

            # -------------------------------------------------
            # Example 2 — Ride / Tempo (hillier, shorter)
            # -------------------------------------------------
            {
                "role": "user",
                "content": json.dumps({
                    "id": 202,
                    "user_id": 1,
                    "activity_id": 9002,
                    "activity_type_id": 4,   # Ride
                    "category_id": 4,        # Tempo
                    "delta_distance_pct": -17.2,
                    "delta_hr_pct": 6.1,
                    "delta_duration_pct": -14.3,
                    "delta_elevation_gain_pct": 28.0,
                }),
            },
            {
                "role": "assistant",
                "content": (
                    "Activity: Ride | Category: Tempo (tempo)\n\n"
                    "This tempo ride was shorter but much hillier, pushing heart rate higher and increasing relative effort.\n\n"
                    "- Distance dropped ~17.2% while climbing rose ~28%.\n"
                    "- HR increased ~6.1%, pointing to tougher workload.\n"
                    "- Duration fell ~14.3%, reducing sustained tempo time.\n"
                    "- Efficiency declined slightly versus your usual tempo rides.\n\n"
                    "Recommendation: Keep the next session easy and attempt a longer steady tempo later in the week."
                ),
            },

            # -------------------------------------------------
            # Example 3 — Workout / Threshold (no distance/pace)
            # -------------------------------------------------
            {
                "role": "user",
                "content": json.dumps({
                    "id": 279,
                    "user_id": 1,
                    "activity_id": 102,
                    "activity_type_id": 10,  # Workout
                    "category_id": 5,       # Threshold
                    "delta_distance": 0.0,
                    "delta_distance_pct": None,
                    "delta_hr_pct": -1.6,
                    "delta_avg_pace_pct": None,
                    "delta_duration_pct": -6.2,
                    "delta_elevation_gain_pct": None,
                }),
            },
            {
                "role": "assistant",
                "content": (
                    "Activity: Workout | Category: Threshold (threshold)\n\n"
                    "This threshold session was slightly shorter with a small drop in heart rate, suggesting a marginally lighter load than usual.\n\n"
                    "- Duration fell ~6.2%, reducing sustained high-intensity time.\n"
                    "- HR dropped ~1.6%, possibly reflecting better efficiency or reduced effort.\n"
                    "- Distance and pace metrics were not relevant for this activity type.\n"
                    "- Overall training stress was modestly lower than typical threshold work.\n\n"
                    "Recommendation: Extend time-at-intensity next time if this was meant to be a key workout."
                ),
            },

            # -------------------------------------------------
            # Example 4 — Hike / Long
            # -------------------------------------------------
            {
                "role": "user",
                "content": json.dumps({
                    "id": 333,
                    "user_id": 1,
                    "activity_id": 9004,
                    "activity_type_id": 12,  # Hike
                    "category_id": 8,       # Long
                    "delta_distance_pct": 9.7,
                    "delta_duration_pct": 17.5,
                    "delta_elevation_gain_pct": 21.2,
                    "delta_hr_pct": 2.3,
                }),
            },
            {
                "role": "assistant",
                "content": (
                    "Activity: Hike | Category: Long (long)\n\n"
                    "You extended both time and climbing with only a small rise in heart rate, creating a strong endurance stimulus.\n\n"
                    "- Duration increased ~17.5%, supporting long-effort adaptation.\n"
                    "- Elevation gain rose ~21.2%, making the route tougher.\n"
                    "- HR climbed just ~2.3%, showing good aerobic control.\n"
                    "- Distance also increased moderately.\n\n"
                    "Recommendation: Recover well and keep the next long outing similar before progressing again."
                ),
            },

            # -------------------------------------------------
            # Example 5 — Yoga / Recovery
            # -------------------------------------------------
            {
                "role": "user",
                "content": json.dumps({
                    "id": 401,
                    "user_id": 1,
                    "activity_id": 9005,
                    "activity_type_id": 14,  # Yoga
                    "category_id": 1,       # Recovery
                    "delta_hr_pct": -6.4,
                    "delta_duration_pct": 4.9,
                    "delta_distance_pct": None,
                }),
            },
            {
                "role": "assistant",
                "content": (
                    "Activity: Yoga | Category: Recovery (recovery)\n\n"
                    "This session stayed very low stress with a calmer cardiovascular response while lasting slightly longer.\n\n"
                    "- HR dropped ~6.4%, reinforcing recovery intent.\n"
                    "- Duration increased ~4.9%, extending mobility work.\n"
                    "- Distance metrics are not meaningful for this activity.\n"
                    "- No signs of excess training load.\n\n"
                    "Recommendation: Keep yoga as an anchor for recovery between harder days."
                ),
            },
        ]


        # -------------------------------
        # Final payload
        # -------------------------------

        payload = {
            "model": "gpt-4.1-mini",
            "messages": (
                [{"role": "system", "content": SYSTEM_PROMPT}]
                + EXAMPLES
                + [{"role": "user", "content": json.dumps(record.to_dict())}]
            ),
        }

        headers = {
            "Authorization": f"Bearer {core_config.OPENAI_API_KEY}",
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

    return ""

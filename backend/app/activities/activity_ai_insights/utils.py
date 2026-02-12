import time
import requests
import json

from sqlalchemy.orm import Session
from activities.activity.schema import Activity
from activities.activity_delta_records.models import ActivityDeltaRecords
from activities.activity_ai_insights.schema import ActivityAIInsightCreate

import activities.activity_ai_insights.crud as ai_insights_crud
import activities.activity_delta_records.crud as delta_crud
import users.user_category_rules.crud as user_category_rules_crud
import users.user_activity_stats.crud as user_stats_crud

from activities.activity_categories.utils import CANONICAL_ACTIVITY_CATEGORIES
from activities.activity.constants import ACTIVITY_ID_TO_NAME

import activities.activity_delta_records.utils as delta_utils
import core.config as core_config



def generate_ai_insight(record: ActivityDeltaRecords, api_key: str, retries: int = 3, timeout: int = 30) -> str:
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
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()

            return response.json()["choices"][0]["message"]["content"]

        except Exception as err:
            last_error = err

            # No sleep after final attempt
            if attempt < retries:
                sleep_time = 2 ** attempt
                time.sleep(sleep_time)

    # All retries failed
    raise last_error


def get_activity_ai_insights(activity: Activity, db: Session):
    rules = user_category_rules_crud.get_rules_by_user_activity_type(
        activity.user_id,
        activity.activity_type,
        db=db
    )

    if not rules:
        return

    category_id = delta_utils.classify_activity_by_rule_vectors(
        activity=activity,
        rules=rules,
    )

    stats = user_stats_crud.user_stats_by_user_id_activity_type_category(
        activity.user_id,
        activity.activity_type,
        category_id,
        db=db
    )

    delta_record = delta_utils.compute_activity_delta(
        activity=activity,
        category_id=category_id,
        stats=stats,
    )

    delta_record = delta_crud.create_delta(
        record_in=delta_record,
        db=db,
    )

    insight_text = generate_ai_insight(
        record=delta_record,
        api_key=core_config.OPENAI_API_KEY,
    )

    ai_insights_crud.create_insight(
        insight=ActivityAIInsightCreate(
            activity_id=activity.id,
            insight_text=insight_text,
        ),
        db=db,
    )

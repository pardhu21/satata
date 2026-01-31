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

import activities.activity_delta_records.utils as delta_utils



def generate_ai_insight(record: ActivityDeltaRecords, api_key: str, retries: int = 3, timeout: int = 30) -> str:
    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a fitness analytics assistant that generates training insights from running data.",
            },
            {
                "role": "user",
                "content": json.dumps(record.to_dict()),
            },
        ],
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
        api_key=API_KEY,
    )

    ai_insights_crud.create_insight(
        insight=ActivityAIInsightCreate(
            activity_id=activity.id,
            insight_text=insight_text,
        ),
        db=db,
    )

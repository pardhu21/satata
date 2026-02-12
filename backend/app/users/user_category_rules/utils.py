"""
Canonical user category rules for running activity type.

Mapping structure:
USER_CATEGORY_RULES: dict[int, dict] where key is category_id and
value is a dict with the fields required to insert into user_category_rules.
"""
from typing import Dict
from users.user_category_rules.models import UserCategoryRules
from users.users import models as users_models

from activities.activity.constants import ACTIVITY_ID_TO_NAME
from activities.activity_types import utils as activity_types_utils
from activities.activity_categories import utils as activity_category_utils


# Default values to be used when creating user category rules for a user.
USER_CATEGORY_RULES: Dict[int, dict] = {
    1: {
        "activity_type_id": 1,
        "category_id": 1,
        "min_distance": 2000,
        "max_distance": 8000,
        "min_hr": 90,
        "max_hr": 120,
        "min_elevation_gain": 0,
        "max_elevation_gain": 150,
    },
    2: {
        "activity_type_id": 1,
        "category_id": 2,
        "min_distance": 3000,
        "max_distance": 15000,
        "min_hr": 110,
        "max_hr": 140,
        "min_elevation_gain": 0,
        "max_elevation_gain": 300,
    },
    3: {
        "activity_type_id": 1,
        "category_id": 3,
        "min_distance": 5000,
        "max_distance": 18000,
        "min_hr": 130,
        "max_hr": 155,
        "min_elevation_gain": 0,
        "max_elevation_gain": 500,
    },
    4: {
        "activity_type_id": 1,
        "category_id": 4,
        "min_distance": 5000,
        "max_distance": 20000,
        "min_hr": 150,
        "max_hr": 170,
        "min_elevation_gain": 0,
        "max_elevation_gain": 600,
    },
    5: {
        "activity_type_id": 1,
        "category_id": 5,
        "min_distance": 4000,
        "max_distance": 15000,
        "min_hr": 165,
        "max_hr": 180,
        "min_elevation_gain": 0,
        "max_elevation_gain": 700,
    },
    6: {
        "activity_type_id": 1,
        "category_id": 6,
        "min_distance": 2000,
        "max_distance": 10000,
        "min_hr": 175,
        "max_hr": 190,
        "min_elevation_gain": 0,
        "max_elevation_gain": 800,
    },
    7: {
        "activity_type_id": 1,
        "category_id": 7,
        "min_distance": 500,
        "max_distance": 6000,
        "min_hr": 180,
        "max_hr": 200,
        "min_elevation_gain": 0,
        "max_elevation_gain": 500,
    },
    8: {
        "activity_type_id": 1,
        "category_id": 8,
        "min_distance": 15000,
        "max_distance": 40000,
        "min_hr": 120,
        "max_hr": 155,
        "min_elevation_gain": 0,
        "max_elevation_gain": 1200,
    },
    9: {
        "activity_type_id": 1,
        "category_id": 9,
        "min_distance": 3000,
        "max_distance": 42000,
        "min_hr": 160,
        "max_hr": 200,
        "min_elevation_gain": 0,
        "max_elevation_gain": 2000,
    },
    10: {
        "activity_type_id": 1,
        "category_id": 10,
        "min_distance": 3000,
        "max_distance": 25000,
        "min_hr": 120,
        "max_hr": 190,
        "min_elevation_gain": 0,
        "max_elevation_gain": 1000,
    },
}

def seed_user_category_rules_for_user(
    db,
    core_logger,
    user_id: int,
    defaults_by_activity: dict = None,
    categories_by_id: dict = None,
) -> bool:
    """
    Seed default user category rules for a single user.
    """
    processed_ok = True

    if defaults_by_activity is None:
        defaults_by_activity = (
            activity_types_utils.build_activity_category_default_values()
        )
    if categories_by_id is None:
        categories_by_id = dict(
            activity_category_utils.CANONICAL_ACTIVITY_CATEGORIES
        )

    for type_id, display_name in sorted(
        ACTIVITY_ID_TO_NAME.items(),
        key=lambda kv: kv[0],
    ):
        internal_name = activity_types_utils.normal_to_snake_case(
            display_name
        )
        per_category_defaults = defaults_by_activity.get(
            internal_name, {}
        )

        for cat_id, (cat_name, _cat_disp) in categories_by_id.items():
            pd = per_category_defaults.get(cat_name, {})
            dist_val = pd.get("distance")
            hr_val = pd.get("hr")
            elev_val = pd.get("elevation_gain")

            # Skip unsupported activity-category combos
            if (
                dist_val is None
                and hr_val is None
                and elev_val is None
            ):
                continue

            try:
                existing = (
                    db.query(UserCategoryRules)
                    .filter(
                        UserCategoryRules.user_id == user_id,
                        UserCategoryRules.activity_type_id == type_id,
                        UserCategoryRules.category_id == cat_id,
                    )
                    .first()
                )
                if existing:
                    core_logger.print_to_log_and_console(
                        f"Migration s1 - Rule already exists for user {user_id}, "
                        f"activity {type_id}, category {cat_id}. Skipping."
                    )
                    continue

                new_rule = UserCategoryRules(
                    user_id=user_id,
                    activity_type_id=type_id,
                    category_id=cat_id,
                    values=pd,
                )
                db.add(new_rule)

            except Exception as err:
                processed_ok = False
                core_logger.print_to_log_and_console(
                    f"Migration s1 - Failed to insert rule for user {user_id}, "
                    f"activity {type_id}, category {cat_id}: {err}",
                    "error",
                    exc=err,
                )

    return processed_ok


def seed_user_category_rules(db, core_logger) -> bool:
    """
    Seed default user category rules for all users.
    """
    try:
        users = db.query(users_models.Users).all()
    except Exception as e:
        core_logger.print_to_log_and_console(
            f"Migration s1 - Failed to fetch users: {e}",
            "error",
            exc=e,
        )
        return False

    if not users:
        core_logger.print_to_log_and_console(
            "Migration s1 - No users found. Skipping user_category_rules seeding."
        )
        return True

    defaults_by_activity = (
        activity_types_utils.build_activity_category_default_values()
    )
    categories_by_id = dict(
        activity_category_utils.CANONICAL_ACTIVITY_CATEGORIES
    )

    processed_ok = True

    for user in users:
        ok = seed_user_category_rules_for_user(
            db=db,
            core_logger=core_logger,
            user_id=user.id,
            defaults_by_activity=defaults_by_activity,
            categories_by_id=categories_by_id,
        )
        if not ok:
            processed_ok = False

    return processed_ok

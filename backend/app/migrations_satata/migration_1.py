from sqlalchemy.orm import Session

import activities.activity.utils as activity_utils
import activities.activity_types.models as activity_types_models
import activities.activity_types.crud as activity_types_crud
import activities.activity_types.utils as activity_types_utils
import activities.activity_categories.utils as activity_category_utils
import activities.activity_categories.models as activity_categories_models
import migrations_satata.crud as migrations_crud
import users.user_category_rules.utils as user_category_rules_utils

import core.logger as core_logger


def process_migration_1(db: Session):
    """
    Seed activity_types, activity_categories, and per-user user_category_rules using
    canonical utils so that separate migrations 2 and 3 are not required.

    Idempotent: skips inserting rows that already exist by natural keys.
    """
    core_logger.print_to_log_and_console(
        "Started migration s1 - seed types, categories and user rules"
    )

    processed_ok = True

    try:
        # -----------------------------
        # Seed activity categories (was migration_2)
        # -----------------------------
        for cat_id, (cat_name, cat_display) in (
            activity_category_utils.CANONICAL_ACTIVITY_CATEGORIES.items()
        ):
            try:
                # Skip if an entry with this id already exists
                existing = (
                    db.query(activity_categories_models.ActivityCategories)
                    .filter(
                        activity_categories_models.ActivityCategories.id == cat_id
                    )
                    .first()
                )
                if existing:
                    core_logger.print_to_log_and_console(
                        f"Migration s1 - Category id {cat_id} already exists. Skipping."
                    )
                    continue

                # Skip if an entry with the same name exists
                existing_by_name = (
                    db.query(activity_categories_models.ActivityCategories)
                    .filter(
                        activity_categories_models.ActivityCategories.name
                        == cat_name
                    )
                    .first()
                )
                if existing_by_name:
                    core_logger.print_to_log_and_console(
                        f"Migration s1 - Category name '{cat_name}' already exists. Skipping."
                    )
                    continue

                new_cat = activity_categories_models.ActivityCategories(
                    id=cat_id,
                    name=cat_name,
                    display_name=cat_display,
                )

                db.add(new_cat)
            except Exception as inner_err:
                processed_ok = False
                core_logger.print_to_log_and_console(
                    f"Migration s1 - Failed to insert category {cat_id}: {inner_err}",
                    "error",
                    exc=inner_err,
                )

        # -----------------------------
        # Seed activity types (enhanced)
        # -----------------------------
        for type_id, display_name in sorted(
            activity_utils.ACTIVITY_ID_TO_NAME.items(), key=lambda kv: kv[0]
        ):
            try:
                # Skip if an entry with this id already exists
                existing_by_id = activity_types_crud.get_type_by_id(type_id, db)
                if existing_by_id:
                    core_logger.print_to_log_and_console(
                        f"Migration s1 - Activity type {type_id} already exists. Skipping."
                    )
                    continue

                internal_name = activity_types_utils.normal_to_snake_case(
                    display_name
                )

                # Skip if an entry with the same internal name exists
                existing_by_name = (
                    db.query(activity_types_models.ActivityTypes)
                    .filter(
                        activity_types_models.ActivityTypes.name == internal_name
                    )
                    .first()
                )
                if existing_by_name:
                    core_logger.print_to_log_and_console(
                        f"Migration s1 - Activity type name '{internal_name}' already exists. Skipping."
                    )
                    continue

                params = activity_types_utils.get_parameters_for_activity(
                    display_name
                )

                new_type = activity_types_models.ActivityTypes(
                    id=type_id,
                    name=internal_name,
                    display_name=display_name,
                    ai_insight_parameters=params if params is not None else None,
                )
                db.add(new_type)
            except Exception as inner_err:
                processed_ok = False
                core_logger.print_to_log_and_console(
                    f"Migration s1 - Failed to insert activity type {type_id}: {inner_err}",
                    "error",
                    exc=inner_err,
                )

        # -----------------------------
        # Seed per-user rules from defaults (was migration_3, now generalized)
        # -----------------------------
        try:
            user_category_rules_utils.seed_user_category_rules(db, core_logger=core_logger)
        except Exception as e:
            processed_ok = False
            core_logger.print_to_log_and_console(
                f"Migration s1 - Failed to fetch users: {e}",
                "error",
                exc=e,
            )
        # Commit all inserts at once
        db.commit()
    except Exception as err:
        db.rollback()
        processed_ok = False
        core_logger.print_to_log_and_console(
            f"Migration s1 - Error during seeding process: {err}",
            "error",
            exc=err,
        )

    # Mark migration as executed on success
    if processed_ok:
        try:
            migrations_crud.set_migration_as_executed(1, db)
        except Exception as err:
            core_logger.print_to_log_and_console(
                f"Migration s1 - Failed to set migration as executed: {err}",
                "error",
                exc=err,
            )
            return
    else:
        core_logger.print_to_log_and_console(
            "Migration s1 completed with errors. Will try again later.",
            "error",
        )

    core_logger.print_to_log_and_console("Finished migration s1")


def normal_to_snake_case(value: str) -> str:
    """
    Convert a human-friendly string to snake_case.

    Args:
        value: The input string.

    Returns:
        The snake_cased string.

    Raises:
        ValueError: If value is None.
    """
    if value is None:
        raise ValueError("value cannot be None")

    import re

    s = value.strip().lower()
    # Replace any sequence of non-alphanumeric characters with underscore
    s = re.sub(r"[^a-z0-9]+", "_", s)
    # Collapse multiple underscores into one
    s = re.sub(r"_+", "_", s)
    # Trim leading/trailing underscores
    s = s.strip("_")
    return s
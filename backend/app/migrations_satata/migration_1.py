from sqlalchemy.orm import Session

import activities.activity.utils as activity_utils
import activities.activity_types.models as activity_types_models
import activities.activity_types.crud as activity_types_crud
import migrations_satata.crud as migrations_crud

import core.logger as core_logger


def process_migration_1(db: Session):
    """
    Insert canonical activity types from activity utils.

    Args:
        db: Database session.

    Returns:
        None.

    Raises:
        None. Errors are logged and the migration is not marked
        executed if failures occur.
    """
    core_logger.print_to_log_and_console("Started migration s1")

    processed_ok = True

    try:
        # Iterate the mapping of id -> display name from utils
        for type_id, type_name in activity_utils.ACTIVITY_ID_TO_NAME.items():
            try:
                # Skip if an entry with this id already exists
                existing_by_id = activity_types_crud.get_type_by_id(type_id, db)
                if existing_by_id:
                    core_logger.print_to_log_and_console(
                        f"Migration s1 - Activity type {type_id} already "
                        f"exists. Skipping.")
                    continue

                # Skip if an entry with the same name exists
                existing_by_name = (
                    db.query(activity_types_models.ActivityTypes)
                    .filter(
                        activity_types_models.ActivityTypes.name == type_name
                    )
                    .first()
                )
                if existing_by_name:
                    core_logger.print_to_log_and_console(
                        f"Migration s1 - Activity type name '{type_name}' "
                        f"already exists. Skipping.")
                    continue

                # Create new activity type with explicit id, name and display
                new_type = activity_types_models.ActivityTypes(
                    id=type_id,
                    name=type_name,
                    display_name=normal_to_snake_case(type_name),
                )
                db.add(new_type)
            except Exception as inner_err:
                processed_ok = False
                core_logger.print_to_log_and_console(
                    f"Migration s1 - Failed to insert type {type_id}: "
                    f"{inner_err}",
                    "error",
                    exc=inner_err,
                )
        # Commit all inserts at once
        db.commit()
    except Exception as err:
        db.rollback()
        processed_ok = False
        core_logger.print_to_log_and_console(
            f"Migration s1 - Error processing activity types: {err}",
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
            "Migration s1 failed to process all activity types. "
            "Will try again later.",
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
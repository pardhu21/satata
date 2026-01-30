from sqlalchemy.orm import Session

import activities.activity_categories.utils as activity_category_utils
import activities.activity_categories.models as activity_categories_models
import migrations_satata.crud as migrations_crud

import core.logger as core_logger


def process_migration_2(db: Session):
    """
    Insert canonical activity categories into
    activity_categories table.

    Args:
        db: Database session.

    Returns:
        None. Logs errors and marks migration executed on
        success.
    """
    core_logger.print_to_log_and_console(
        "Started migration_satata 2 - seed activity categories"
    )

    processed_ok = True

    try:
        for cat_id, (name, display_name) in (
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
                        f"Migration satata_2 - Category id {cat_id} "
                        "already exists. Skipping."
                    )
                    continue

                # Skip if an entry with the same name exists
                existing_by_name = (
                    db.query(activity_categories_models.ActivityCategories)
                    .filter(
                        activity_categories_models.ActivityCategories.name == name
                    )
                    .first()
                )
                if existing_by_name:
                    core_logger.print_to_log_and_console(
                        f"Migration satata_2 - Category name '{name}' "
                        "already exists. Skipping."
                    )
                    continue

                new_cat = activity_categories_models.ActivityCategories(
                    id=cat_id,
                    name=name,
                    display_name=display_name,
                )
                db.add(new_cat)
            except Exception as inner_err:
                processed_ok = False
                core_logger.print_to_log_and_console(
                    f"Migration satata_2 - Failed to insert category "
                    f"{cat_id}: {inner_err}",
                    "error",
                    exc=inner_err,
                )
        # Commit all inserts at once
        db.commit()
    except Exception as err:
        db.rollback()
        processed_ok = False
        core_logger.print_to_log_and_console(
            f"Migration satata_2 - Error processing categories: {err}",
            "error",
            exc=err,
        )

    # Mark migration as executed on success
    if processed_ok:
        try:
            migrations_crud.set_migration_as_executed(2, db)
        except Exception as err:
            core_logger.print_to_log_and_console(
                f"Migration satata_2 - Failed to set migration as executed: {err}",
                "error",
                exc=err,
            )
            return
    else:
        core_logger.print_to_log_and_console(
            "Migration satata_2 failed to process all categories. "
            "Will try again later.",
            "error",
        )

    core_logger.print_to_log_and_console("Finished migration_satata 2")

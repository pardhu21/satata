from sqlalchemy.orm import Session

import users.user_category_rules.utils as user_category_rules_utils
import users.user_category_rules.models as user_category_rules_models
import migrations_satata.crud as migrations_crud

import core.logger as core_logger

def process_migration_3(db: Session):
    """
    Seed user_category_rules table for running activity type
    using canonical mapping in users.user_category_rules.utils for
    every user in the system.
    """
    core_logger.print_to_log_and_console(
        "Started migration_satata 3 - seed user_category_rules for all users"
    )

    processed_ok = True

    try:
        # Resolve all users and apply rules to each
        try:
            from users.users import models as users_models
            users = db.query(users_models.Users).all()
        except Exception as e:
            core_logger.print_to_log_and_console(
                f"Migration satata_3 - Failed to fetch users: {e}",
                "error",
                exc=e,
            )
            return

        if not users:
            core_logger.print_to_log_and_console(
                "Migration satata_3 - No users found to assign default rules to. Aborting.",
                "error",
            )
            return

        for user in users:
            user_id = user.id
            for rule_id, rule in user_category_rules_utils.USER_CATEGORY_RULES.items():
                try:
                    # Check whether a rule matching user_id, activity_type_id and
                    # category_id already exists to avoid duplicates
                    existing = (
                        db.query(user_category_rules_models.UserCategoryRules)
                        .filter(
                            user_category_rules_models.UserCategoryRules.user_id
                            == user_id,
                            user_category_rules_models.UserCategoryRules.activity_type_id
                            == rule["activity_type_id"],
                            user_category_rules_models.UserCategoryRules.category_id
                            == rule["category_id"],
                        )
                        .first()
                    )
                    if existing:
                        core_logger.print_to_log_and_console(
                            f"Migration satata_3 - Rule for category {rule['category_id']} already exists for user {user_id}. Skipping."
                        )
                        continue

                    new_rule = user_category_rules_models.UserCategoryRules(
                        user_id=user_id,
                        activity_type_id=rule["activity_type_id"],
                        category_id=rule["category_id"],
                        min_distance=rule.get("min_distance"),
                        max_distance=rule.get("max_distance"),
                        min_hr=rule.get("min_hr"),
                        max_hr=rule.get("max_hr"),
                        min_elevation_gain=rule.get("min_elevation_gain"),
                        max_elevation_gain=rule.get("max_elevation_gain"),
                    )
                    db.add(new_rule)
                except Exception as inner_err:
                    processed_ok = False
                    core_logger.print_to_log_and_console(
                        f"Migration satata_3 - Failed to insert rule {rule_id} for user {user_id}: {inner_err}",
                        "error",
                        exc=inner_err,
                    )
        db.commit()
    except Exception as err:
        db.rollback()
        processed_ok = False
        core_logger.print_to_log_and_console(
            f"Migration satata_3 - Error processing rules: {err}",
            "error",
            exc=err,
        )

    if processed_ok:
        try:
            migrations_crud.set_migration_as_executed(3, db)
        except Exception as err:
            core_logger.print_to_log_and_console(
                f"Migration satata_3 - Failed to set migration as executed: {err}",
                "error",
                exc=err,
            )
            return
    else:
        core_logger.print_to_log_and_console(
            "Migration satata_3 failed to process all rules. Will try again later.",
            "error",
        )

    core_logger.print_to_log_and_console("Finished migration_satata 3")

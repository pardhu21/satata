import users.user_category_rules.models as models
import users.user_category_rules.schema as schema
import users.user_activity_stats.crud as stats_crud

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import core.logger as core_logger


def get_all_rules(db: Session):
    try:
        rules = db.query(models.UserCategoryRules).all()
        return rules if rules else None
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_all_rules: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_rule_by_id(rule_id: int, db: Session):
    try:
        return (
            db.query(models.UserCategoryRules)
            .filter(models.UserCategoryRules.id == rule_id)
            .first()
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_rule_by_id: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_rule(rule_in: schema.UserCategoryRuleCreate, db: Session):
    try:
        db_obj = models.UserCategoryRules(
            user_id=rule_in.user_id,
            activity_type_id=rule_in.activity_type_id,
            category_id=rule_in.category_id,
            min_distance=rule_in.min_distance,
            max_distance=rule_in.max_distance,
            min_hr=rule_in.min_hr,
            max_hr=rule_in.max_hr,
            min_elevation_gain=rule_in.min_elevation_gain,
            max_elevation_gain=rule_in.max_elevation_gain,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        # Optionally refresh related stats
        try:
            stats_crud.create_stats(
                schema.UserActivityStatsCreate(
                    activity_type_id=rule_in.activity_type_id,
                    user_category_id=db_obj.id,
                ),
                db,
            )
        except Exception:
            # non-critical
            pass
        return db_obj
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in create_rule: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def edit_rule(rule_id: int, rule_edit: schema.UserCategoryRuleEdit, token_user_id: int, db: Session):
    try:
        db_obj = get_rule_by_id(rule_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User category rule not found",
            )
        if db_obj.user_id != token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this rule",
            )
        for field in [
            "min_distance",
            "max_distance",
            "min_hr",
            "max_hr",
            "min_elevation_gain",
            "max_elevation_gain",
        ]:
            val = getattr(rule_edit, field)
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
            f"Error in edit_rule: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def delete_rule(rule_id: int, token_user_id: int, db: Session):
    try:
        db_obj = get_rule_by_id(rule_id, db)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User category rule not found",
            )
        if db_obj.user_id != token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this rule",
            )
        db.delete(db_obj)
        db.commit()
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in delete_rule: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err

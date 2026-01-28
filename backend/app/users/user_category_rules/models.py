from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)
from core.database import Base
from sqlalchemy.sql import func


class UserCategoryRules(Base):
    __tablename__ = "user_category_rules"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="User category rule ID",
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID this rule belongs to",
    )

    activity_type_id = Column(
        Integer,
        ForeignKey("activity_types.id"),
        nullable=False,
        index=True,
        comment="Activity type ID",
    )

    category_id = Column(
        Integer,
        ForeignKey("activity_categories.id"),
        nullable=False,
        index=True,
        comment="Activity category ID",
    )

    min_distance = Column(
        Float,
        nullable=True,
        comment="Minimum distance in meters",
    )

    max_distance = Column(
        Float,
        nullable=True,
        comment="Maximum distance in meters",
    )

    min_hr = Column(
        Float,
        nullable=True,
        comment="Minimum average heart rate",
    )

    max_hr = Column(
        Float,
        nullable=True,
        comment="Maximum average heart rate",
    )

    min_elevation_gain = Column(
        Float,
        nullable=True,
        comment="Minimum elevation gain in meters",
    )

    max_elevation_gain = Column(
        Float,
        nullable=True,
        comment="Maximum elevation gain in meters",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Rule creation timestamp",
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Rule last update timestamp",
    )
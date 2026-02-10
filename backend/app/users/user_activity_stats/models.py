from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from core.database import Base


class UserActivityStats(Base):
    __tablename__ = "user_activity_stats"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="User activity statistics ID",
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID that this delta record belongs to",
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
        ForeignKey("activity_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Activity category ID used as baseline",
    )

    avg_distance = Column(
        Float,
        nullable=True,
        comment="Average distance in meters",
    )

    m2_distance = Column(
        Float,
        nullable=True,
        comment="Welford M2 value for distance variance",
    )

    avg_heart_rate = Column(
        Float,
        nullable=True,
        comment="Average heart rate",
    )

    m2_heart_rate = Column(
        Float,
        nullable=True,
        comment="Welford M2 value for heart rate variance",
    )

    avg_pace = Column(
        Float,
        nullable=True,
        comment="Average pace in seconds per kilometer",
    )

    m2_pace = Column(
        Float,
        nullable=True,
        comment="Welford M2 value for pace variance",
    )

    avg_duration = Column(
        Float,
        nullable=True,
        comment="Average moving time in seconds",
    )

    m2_duration = Column(
        Float,
        nullable=True,
        comment="Welford M2 value for moving time variance",
    )

    avg_elevation_gain = Column(
        Float,
        nullable=True,
        comment="Average elevation gain in meters",
    )

    m2_elevation_gain = Column(
        Float,
        nullable=True,
        comment="Welford M2 value for elevation gain variance",
    )

    avg_elevation_loss = Column(
        Float,
        nullable=True,
        comment="Average elevation loss in meters",
    )

    m2_elevation_loss = Column(
        Float,
        nullable=True,
        comment="Welford M2 value for elevation loss variance",
    )

    total_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of activities in this category",
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last statistics update timestamp",
    )

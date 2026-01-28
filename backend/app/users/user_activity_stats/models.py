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

    activity_type_id = Column(
        Integer,
        ForeignKey("activity_types.id"),
        nullable=False,
        index=True,
        comment="Activity type ID",
    )

    user_category_id = Column(
        Integer,
        ForeignKey("user_category_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User category rule ID",
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

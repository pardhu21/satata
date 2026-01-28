from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from core.database import Base


class ActivityDeltaRecords(Base):
    __tablename__ = "activity_delta_records"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Activity delta record ID",
    )

    activity_id = Column(
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Activity ID this delta record belongs to",
    )

    user_category_id = Column(
        Integer,
        ForeignKey("user_category_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User category rule ID used as baseline",
    )

    delta_distance = Column(
        Float,
        nullable=True,
        comment="Delta distance in meters compared to baseline average",
    )

    delta_distance_pct = Column(
        Float,
        nullable=True,
        comment="Delta distance percentage compared to baseline average",
    )

    delta_hr = Column(
        Float,
        nullable=True,
        comment="Delta average heart rate compared to baseline",
    )

    delta_hr_pct = Column(
        Float,
        nullable=True,
        comment="Delta heart rate percentage compared to baseline",
    )

    delta_elevation_gain = Column(
        Float,
        nullable=True,
        comment="Delta elevation gain compared to baseline",
    )

    delta_elevation_gain_pct = Column(
        Float,
        nullable=True,
        comment="Delta elevation gain percentage compared to baseline",
    )

    delta_elevation_loss = Column(
        Float,
        nullable=True,
        comment="Delta elevation loss compared to baseline",
    )

    delta_elevation_loss_pct = Column(
        Float,
        nullable=True,
        comment="Delta elevation loss percentage compared to baseline",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Delta record creation timestamp",
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Delta record last update timestamp",
    )
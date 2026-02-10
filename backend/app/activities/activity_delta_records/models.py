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

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID that this delta record belongs to",
    )

    activity_id = Column(
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Activity ID this delta record belongs to",
    )

    activity_type_id = Column(
        Integer,
        ForeignKey("activity_types.id", ondelete="SET NULL"),
        nullable=True,
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

    delta_avg_pace = Column(
        Float,
        nullable=True,
        comment="Delta average pace (seconds per km) compared to baseline",
    )

    delta_avg_pace_pct = Column(
        Float,
        nullable=True,
        comment="Delta average pace percentage compared to baseline",
    )

    delta_duration = Column(
        Float,
        nullable=True,
        comment="Delta moving time in seconds compared to baseline",
    )

    delta_duration_pct = Column(
        Float,
        nullable=True,
        comment="Delta moving time percentage compared to baseline",
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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_id": self.activity_id,
            "activity_type_id": self.activity_type_id,
            "category_id": self.category_id,
            "delta_distance": self.delta_distance,
            "delta_distance_pct": self.delta_distance_pct,
            "delta_hr": self.delta_hr,
            "delta_hr_pct": self.delta_hr_pct,
            "delta_avg_pace": self.delta_avg_pace,
            "delta_avg_pace_pct": self.delta_avg_pace_pct,
            "delta_duration": self.delta_duration,
            "delta_duration_pct": self.delta_duration_pct,
            "delta_elevation_gain": self.delta_elevation_gain,
            "delta_elevation_gain_pct": self.delta_elevation_gain_pct,
            "delta_elevation_loss": self.delta_elevation_loss,
            "delta_elevation_loss_pct": self.delta_elevation_loss_pct,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
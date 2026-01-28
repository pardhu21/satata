from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from core.database import Base


class ActivityAIInsights(Base):
    __tablename__ = "activity_ai_insights"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="AI insight record ID",
    )

    activity_id = Column(
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Activity ID this AI insight belongs to",
    )

    insight_text = Column(
        Text,
        nullable=True,
        comment="Generated AI insight text for the activity",
    )

    model_used = Column(
        String(length=250),
        nullable=True,
        comment="LLM model used to generate the insight",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Insight creation timestamp",
    )

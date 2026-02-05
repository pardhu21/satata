from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
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

    values = Column(
        JSONB,
        nullable=False,
        comment="JSON object defining the rule values",
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
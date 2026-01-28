from sqlalchemy import (
    Column,
    Integer,
    String,
)
from core.database import Base


class ActivityCategories(Base):
    __tablename__ = "activity_categories"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Activity category ID",
    )

    name = Column(
        String(length=250),
        nullable=False,
        unique=True,
        index=True,
        comment="Internal activity category name (e.g. easy, tempo, long)",
    )

    display_name = Column(
        String(length=250),
        nullable=False,
        comment="User-facing activity category name (e.g. Easy, Tempo, Long)",
    )

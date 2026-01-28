from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from core.database import Base


class ActivityTypes(Base):
    __tablename__ = "activity_types"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Activity type ID",
    )

    name = Column(
        String(length=250),
        nullable=False,
        unique=True,
        index=True,
        comment="Internal activity type name (e.g. run, ride, swim)",
    )

    display_name = Column(
        String(length=250),
        nullable=False,
        comment="User-facing activity type name (e.g. Run, Ride, Swim)",
    )

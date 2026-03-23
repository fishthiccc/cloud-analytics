print("Loading town model")
from sqlalchemy import Integer, Float,String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.database import Base


class Town(Base):
    __tablename__ = "towns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationship
    observations: Mapped[list["WeatherObservation"]] = relationship(
        "WeatherObservation",
        back_populates="town",
        cascade="all, delete-orphan"
    )

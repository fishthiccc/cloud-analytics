print("Loading weather_observation model...")
from sqlalchemy import Integer, Float,String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.database import Base
from app.models.town import Town
print("Existing tables BEFORE definition:", Base.metadata.tables.keys())


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id: Mapped[int] = mapped_column(primary_key=True)

    town_id: Mapped[int] = mapped_column(
        ForeignKey("towns.id"),
        index=True
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        index=True
    )

    temperature: Mapped[float] = mapped_column(Float)
    feels_like: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pressure: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_direction: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cloud_coverage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rainfall: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationship
    town: Mapped["Town"] = relationship("Town", back_populates="observations")

    # Constraints + indexes
    __table_args__ = (
        UniqueConstraint("town_id", "timestamp", name="uq_town_timestamp"),
        Index("idx_town_timestamp", "town_id", "timestamp"),
        {"extend_existing": True}
    )
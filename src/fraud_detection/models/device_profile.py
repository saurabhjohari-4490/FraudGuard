"""Device profile model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from fraud_detection.models.base import Base, UUIDMixin


class DeviceProfile(UUIDMixin, Base):
    __tablename__ = "device_profiles"

    fingerprint: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    user_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    os: Mapped[str | None] = mapped_column(String(64))
    browser: Mapped[str | None] = mapped_column(String(64))
    screen_resolution: Mapped[str | None] = mapped_column(String(16))
    timezone: Mapped[str | None] = mapped_column(String(64))
    language: Mapped[str | None] = mapped_column(String(16))
    is_emulator: Mapped[bool] = mapped_column(Boolean, default=False)
    is_rooted: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    extra_data: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

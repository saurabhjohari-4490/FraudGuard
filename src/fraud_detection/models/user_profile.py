"""User profile model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from fraud_detection.models.base import Base, UUIDMixin


class UserProfile(UUIDMixin, Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    avg_transaction_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    typical_merchants: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    typical_geo_regions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    risk_level: Mapped[str] = mapped_column(String(16), default="low")
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    extra_data: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

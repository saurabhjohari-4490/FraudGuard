"""Transaction model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from fraud_detection.models.base import Base, UUIDMixin


class Transaction(UUIDMixin, Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    merchant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    card_bin: Mapped[str | None] = mapped_column(String(6))
    device_fingerprint: Mapped[str | None] = mapped_column(String(128))
    ip_address: Mapped[str | None] = mapped_column(INET)
    geo_lat: Mapped[float | None] = mapped_column()
    geo_lon: Mapped[float | None] = mapped_column()
    channel: Mapped[str | None] = mapped_column(String(32))
    extra_data: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_transactions_created_at", "created_at"),
    )

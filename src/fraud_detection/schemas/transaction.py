"""Transaction Pydantic schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    """Request schema for creating a transaction."""

    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., min_length=1, max_length=64)
    merchant_id: str = Field(..., min_length=1, max_length=64)
    amount: Decimal = Field(..., gt=0, le=Decimal("9999999999.99"))
    currency: str = Field(default="INR", pattern=r"^[A-Z]{3}$")
    card_bin: str | None = Field(None, pattern=r"^\d{6}$")
    device_fingerprint: str | None = Field(None, max_length=128)
    ip_address: str | None = None
    geo_lat: float | None = Field(None, ge=-90, le=90)
    geo_lon: float | None = Field(None, ge=-180, le=180)
    channel: str | None = Field(None, max_length=32)
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TransactionResponse(BaseModel):
    """Response after transaction ingestion and scoring."""

    transaction_id: str
    risk_score: float
    decision: str
    risk_level: str  # critical, high, medium, low
    signals: list[str]
    explanation: str
    processing_time_ms: float

    model_config = {"from_attributes": True}


class TransactionDetail(BaseModel):
    """Full transaction detail response."""

    transaction_id: str
    user_id: str
    merchant_id: str
    amount: float
    currency: str
    device_fingerprint: str | None
    ip_address: str | None
    geo_lat: float | None
    geo_lon: float | None
    channel: str | None
    created_at: datetime
    risk_score: float | None = None
    decision: str | None = None

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    """Paginated transaction list."""

    transactions: list[TransactionDetail]
    total: int
    page: int
    page_size: int

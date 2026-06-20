"""Base scoring module and result types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from fraud_detection.services.enrichment import EnrichedContext


@dataclass
class ScoringResult:
    """Result from a single scoring module."""

    score: float  # 0-100 normalized
    confidence: float  # 0.0-1.0
    signals: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.score = max(0.0, min(100.0, self.score))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class TransactionContext:
    """Full context for scoring a transaction."""

    # Transaction data
    transaction_id: str
    user_id: str
    merchant_id: str
    amount: Decimal
    currency: str
    card_bin: str | None
    device_fingerprint: str | None
    ip_address: str | None
    geo_lat: float | None
    geo_lon: float | None
    channel: str | None
    timestamp: datetime
    metadata: dict

    # Enriched features
    enrichment: EnrichedContext


class ScoringModule(ABC):
    """Abstract base class for fraud scoring modules."""

    name: str
    weight: float
    description: str

    @abstractmethod
    async def score(self, context: TransactionContext) -> ScoringResult:
        """Compute a fraud risk score for the given transaction context.

        Returns a ScoringResult with score 0-100.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} weight={self.weight}>"

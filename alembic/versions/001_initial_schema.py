"""Initial schema - transactions, fraud_decisions, user_profiles, device_profiles.

Revision ID: 001
Revises: None
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Transactions table
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transaction_id", sa.String(64), unique=True, nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("merchant_id", sa.String(64), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("card_bin", sa.String(6)),
        sa.Column("device_fingerprint", sa.String(128)),
        sa.Column("ip_address", postgresql.INET),
        sa.Column("geo_lat", sa.Float),
        sa.Column("geo_lon", sa.Float),
        sa.Column("channel", sa.String(32)),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_transactions_user_id", "transactions", ["user_id"])
    op.create_index("idx_transactions_merchant_id", "transactions", ["merchant_id"])
    op.create_index("idx_transactions_created_at", "transactions", ["created_at"])

    # Fraud decisions table
    op.create_table(
        "fraud_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "transaction_id",
            sa.String(64),
            sa.ForeignKey("transactions.transaction_id"),
            nullable=False,
        ),
        sa.Column("risk_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("decision", sa.String(16), nullable=False),
        sa.Column("sub_scores", postgresql.JSONB, nullable=False),
        sa.Column("signals", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("explanation", sa.Text),
        sa.Column("analyst_action", sa.String(16)),
        sa.Column("analyst_notes", sa.Text),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_fraud_decisions_decision", "fraud_decisions", ["decision"])
    op.create_index("idx_fraud_decisions_risk_score", "fraud_decisions", ["risk_score"])

    # User profiles table
    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(64), unique=True, nullable=False),
        sa.Column("avg_transaction_amount", sa.Numeric(12, 2)),
        sa.Column("transaction_count", sa.Integer, server_default="0"),
        sa.Column("typical_merchants", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("typical_geo_regions", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("risk_level", sa.String(16), server_default="low"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True)),
        sa.Column("last_active_at", sa.DateTime(timezone=True)),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Device profiles table
    op.create_table(
        "device_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("fingerprint", sa.String(128), unique=True, nullable=False),
        sa.Column("user_ids", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("os", sa.String(64)),
        sa.Column("browser", sa.String(64)),
        sa.Column("screen_resolution", sa.String(16)),
        sa.Column("timezone", sa.String(64)),
        sa.Column("language", sa.String(16)),
        sa.Column("is_emulator", sa.Boolean, server_default="false"),
        sa.Column("is_rooted", sa.Boolean, server_default="false"),
        sa.Column("risk_score", sa.Numeric(5, 2), server_default="0"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True)),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_table("device_profiles")
    op.drop_table("user_profiles")
    op.drop_table("fraud_decisions")
    op.drop_table("transactions")

# FraudGuard - AI-Powered Real-Time Fraud Detection Platform

A production-grade fraud detection system that scores financial transactions in real-time using 6 parallel risk assessment modules, renders transparent decisions with full explainability, and provides an analyst dashboard for manual review.

## System Overview

```
Transaction (INR 50,000)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  ENRICHMENT (50ms cap)                                       │
│  Redis parallel lookups: velocity + user profile + device    │
└───────────────────────────────┬─────────────────────────────┘
                                │
    ┌───────────┬───────────┬───┼───┬───────────┬─────────────┐
    ▼           ▼           ▼   ▼   ▼           ▼             │
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Behavior│ │Velocity│ │ Device │ │Merchant│ │  Geo   │ │IP Intel│
│  25%   │ │  20%   │ │  20%   │ │  15%   │ │  10%   │ │  10%   │
│score:95│ │score:35│ │score:20│ │score:45│ │score: 0│ │score:30│
└────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘
     └──────────┴──────────┴─────┬────┴──────────┴──────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│  AGGREGATION                                                 │
│  Weighted sum → Critical boost → Multi-module amplifier      │
│  Base: 43.25 → Boosted: 54 → Amplified (5 active): 86.4    │
└───────────────────────────────┬─────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│  DECISION ENGINE                                             │
│  Score 86.4 → ESCALATE (Critical Risk)                       │
│  → Alert created for analyst review                          │
└─────────────────────────────────────────────────────────────┘
```

**Processing time: < 100ms end-to-end (typically 2-5ms)**

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **No auto-block** | System never rejects transactions automatically. All blocking is a manual analyst decision. Zero false-positive rejections. |
| **Three-tier decisions** | Approve (0-30) / Verify (31-60) / Escalate (61-100). Simple, auditable, no gray zones. |
| **Parallel scoring** | All 6 modules run concurrently via `asyncio.gather`. One slow module doesn't block others. |
| **Approve-only profile updates** | Fraudulent transactions never pollute the user's behavioral baseline. A single large fraud won't shift the average. |
| **Critical signal boost** | Prevents extreme signals from being diluted by the weighted average. Single module at 90+ guarantees at least VERIFY. |
| **Multi-module amplifier** | Broad coverage across 4-5 modules triggers escalation even with moderate individual scores. |
| **Graceful degradation** | Redis down? Scoring continues with neutral defaults. Module failure? Returns score 50, zero confidence. |

## Decision Thresholds

| Score | Decision | Risk Level | What Happens |
|-------|----------|------------|--------------|
| 0-30 | APPROVE | Low | Transaction passes, user profile updated |
| 31-60 | VERIFY | Medium | Step-up auth requested, alert queued |
| 61-80 | ESCALATE | High | Alert queued for analyst review |
| 81-100 | ESCALATE | Critical | High-priority alert, immediate analyst attention |

Analyst can then: **Approve** (false positive) | **Escalate** (route to senior) | **Block** (confirm fraud)

## Scoring Modules

### 1. Behavior Analyzer (25%)

Compares current transaction against user's historical spending baseline.

| Signal | Score | Trigger |
|--------|-------|---------|
| Amount 50x+ above average | +80 | Extreme anomaly |
| Amount 10x-50x above average | +60 | Major spike |
| Amount 5x-10x above average | +40 | Notable increase |
| Amount 3x-5x above average | +20 | Mild deviation |
| First-time user | +10 | No history to compare |
| New merchant | +15 | Never seen this merchant |
| Unusual hours (1-5 AM) | +20 | Off-pattern timing |
| Late night (22:00-01:00) | +10 | Slightly unusual |
| Large round amount (>=10K, divisible by 1000) | +10 | Test transaction pattern |

Confidence: 0.3 (first transaction) → scales linearly to 1.0 at 20+ transactions.

### 2. Velocity Detector (20%)

Detects burst patterns indicating card testing or automated attacks.

| Window | Threshold | Max Score | Pattern |
|--------|-----------|-----------|---------|
| 1 minute | >= 3 txns | up to 70 | Rapid-fire attack |
| 5 minutes | >= 8 txns | up to 50 | Sustained burst |
| 1 hour | >= 20 txns | +20 | High-frequency abuse |
| 24 hours | >= 50 txns | +15 | Volume fraud |
| Acceleration | 5m rate > 3x hourly avg | +15 | Sudden rate change |

Scoring formula (1m): `min(70, (count - 3 + 1) * 20)` — scales with severity.

### 3. Device Risk Engine (20%)

Identifies compromised or suspicious devices.

| Signal | Score | Description |
|--------|-------|-------------|
| Emulator/VM | +40 | Virtual device |
| Rooted/jailbroken | +30 | Security bypassed |
| New device (< 5 min) | +25 | Just provisioned |
| First time seen | +20 | No history |
| Shared (3+ users) | +25 | Multi-account device |
| Shared (2 users) | +10 | Possibly shared |
| Emulator + rooted combo | +15 | Extra dangerous |
| Recently registered (< 1hr) | +10 | Very new |
| No fingerprint | +15 | Cannot identify |

### 4. Merchant Risk Engine (15%)

Evaluates merchant category and context.

| Category | Base Score | Additional Signals |
|----------|-----------|-------------------|
| Gambling | +30 | Suspicious name (test_/demo_/temp_): +20 |
| Crypto | +25 | New merchant for user: +10 |
| Adult | +20 | Large amount at high-risk (>50K): +15 |
| Digital Goods | +15 | Cross-border: +10 |
| Travel | +10 | |
| Electronics | +10 | |

### 5. Geolocation Engine (10%)

Detects physically impossible travel using Haversine distance.

| Signal | Score | Example |
|--------|-------|---------|
| > 900 km/h travel | +60 | Delhi to London in 30 min |
| > 500 km/h travel | +30 | Faster than airline |
| > 1000 km displacement | +15 | Large geographic shift |
| New region for user | +25 | Never transacted here |
| High-risk region | +20 | Flagged geography |

### 6. IP Intelligence (10%)

Identifies anonymizing networks and suspicious origins.

| Signal | Score | Description |
|--------|-------|-------------|
| TOR exit node | +45 | Maximum anonymity |
| Loopback (127.x) | +40 | Invalid in production |
| Private IP | +30 | Should not originate payments |
| VPN | +25 | Connection hiding |
| Proxy | +20 | IP masking |
| Datacenter/cloud IP | +20 | Non-residential |
| Multiple indicators | +15 | Compound risk |
| IP/geo mismatch | +15 | Location inconsistency |
| Invalid IP format | +10 | Malformed address |

## Risk Aggregation

### Formula

```
Base Score = Σ(module_score × module_weight)

Critical Signal Boost:
  if max(module_scores) >= 80:
    total = max(base, max_score × 0.6)

Multi-Module Amplifier:
  active_count = count(modules where score >= 20)
  if active >= 5: total × 1.6
  if active >= 4: total × 1.4
  if active >= 3: total × 1.2

Final Score = clamp(total, 0, 100)
```

### Why Two Boosts?

- **Critical boost** prevents one extreme signal from being averaged away (e.g., Behavior=90 alone would only give 22.5 weighted)
- **Multi-module amplifier** catches broad fraud that triggers many moderate signals (individual scores 20-60 range)

## User Risk Levels

Computed from **average risk score** across non-approved transactions:

| Avg Score | Level | Meaning |
|-----------|-------|---------|
| > 80 | Critical | Consistently triggers critical alerts |
| > 60 | High | Frequent escalations |
| > 30 | Medium | Occasional verifications |
| <= 30 | Low | Clean transaction history |

## Analyst Workflow

```
Transaction scored → decision assigned
    │
    ├── APPROVE → passes through, profile updated
    │
    └── VERIFY/ESCALATE → alert created
            │
            ├── Analyst clicks "Approve" → decision = approve
            ├── Analyst clicks "Escalate" → routed to senior
            └── Analyst clicks "Block" → decision = block (ONLY way to reject)
```

**Alert queue filters:** All | Critical (score >80) | Escalated (61-80) | Verify (31-60) | Blocked (analyst-blocked)

## Dashboard Pages

| Page | Path | Features |
|------|------|----------|
| **Dashboard** | `/` | 8 metric cards with drill-down, score distribution chart, decision pie chart, top risky users, recent high-risk txns |
| **Alerts** | `/alerts` | Filterable queue, risk breakdown panel, per-module bar charts, fraud signals, AI explanation, analyst actions |
| **Transactions** | `/transactions` | Search by ID/user/merchant, 10 recent on load, detail panel with full scoring |
| **Users** | `/users` | User list with risk badges, click for full risk profile |
| **User Profile** | `/users/:id` | Transaction history, risk timeline, merchant patterns, decision distribution |

## Architecture

| Component | Technology | Port |
|-----------|-----------|------|
| API Server | Python 3.12, FastAPI (async) | 8001 |
| Dashboard | React 18, TypeScript, TailwindCSS, Vite | 3001 |
| Database | PostgreSQL 16, SQLAlchemy 2.0 async | 5433 |
| Cache | Redis 7 (sorted sets + hashes) | 6380 |
| Mock Generator | Python (seed-based, 10 TPS) | — |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/transactions` | Score a transaction (returns risk_score, decision, signals) |
| `GET` | `/api/v1/transactions` | List/search transactions |
| `GET` | `/api/v1/alerts` | Alert queue (filter: critical/escalate/verify/block) |
| `PATCH` | `/api/v1/alerts/{id}` | Analyst action (approve/escalate/block) |
| `GET` | `/api/v1/metrics` | Real-time platform metrics |
| `GET` | `/api/v1/metrics/transactions?category=X` | Drill-down by metric category |
| `GET` | `/api/v1/users` | List users with risk summaries |
| `GET` | `/api/v1/users/{id}/risk-profile` | Full user risk profile |
| `GET` | `/health` | Service health |
| `GET` | `/playground` | Interactive API testing UI |

## Performance

| Metric | Result |
|--------|--------|
| Scoring latency (p95) | ~70-86ms |
| User list endpoint | ~70ms (single aggregated query) |
| Enrichment (Redis) | < 5ms cache hits |
| Throughput | 10+ TPS sustained |
| Availability | Graceful degradation (continues if Redis down) |

## Database Schema

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `transactions` | Raw transaction data | user_id, merchant_id, amount, device, IP, geo |
| `fraud_decisions` | Scoring results | risk_score, decision, sub_scores (JSONB), signals, analyst_action |
| `user_profiles` | Aggregated user stats | avg_amount, txn_count, typical_merchants |
| `device_profiles` | Device data | fingerprint, is_emulator, is_rooted, user_ids |

## Profile Update Rules

| Component | Updated on Approve | Updated on Escalate/Verify |
|-----------|:--:|:--:|
| Velocity counters | Always | Always |
| User avg_amount | Yes | No |
| User txn_count | Yes | No |
| User typical_merchants | Yes | No |
| Device profile | Yes | No |

**Why approve-only?** If a fraudulent INR 5,000,000 transaction (on a user averaging INR 500) updated the profile, the average would jump to INR 49,995 — making future INR 50,000 fraud look "normal". By excluding non-approved transactions, the behavioral baseline stays clean.

## Fraud Patterns Detected

| Pattern | Modules Triggered |
|---------|-------------------|
| Velocity Burst (10-15 txns in 1-2 min) | Velocity + Behavior |
| Account Takeover (new device + large amount + foreign location) | Device + Geo + Behavior |
| Impossible Travel (Delhi to London in 30 min) | Geolocation + Behavior |
| Card Testing (8-15 micro-transactions from datacenter) | Velocity + IP + Merchant |
| Device Spoofing (emulator + rooted + datacenter IP) | Device + IP + Behavior |
| Amount Anomaly (10-50x user average) | Behavior + Merchant |
| Mixed Pattern (VPN + emulator + cross-border + large) | All 6 modules |

## Quick Start

See [SETUP.md](./SETUP.md) for detailed installation instructions, prerequisites, and step-by-step Docker setup.

```bash
# TL;DR (requires Docker)
git clone git@github.com:razorpay/fraudguard.git && cd fraudguard
docker compose up --build -d
# Dashboard: http://localhost:3001
# API: http://localhost:8001
# Playground: http://localhost:8001/playground

# Start mock traffic
docker compose --profile mock up -d mock-gen
```

## Documentation

| Document | Contents |
|----------|----------|
| [SETUP.md](./SETUP.md) | Prerequisites, installation, Docker setup, troubleshooting |
| [docs/problem_statement.md](./docs/problem_statement.md) | Full problem statement, scoring module details, risk aggregation math |
| [docs/implementation_details.md](./docs/implementation_details.md) | Code architecture, optimizations, error handling, DB schema |

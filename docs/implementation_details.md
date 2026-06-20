# Implementation Details

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend | Python | 3.12 | Application runtime |
| API Framework | FastAPI | 0.115+ | Async HTTP endpoints |
| ORM | SQLAlchemy | 2.0 (async) | Database operations |
| Database | PostgreSQL | 16 | Persistent storage |
| Cache | Redis | 7 | Velocity counters, profile caching |
| Migrations | Alembic | 1.14+ | Schema versioning |
| Frontend | React | 18 | Dashboard UI |
| Build Tool | Vite | 5+ | Frontend bundler with HMR |
| Styling | TailwindCSS | 3 | Utility-first CSS |
| Charts | Recharts | 2 | Data visualization |
| HTTP Client | Axios | 1.7+ | Frontend API calls |
| Containerization | Docker Compose | v2 | Multi-service orchestration |

---

## System Architecture

```
                                    +------------------+
                                    |   React Dashboard |
                                    |   (Vite, port 3001)|
                                    +--------+---------+
                                             |
                                             | HTTP (REST API)
                                             v
+----------------+          +--------------------------------+
|                |  POST    |         FastAPI Server          |
|  Transaction   +--------->+         (port 8001)            |
|  Source        |          |                                |
|  (Mock Gen)    |          |  +---------------------------+ |
+----------------+          |  |    Transaction Endpoint    | |
                            |  +---------------------------+ |
                            |              |                  |
                            |              v                  |
                            |  +---------------------------+ |
                            |  |   Enrichment Service      | |
                            |  |   (50ms timeout)          | |
                            |  +--+--------+--------+---+  | |
                            |     |        |        |      | |
                            |     v        v        v      | |
                            |  Velocity  User     Device   | |
                            |  (Redis)  Profile   Profile  | |
                            |            (Redis)  (Redis)  | |
                            |              |                | |
                            |              v                | |
                            |  +---------------------------+| |
                            |  |   Scoring Pipeline        || |
                            |  |   (6 modules parallel)    || |
                            |  +---------------------------+| |
                            |              |                 | |
                            |              v                 | |
                            |  +---------------------------+| |
                            |  |   Risk Aggregator         || |
                            |  |   (Weighted + Boost)      || |
                            |  +---------------------------+| |
                            |              |                 | |
                            |              v                 | |
                            |  +---------------------------+| |
                            |  |   Decision Engine         || |
                            |  |   (Threshold mapping)     || |
                            |  +---------------------------+| |
                            |              |                 | |
                            |              v                 | |
                            |  +---------------------------+| |
                            |  |   PostgreSQL              || |
                            |  |   (Persist decision)      || |
                            |  +---------------------------+| |
                            +--------------------------------+
```

---

## Project Structure

```
bee/
├── pyproject.toml                    # Python dependencies & tool config
├── Dockerfile                        # Backend container
├── Dockerfile.dashboard              # Frontend production build
├── docker-compose.yml                # 5-service orchestration
├── alembic.ini                       # Migration config
├── .env.example                      # Environment template
├── alembic/
│   ├── env.py                        # Async migration env
│   └── versions/
│       └── 001_initial_schema.py     # 4-table schema
├── src/fraud_detection/
│   ├── main.py                       # FastAPI app factory + lifespan
│   ├── config.py                     # Pydantic Settings (env-based)
│   ├── middleware/
│   │   ├── correlation.py            # X-Request-ID propagation
│   │   ├── logging.py               # Structured JSON logging
│   │   └── timing.py                # X-Process-Time header
│   ├── db/
│   │   ├── engine.py                 # Async SQLAlchemy engine
│   │   ├── session.py               # Session dependency injection
│   │   └── migrate.py               # Auto-migration on startup
│   ├── cache/
│   │   ├── pool.py                   # Redis connection pool
│   │   ├── velocity.py              # Sorted set velocity counters
│   │   ├── user_profile.py          # User profile hash cache
│   │   └── device_profile.py        # Device profile hash cache
│   ├── models/
│   │   ├── base.py                   # SQLAlchemy declarative base + mixins
│   │   ├── transaction.py           # Transactions table
│   │   ├── fraud_decision.py        # Fraud decisions table
│   │   ├── user_profile.py          # User profiles table
│   │   └── device_profile.py        # Device profiles table
│   ├── schemas/
│   │   ├── transaction.py           # Pydantic request/response models
│   │   ├── fraud_decision.py        # Decision schemas
│   │   ├── metrics.py               # Metrics response schema
│   │   └── alert.py                 # Alert list/update schemas
│   ├── api/
│   │   ├── router.py                # Top-level router aggregation
│   │   └── v1/
│   │       ├── transactions.py      # POST + GET /api/v1/transactions
│   │       ├── fraud.py             # GET /api/v1/fraud/{txn_id}
│   │       ├── alerts.py            # GET + PATCH /api/v1/alerts
│   │       ├── users.py             # GET /api/v1/users/{id}/risk-profile
│   │       ├── metrics.py           # GET /api/v1/metrics + /transactions
│   │       └── health.py            # /health, /ready
│   ├── services/
│   │   ├── enrichment.py            # Parallel Redis lookups (50ms timeout)
│   │   ├── scoring_pipeline.py      # Module registry + asyncio.gather
│   │   ├── risk_aggregator.py       # Weighted aggregation + critical signal boost + multi-module amplifier
│   │   ├── decision_engine.py       # Score → decision mapping
│   │   └── explainability.py        # Template-based explanations
│   ├── scoring/
│   │   ├── base.py                  # ScoringModule ABC + ScoringResult
│   │   ├── behavior.py             # Spending anomaly detection (25%)
│   │   ├── velocity.py             # Burst detection (20%)
│   │   ├── device.py               # Device risk assessment (20%)
│   │   ├── merchant.py             # Category risk scoring (15%)
│   │   ├── geolocation.py          # Impossible travel (10%)
│   │   └── ip_intelligence.py      # VPN/TOR/proxy detection (10%)
│   └── mock/
│       ├── runner.py                # Mock traffic entry point
│       ├── users.py                 # 1000 user profile generator
│       ├── merchants.py            # 500 merchant generator
│       ├── transactions.py         # Configurable TPS generator
│       └── fraud_patterns.py       # 7 fraud injection patterns
└── dashboard/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── main.tsx                  # React entry point
        ├── App.tsx                   # Router + layout
        ├── api/client.ts            # Axios instance
        ├── types/index.ts           # TypeScript interfaces
        ├── hooks/
        │   ├── useMetrics.ts        # Metrics polling (5s interval)
        │   ├── useAlerts.ts         # Alerts with optimistic updates
        │   └── useTransactions.ts   # Transaction search
        ├── components/
        │   ├── layout/              # AppShell, Sidebar, Header
        │   ├── metrics/             # MetricsPanel, DecisionChart, DrillDown
        │   ├── alerts/              # AlertsQueue, AlertCard, AlertDetailPanel
        │   └── transactions/        # Search, List, Detail views
        └── pages/
            ├── Dashboard.tsx         # Metrics overview + drill-down
            ├── Alerts.tsx            # Analyst alert queue
            ├── Transactions.tsx      # Transaction search & detail
            └── UserProfile.tsx       # Per-user risk view
```

---

## Database Schema

### 4 Core Tables

#### `transactions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Internal identifier |
| transaction_id | VARCHAR(64) | UNIQUE, INDEX | External transaction ID |
| user_id | VARCHAR(64) | INDEX | Payer identifier |
| merchant_id | VARCHAR(64) | INDEX | Payee identifier |
| amount | DECIMAL(12,2) | NOT NULL | Transaction amount |
| currency | VARCHAR(3) | DEFAULT 'INR' | Currency code |
| card_bin | VARCHAR(8) | NULLABLE | First 6-8 digits of card |
| device_fingerprint | VARCHAR(128) | NULLABLE | Browser/device hash |
| ip_address | INET | NULLABLE | Client IP address |
| geo_lat | FLOAT | NULLABLE | Latitude |
| geo_lon | FLOAT | NULLABLE | Longitude |
| channel | VARCHAR(16) | NULLABLE | mobile/web/pos/api |
| extra_data | JSONB | DEFAULT {} | Extensible metadata |
| created_at | TIMESTAMP | INDEX, server_default=now() | Ingestion time |

#### `fraud_decisions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Decision identifier |
| transaction_id | VARCHAR(64) | FK → transactions | Linked transaction |
| risk_score | DECIMAL(5,2) | NOT NULL | Composite score (0-100) |
| decision | VARCHAR(16) | INDEX | approve/verify/escalate/block (block only via analyst action) |
| sub_scores | JSONB | NOT NULL | {module_name: score} |
| signals | TEXT[] | NOT NULL | Array of signal strings |
| explanation | TEXT | NULLABLE | Human-readable summary |
| analyst_action | VARCHAR(16) | NULLABLE | approve/escalate/block (manual only, block is analyst-only) |
| analyst_notes | TEXT | NULLABLE | Analyst review notes |
| decided_at | TIMESTAMP | NOT NULL | Engine decision time |
| reviewed_at | TIMESTAMP | NULLABLE | Analyst review time |

#### `user_profiles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Profile identifier |
| user_id | VARCHAR(64) | UNIQUE | User identifier |
| avg_transaction_amount | DECIMAL(12,2) | NULLABLE | Historical average |
| transaction_count | INT | DEFAULT 0 | Total transaction count |
| typical_merchants | TEXT[] | DEFAULT {} | Frequent merchant list |
| typical_geo_regions | TEXT[] | DEFAULT {} | Common regions |
| risk_level | VARCHAR(16) | DEFAULT 'low' | low/medium/high/critical (computed from avg score at query time) |
| first_seen_at | TIMESTAMP | NULLABLE | First transaction time |
| last_active_at | TIMESTAMP | NULLABLE | Last transaction time |
| extra_data | JSONB | DEFAULT {} | Extensible metadata |
| updated_at | TIMESTAMP | auto-update | Last profile update |

#### `device_profiles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Profile identifier |
| fingerprint | VARCHAR(128) | UNIQUE | Device fingerprint hash |
| user_ids | TEXT[] | NOT NULL | All users on this device |
| os | VARCHAR(32) | NULLABLE | Operating system |
| browser | VARCHAR(32) | NULLABLE | Browser type |
| screen_resolution | VARCHAR(16) | NULLABLE | e.g., "1920x1080" |
| timezone | VARCHAR(64) | NULLABLE | Client timezone |
| language | VARCHAR(8) | NULLABLE | Browser language |
| is_emulator | BOOLEAN | DEFAULT FALSE | Virtual device flag |
| is_rooted | BOOLEAN | DEFAULT FALSE | Jailbroken/rooted flag |
| risk_score | DECIMAL(5,2) | DEFAULT 0 | Device risk score |
| first_seen_at | TIMESTAMP | NULLABLE | First appearance |
| last_seen_at | TIMESTAMP | NULLABLE | Last activity |
| extra_data | JSONB | DEFAULT {} | Extensible metadata |

---

## API Endpoints

### Transaction Processing

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/transactions` | Submit transaction for scoring |
| GET | `/api/v1/transactions` | Search/list transactions (paginated) |
| GET | `/api/v1/fraud/{txn_id}` | Get fraud decision for transaction |

**POST /api/v1/transactions** — Request:
```json
{
  "transaction_id": "txn_abc123",
  "user_id": "user_0042",
  "merchant_id": "MegaMart_003",
  "amount": 15000.00,
  "currency": "INR",
  "device_fingerprint": "fp_device_user0042_1",
  "ip_address": "103.45.67.89",
  "geo_lat": 28.6139,
  "geo_lon": 77.2090,
  "channel": "mobile"
}
```

**POST /api/v1/transactions** — Response (201):
```json
{
  "transaction_id": "txn_abc123",
  "risk_score": 45.2,
  "decision": "verify",
  "signals": [
    "Amount is 5.1x higher than user average",
    "New merchant for user"
  ],
  "sub_scores": {
    "behavior_analyzer": 55.0,
    "velocity_detector": 10.0,
    "device_risk": 20.0,
    "merchant_risk": 30.0,
    "geolocation": 0.0,
    "ip_intelligence": 0.0
  },
  "explanation": "Additional verification required. Risk score 45.2/100. Key concerns: Amount is 5.1x higher than user average; New merchant for user.",
  "processing_time_ms": 47.3
}
```

### Alerts (Analyst Workflow)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/alerts` | List alerts with per-decision counts |
| PATCH | `/api/v1/alerts/{id}` | Update alert with analyst action |

**GET /api/v1/alerts?decision=critical|escalate|verify|block** — Response:
```json
{
  "alerts": [...],
  "total": 257,
  "counts": {
    "all": 257,
    "critical": 14,
    "escalate": 45,
    "verify": 198
  }
}
```

Filter options:
- `critical` — Score > 80 (auto-escalated, shown as "CRITICAL RISK")
- `escalate` — Score 61-80 (auto-escalated, shown as "ESCALATED")
- `verify` — Score 31-60 (shown as "VERIFY")
- `block` — Manually blocked by analyst (shown as "BLOCKED BY ANALYST")

**PATCH /api/v1/alerts/{id}** — Request:
```json
{
  "analyst_action": "approve",
  "analyst_notes": "Verified with customer, legitimate purchase"
}
```

Analyst actions: `approve`, `block`, `escalate`. After action, the alert stays in the list with an updated tag (e.g., "BLOCKED BY ANALYST", "APPROVED BY ANALYST").

### Metrics & Dashboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/metrics` | Real-time fraud metrics |
| GET | `/api/v1/metrics/transactions?category=X` | Drill-down by category |
| GET | `/api/v1/users/{id}/risk-profile` | User risk profile |

**Drill-down categories:** all, critical, escalate, verify, approved, blocked, fraud_rate, high_risk, pending, reviewed, amount_at_risk

### Health Checks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Application health status |
| GET | `/ready` | Dependency readiness check |

---

## Transaction Processing Pipeline

### Step-by-Step Flow

```python
# 1. Receive transaction via POST /api/v1/transactions
payload = TransactionCreate(...)

# 2. Idempotency check (duplicate transaction_id → 409 Conflict)
existing = await db.execute(select(Transaction).where(...))

# 3. Persist raw transaction to PostgreSQL
txn = Transaction(id=uuid4(), **payload.dict())
db.add(txn)
await db.flush()

# 4. Enrichment — parallel Redis lookups (50ms timeout)
enriched = await enrichment_service.enrich(payload)
#   - Velocity counters (sorted sets): vel_1m, vel_5m, vel_1h, vel_24h
#   - User profile (hash): avg_amount, txn_count, typical_merchants
#   - Device profile (hash): is_emulator, is_rooted, user_ids

# 5. Build TransactionContext (transaction data + enriched features)
context = TransactionContext(transaction=payload, enrichment=enriched)

# 6. Parallel Scoring (6 modules via asyncio.gather, 100ms timeout)
module_results = await scoring_pipeline.execute(context)
#   Returns: {module_name: ScoringResult(score, confidence, signals)}

# 7. Weighted Aggregation + Critical Signal Boost + Multi-Module Amplifier
aggregated = risk_aggregator.aggregate(module_results)
#   Base = sum(score * weight)
#   Critical signal boost: if any module >= 80, total = max(base, max_score * 0.6)
#   Multi-module amplifier: count modules scoring >= 20:
#     3 active → 1.2x, 4 active → 1.4x, 5+ active → 1.6x
#   Returns: AggregatedRisk(total_score, sub_scores, confidence, signals)

# 8. Decision Mapping
decision_result = decision_engine.decide(aggregated)
#   Maps score to: approve/verify/escalate/block
#   Generates explanation text

# 9. Persist FraudDecision to PostgreSQL
fraud_decision = FraudDecision(
    transaction_id=...,
    risk_score=decision_result.risk_score,
    decision=decision_result.decision,
    sub_scores=decision_result.sub_scores,
    signals=decision_result.signals,
    explanation=decision_result.explanation,
)
db.add(fraud_decision)
await db.commit()

# 10. Update user profile ONLY if approved (protect baseline from fraud pollution)
if decision_result.decision == "approve":
    await enrichment_service.update_profile_on_approve(
        user_id, device_fingerprint, amount, merchant_id
    )
#   Updates Redis: user:{user_id} → new avg_amount, txn_count, merchants
#   Skipped for block/escalate/verify to prevent fraud from inflating the baseline

# 11. Return response with score, decision, signals, explanation
```

---

## Redis Data Structures

### Velocity Counters (Sorted Sets)

```
Key: velocity:{user_id}
Members: transaction timestamps (epoch ms)
Score: same as member (timestamp)

Operations:
  ZADD velocity:{user_id} {timestamp} {timestamp}      # Record txn
  ZCOUNT velocity:{user_id} {now-60s} {now}            # Count last 1 min
  ZCOUNT velocity:{user_id} {now-300s} {now}           # Count last 5 min
  ZCOUNT velocity:{user_id} {now-3600s} {now}          # Count last 1 hour
  ZCOUNT velocity:{user_id} {now-86400s} {now}         # Count last 24 hours
  ZREMRANGEBYSCORE velocity:{user_id} -inf {now-86400s} # Cleanup old entries
```

### User Profile Cache (Hashes)

```
Key: user:{user_id}
Fields:
  avg_amount: "2500.00"
  txn_count: "47"
  typical_merchants: "MegaMart_001,FoodDash_003,TechZone_002"
  typical_geo_regions: "IN,APAC"
  risk_level: "low"

TTL: 3600 seconds (1 hour)
```

**Update logic (approve-only):**

```python
# Only called when decision == "approve"
async def update_on_transaction(user_id, amount, merchant_id):
    profile = await redis.hgetall(f"user:{user_id}") or defaults

    # Incremental running average (O(1), no historical recalculation)
    count = profile["txn_count"] + 1
    new_avg = (profile["avg_amount"] * profile["txn_count"] + amount) / count

    # Rolling merchant window (last 10)
    merchants = (profile["typical_merchants"] + [merchant_id])[-10:]

    # Write back with TTL refresh
    await redis.hset(f"user:{user_id}", mapping={...})
    await redis.expire(f"user:{user_id}", 3600)
```

**Why approve-only:** If a ₹5,000,000 fraud transaction (blocked) updated the profile, the user's avg would jump from ₹500 to ₹49,995 — making future ₹50,000 fraud look "normal" (only 1x average). By excluding non-approved transactions, the baseline stays clean and the Behavior Analyzer continues detecting anomalies accurately.

### Device Profile Cache (Hashes)

```
Key: device_profile:{fingerprint}
Fields:
  user_ids: "user_0042,user_0103"
  is_emulator: "0"
  is_rooted: "0"
  first_seen: "1718800000"
  risk_score: "15.0"

TTL: 7200 seconds (2 hours)
```

---

## Docker Compose Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| fraud-api | bee-fraud-api (custom) | 8001 → 8000 | FastAPI backend |
| postgres | postgres:16-alpine | 5433 → 5432 | Primary database |
| redis | redis:7-alpine | 6380 → 6379 | Cache + velocity |
| dashboard | bee-dashboard (custom) | 3001 → 5173 | React frontend (dev) |
| mock-gen | bee-fraud-api (same image) | — | Traffic generator (profile: mock) |

### Service Dependencies

```
postgres (healthy) ─┐
                    ├──> fraud-api (healthy) ──> mock-gen
redis (healthy) ────┘                       ──> dashboard
```

Health checks ensure databases are accepting connections before the API starts, and the API is responding before mock traffic begins.

---

## Frontend Architecture

### State Management

No global state library — each page uses local state + custom hooks:

- **useMetrics()** — Polls `/api/v1/metrics` every 5 seconds
- **useAlerts(filter)** — Fetches all alerts, provides optimistic updates + server-side counts
- **useTransactions()** — On-demand search with debouncing

### Optimistic UI Updates

Alert actions (approve, escalate, block) update local state immediately for instant visual feedback. The alert stays in the list with an updated badge (e.g., "BLOCKED BY ANALYST"):

```typescript
const updateAlert = async (alertId: string, action: string) => {
  // 1. Update analyst_action in local state immediately (optimistic)
  setAllAlerts((prev) =>
    prev.map((a) => a.id === alertId ? { ...a, analyst_action: action } : a)
  )

  // 2. Persist to backend
  await api.patch(`/api/v1/alerts/${alertId}`, { analyst_action: action })

  // 3. Refresh from server after 1.5s (avoids race condition)
  setTimeout(fetchAlerts, 1500)
}
```

The badge display uses a unified `getRiskLevelBadge(score, decision, analystAction)` function that prioritizes analyst actions over score-based labels:
1. `analyst_action === 'block'` → "BLOCKED BY ANALYST" (red, prominent)
2. `analyst_action === 'approve'` → "APPROVED BY ANALYST" (green)
3. `analyst_action === 'escalate'` → "ESCALATED BY ANALYST" (orange)
4. `score > 80` → "CRITICAL RISK" (red)
5. `decision === 'escalate'` → "ESCALATED" (orange)
6. `decision === 'verify'` → "VERIFY" (yellow)
7. Default → "APPROVED" (green)

### Key UI Patterns

| Pattern | Implementation |
|---------|---------------|
| Click-outside-to-close | `useRef` + `mousedown` event listener |
| Instant tooltips | Custom CSS with `group-hover:opacity-100 duration-75` |
| Drill-down modals | State-driven panel showing filtered transaction list |
| Filter tabs with counts | Server-side counts from API (not computed from truncated list) |
| Verification-pending priority | Client-side sort: verify first, then by risk_score desc |

---

## Mock Data Generation

### Configuration

```python
MOCK_TPS = 10           # Transactions per second
MOCK_FRAUD_RATE = 0.05  # 5% of transactions are fraudulent
MOCK_SEED = 42          # Deterministic generation
```

### Generated Data

- **1,000 users** — 4 spending profiles (low 40%, medium 35%, high 15%, premium 10%)
- **500 merchants** — 6 categories (retail, food, electronics, travel, digital, gambling)
- **7 fraud patterns** — injected into 5% of transactions

### Traffic Flow

```
MockRunner (10 TPS) → POST /api/v1/transactions → Full Pipeline → DB
                                                                    ↓
                                                              Dashboard reads
```

---

## Middleware Stack

Applied in order (outermost first):

1. **CorrelationMiddleware** — Generates/propagates `X-Request-ID` for request tracing
2. **StructuredLoggingMiddleware** — JSON-formatted request/response logs with correlation ID
3. **TimingMiddleware** — Adds `X-Process-Time` header (ms)
4. **CORSMiddleware** — Allows `localhost:3000`, `localhost:3001`, `localhost:5173`

---

## Configuration (Environment Variables)

| Variable | Default | Description |
|----------|---------|-------------|
| APP_ENV | development | Environment name |
| APP_HOST | 0.0.0.0 | Bind address |
| APP_PORT | 8000 | API port |
| DATABASE_URL | postgresql+asyncpg://fraud:fraud_secret@localhost:5432/fraud_detection | PostgreSQL connection |
| REDIS_URL | redis://localhost:6379/0 | Redis connection |
| REDIS_MAX_CONNECTIONS | 20 | Redis pool size |
| ENRICHMENT_TIMEOUT_MS | 50 | Hard timeout for cache lookups |
| SCORING_TIMEOUT_MS | 100 | Hard timeout for scoring pipeline |
| MOCK_TPS | 10 | Mock generator speed |
| MOCK_FRAUD_RATE | 0.05 | Fraud injection rate |
| MOCK_SEED | 42 | Random seed for reproducibility |
| APP_LOG_LEVEL | info | Logging level |

---

## Risk Score Aggregation Logic

The `RiskAggregator` combines 6 module scores into a single 0-100 score using three layers:

### Layer 1: Weighted Average

```
Base Score = Σ (module_score × module_weight)
```

| Module | Weight |
|--------|--------|
| Behavior Analyzer | 25% |
| Velocity Detector | 20% |
| Device Risk | 20% |
| Merchant Risk | 15% |
| Geolocation | 10% |
| IP Intelligence | 10% |

### Layer 2: Critical Signal Boost

A pure weighted average dilutes extreme signals (e.g., Behavior=90 → only 22.5 after weighting).

```python
if max(module_scores) >= 80:
    floor = max_module_score * 0.6
    total = max(base, floor)
```

Ensures any single extreme fraud signal reaches at least VERIFY level.

### Layer 3: Multi-Module Amplifier

When fraud manifests as moderate signals across many dimensions simultaneously, the weighted average is still too low. The amplifier boosts scores based on how many modules detected risk (score >= 20):

```python
active_modules = count(modules where score >= 20)

if active_modules >= 5: total *= 1.6
elif active_modules >= 4: total *= 1.4
elif active_modules >= 3: total *= 1.2
```

### Combined Effect Examples

| Scenario | Base | After Boost | After Amplifier | Decision |
|----------|------|-------------|-----------------|----------|
| 1 extreme signal (90), others quiet | 22.5 | 54 | 54 (1 active, no amplifier) | VERIFY |
| 1 extreme (90) + 3 moderate signals | 44 | 54 | 75.6 (4 active, 1.4x) | ESCALATE (High) |
| 5 modules flagging risk (max 85) | 43 | 51 | 81.6 (5 active, 1.6x) | ESCALATE (Critical) |

### Decision Thresholds

| Score Range | Decision | Risk Level | Action |
|-------------|----------|------------|--------|
| 0–30 | APPROVE | Low | Auto-approve |
| 31–60 | VERIFY | Medium | Step-up auth (OTP/2FA), analyst can Approve/Escalate/Block |
| 61–80 | ESCALATE | High | Queue for analyst review, analyst can Approve/Block |
| 81–100 | ESCALATE | Critical | Critical risk alert, analyst can Approve/Block |

**Important:** There is NO auto-block. All blocking is manual (analyst action only). The system escalates high-risk transactions for human review. The `decision` field is updated to `"block"` only when an analyst explicitly takes the block action — the scoring engine never assigns `"block"` as an initial decision.

### User Risk Level

User risk level is computed from the user's **average risk score** (of non-approved transactions), using the same boundaries as transaction risk levels:

| Avg Risk Score | Risk Level |
|----------------|------------|
| > 80 | Critical |
| > 60 | High |
| > 30 | Medium |
| ≤ 30 | Low |

---

## Error Handling & Resilience

### Timeout Cascade

```
Total budget: ~150ms
  ├── Enrichment: 50ms hard cap (asyncio.wait_for)
  │     ├── Velocity lookup: 50ms
  │     ├── User profile lookup: 50ms    (all parallel)
  │     └── Device profile lookup: 50ms
  └── Scoring: 100ms hard cap (asyncio.gather)
        ├── Behavior: 100ms
        ├── Velocity: 100ms
        ├── Device: 100ms     (all parallel)
        ├── Merchant: 100ms
        ├── Geolocation: 100ms
        └── IP Intelligence: 100ms
```

### Failure Modes

| Component | Failure | Behavior |
|-----------|---------|----------|
| Redis down | Cache miss | Enrichment returns defaults, scoring continues |
| Single scoring module | Exception/timeout | Returns neutral score (50.0, confidence 0.0) |
| PostgreSQL down | Write failure | Returns 500, transaction not scored |
| Mock generator | API unreachable | Retries with backoff, logs errors |

### Idempotency

Duplicate `transaction_id` in POST returns **409 Conflict** with existing decision — prevents replay attacks and double-scoring.

---

## Deployment

### Local Development

```bash
git clone <repo>
cd bee
docker compose up -d                    # Start all services
docker compose --profile mock up -d     # Start with mock traffic
```

### Production Considerations (Not Implemented)

- Horizontal scaling: Multiple fraud-api replicas behind load balancer
- Redis Cluster for velocity counters at scale
- PostgreSQL read replicas for dashboard queries
- Kafka/SQS for async transaction ingestion (decoupled from scoring)
- Prometheus metrics + Grafana dashboards
- Rate limiting on API endpoints
- JWT authentication for dashboard access

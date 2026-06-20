# AI-Powered Real-Time Fraud Detection Platform

## Problem Statement

### Background

Financial platforms processing digital payments face an escalating threat from increasingly sophisticated fraud attacks. Traditional rule-based fraud detection systems suffer from:

- **High false positive rates** — legitimate transactions get blocked, damaging customer experience and revenue
- **Inability to detect novel fraud patterns** — static rules can only catch known patterns
- **Latency bottlenecks** — sequential processing cannot meet real-time transaction approval SLAs
- **Lack of explainability** — black-box ML models produce decisions that analysts cannot audit or understand
- **No analyst workflow** — flagged transactions pile up with no structured review process

### The Challenge

Build a **real-time fraud detection platform** that:

1. Scores every transaction for fraud risk within **100ms end-to-end**
2. Uses **6 parallel risk assessment modules** covering different fraud dimensions
3. Produces **transparent, explainable decisions** (not black-box predictions)
4. Provides a **three-tier decision framework** (approve/verify/escalate) that balances security with customer friction — with no auto-blocking
5. Delivers an **analyst dashboard** for reviewing escalated transactions with drill-down capabilities

---

## Risk Assessment Architecture

### Scoring Pipeline Overview

Each incoming transaction passes through a parallel scoring pipeline:

```
Transaction → Enrichment (50ms) → 6 Parallel Scoring Modules (100ms) → Weighted Aggregation → Decision
```

The pipeline produces a **composite risk score (0-100)** by running 6 independent modules in parallel, each analyzing a different fraud dimension.

### Module Weights

| Module | Weight | What It Detects |
|--------|--------|----------------|
| Behavior Analyzer | 25% | Spending anomalies vs. user history |
| Velocity Detector | 20% | Transaction burst patterns (card testing) |
| Device Risk Engine | 20% | Compromised/spoofed devices |
| Merchant Risk Engine | 15% | High-risk merchant categories |
| Geolocation Engine | 10% | Impossible travel, suspicious regions |
| IP Intelligence | 10% | VPN, TOR, proxy, datacenter IPs |

**Total: 100%**

---

## Scoring Module Details

### 1. Behavior Analyzer (25% Weight)

Detects spending anomalies by comparing the current transaction against the user's historical behavior profile.

**Risk Signals:**

| Signal | Score Impact | Description |
|--------|-------------|-------------|
| Extreme amount deviation (50x+) | +80 | Amount far exceeds user's average |
| High amount deviation (10x-50x) | +60 | Significant spending spike |
| Moderate deviation (5x-10x) | +40 | Notable spending increase |
| Mild deviation (3x-5x) | +20 | Slightly elevated spending |
| First-time user | +10 | No transaction history available |
| New merchant for user | +15 | User never transacted with this merchant |
| Unusual time of day (1-5 AM) | +20 | Transactions during unusual hours |
| Late night (22:00-01:00) | +10 | Somewhat unusual timing |
| Large round amount (>=10,000 divisible by 1000) | +10 | Pattern common in test transactions |

**Confidence:** 0.3 for first-ever transaction (no history), then scales linearly as `txn_count / 20` up to 1.0 (reaches full confidence at 20+ prior transactions)

---

### 2. Velocity Detector (20% Weight)

Detects burst patterns that indicate card testing, automated attacks, or rapid account drain.

**Time Window Thresholds:**

| Window | Threshold | Score Impact | Pattern |
|--------|-----------|-------------|---------|
| 1 minute | >= 3 transactions | up to 70 | Rapid-fire automated attack |
| 5 minutes | >= 8 transactions | up to 50 | Sustained burst |
| 1 hour | >= 20 transactions | +20 | High-frequency abuse |
| 24 hours | >= 50 transactions | +15 | Volume-based fraud |

**Acceleration Detection:** If 5-minute velocity exceeds 3x the 1-hour average rate, an additional +15 score is applied (indicates sudden acceleration pattern).

**Confidence:** 0.9 (velocity data from Redis is highly reliable)

---

### 3. Device Risk Engine (20% Weight)

Identifies compromised, emulated, or shared devices commonly used in account takeover attacks.

**Risk Signals:**

| Signal | Score Impact | Description |
|--------|-------------|-------------|
| Emulator detected | +40 | Virtual device (common in automated fraud) |
| Rooted/jailbroken | +30 | Security bypasses enabled |
| New device (< 5 min old) | +25 | Recently provisioned device |
| First time seen | +20 | Device has no history |
| Shared device (3+ users) | +25 | Multiple accounts on one device |
| Shared device (2 users) | +10 | Possible shared household |
| Emulator + rooted combo | +15 | Additional penalty for combined signals |
| Recently registered (< 1 hour) | +10 | Very new device registration |
| No fingerprint available | +15 | Cannot identify device |

**Confidence:** 0.85 (device fingerprinting is reliable but not perfect)

---

### 4. Merchant Risk Engine (15% Weight)

Evaluates risk based on merchant category, fraud rates, and transaction context.

**Category Risk Scores:**

| Category | Base Score | Fraud Rate |
|----------|-----------|-----------|
| Gambling | 30 | 8% |
| Crypto | 25 | 5% |
| Adult | 20 | 4% |
| Digital Goods | 15 | 5% |
| Travel | 10 | 3% |
| Electronics | 10 | 4% |
| Retail | 0 | 2% |
| Food Delivery | 0 | 1.5% |

**Additional Signals:**

| Signal | Score Impact | Description |
|--------|-------------|-------------|
| Suspicious merchant name (test_, demo_, temp_) | +20 | Likely test/fraudulent merchant |
| New merchant for user | +10 | User has no history with merchant |
| Large amount at high-risk merchant (>50,000) | +15 | High value + high risk category |
| Cross-border transaction | +10 | International merchant |

**Confidence:** 0.7 (merchant context is variable)

---

### 5. Geolocation Engine (10% Weight)

Detects physically impossible travel patterns and transactions from suspicious geographic regions.

**Impossible Travel Detection:**

Uses the Haversine formula to calculate distance between consecutive transaction locations, then computes implied travel speed.

| Speed | Score Impact | Example |
|-------|-------------|---------|
| > 900 km/h (impossible travel) | +60 | Delhi to London in 30 minutes |
| > 500 km/h (suspicious travel) | +30 | Faster than commercial flight |
| > 1000 km from last location | +15 | Large geographic shift |

**Region-Based Signals:**

| Signal | Score Impact |
|--------|-------------|
| New geographic region for user | +25 |
| High-risk country/region | +20 |

**Confidence:** 0.8 with geolocation data, 0.2 without (early return with no signals)

---

### 6. IP Intelligence (10% Weight)

Identifies connections from anonymizing networks, datacenters, and suspicious IP ranges.

**IP Classification Signals:**

| Signal | Score Impact | Description |
|--------|-------------|-------------|
| TOR exit node | +45 | Maximum anonymity tool |
| Loopback address (127.x.x.x) | +40 | Invalid production traffic |
| Private IP in production | +30 | Should not originate external payments |
| VPN detected | +25 | Connection anonymization |
| Proxy detected | +20 | IP masking |
| Datacenter/cloud IP | +20 | Non-residential origin |
| Multiple risk indicators | +15 | Compound anomaly |
| IP/geo country mismatch | +15 | Location inconsistency |
| Invalid IP format | +10 | Malformed address |

**Known Datacenter Prefixes:** Google (34.x, 35.x), AWS (52.x, 54.x), Cloudflare (104.16.x), Azure (13.64.x)

**Confidence:** 0.75

---

## Risk Aggregation

### Weighted Score Formula

```
Base Score = sum(module_score[i] * weight[i]) for i in all_modules
```

Where:
- `module_score[i]` = individual module score (0-100)
- `weight[i]` = module weight (summing to 1.0)
- Final score clamped to [0, 100]

### Critical Signal Boost

A pure weighted average can dilute extreme fraud signals when only one module fires. For example, a Behavior score of 90 (47,000x spending anomaly) would only contribute 22.5 points to the total if other modules are quiet — resulting in an inappropriately low overall score.

To address this, the aggregator applies a **critical signal boost**:

```
If max(module_scores) >= 80:
    floor = max_module_score * 0.6
    Total Score = max(Base Score, floor)
```

**Effect:**

| Highest Module Score | Minimum Total Score | Decision Floor |
|---------------------|--------------------:|---------------|
| 80 | 48 | VERIFY |
| 85 | 51 | VERIFY |
| 90 | 54 | VERIFY |
| 95 | 57 | VERIFY |
| 100 | 60 | VERIFY (at ESCALATE boundary) |

This ensures that a single extreme fraud signal (score >= 80) always results in at least a verification request, even when other modules report no anomalies. The boost prevents obvious fraud from slipping through as "approved" due to averaging.

**Example:**
- Behavior scores 90 (amount 47,000x higher than average)
- All other modules score 0-10 (no other signals)
- Without boost: weighted average = ~36.5 (barely VERIFY)
- With boost: max(36.5, 90 * 0.6) = **54** (solidly VERIFY, approaching ESCALATE)

### Multi-Module Amplifier

The critical signal boost handles single extreme signals, but fraud often manifests as *multiple moderate signals* across different dimensions. A transaction triggering 5 out of 6 modules (e.g., behavior anomaly + high velocity + suspicious device + risky merchant + bad IP) represents high-confidence fraud — yet individual module scores might be moderate (20-60 range), resulting in a weighted average that's too low.

The **multi-module amplifier** addresses this by boosting scores when multiple modules detect risk simultaneously:

```
active_modules = count(modules where score >= 20)

If active_modules >= 5: Total Score *= 1.6
Elif active_modules >= 4: Total Score *= 1.4
Elif active_modules >= 3: Total Score *= 1.2
```

**Effect (applied after critical signal boost):**

| Active Modules | Multiplier | Example Base → Final | Decision |
|---------------|-----------|---------------------|----------|
| 3 of 6 | 1.2x | 45 → 54 | VERIFY |
| 4 of 6 | 1.4x | 50 → 70 | ESCALATE |
| 5 of 6 | 1.6x | 54 → 86.4 | ESCALATE (Critical) |

**Example (transaction hitting 5 modules):**
- Behavior: 90 (extreme amount anomaly) → 22.5 weighted
- Velocity: 35 (elevated volume) → 7.0 weighted
- Device: 20 (recently registered + shared) → 4.0 weighted
- Merchant: 45 (gambling + large amount) → 6.75 weighted
- IP: 30 (private address) → 3.0 weighted
- Geo: 0 (no signal) → 0 weighted
- Base score: 43.25
- After critical signal boost: max(43.25, 90 * 0.6) = 54
- After multi-module amplifier (5 active): 54 * 1.6 = **86.4** → ESCALATE (Critical Risk)

This ensures that broad fraud coverage across multiple dimensions correctly escalates the transaction with critical risk level, even when no single module produces an extreme score.

### Confidence Calculation

```
Overall Confidence = sum(module_confidence[i] * weight[i]) for i in all_modules
```

### Graceful Degradation

- If a module fails (timeout, error), it returns a neutral score of 50.0 with confidence 0.0
- Failed modules' neutral scores still participate in the weighted average but with zero confidence
- The neutral score of 50 counts as an "active module" (score >= 20) for the multi-module amplifier — this is conservative by design (a failed module doesn't reduce the amplification of genuine signals from other modules)
- The system never blocks scoring due to individual module failures

---

## Decision Framework

### Three-Tier Decision Thresholds

| Score Range | Decision | Risk Level | Action | Customer Impact |
|-------------|----------|------------|--------|----------------|
| 0 - 30 | **APPROVE** | Low | Auto-approve transaction | None (seamless) |
| 31 - 60 | **VERIFY** | Medium | Request step-up authentication (OTP/2FA) | Minor friction |
| 61 - 100 | **ESCALATE** | High / Critical | Queue for analyst manual review | Transaction held |

**Important:** There is no auto-block decision. The system never automatically rejects a transaction. All high-risk transactions are escalated to an analyst who can then choose to block, approve, or further escalate. This prevents false-positive auto-rejections and keeps a human in the loop for all denial decisions.

### User Risk Levels

Each user is assigned a risk level based on their **average risk score** across non-approved transactions:

| Avg Risk Score | Risk Level | Dashboard Display |
|----------------|------------|-------------------|
| > 80 | Critical | Red badge |
| > 60 | High | Orange badge |
| > 30 | Medium | Yellow badge |
| ≤ 30 | Low | Green badge |

### Explainability

Every decision includes:
- **Risk score** (0-100)
- **Sub-scores** from each module
- **Signals** — human-readable reasons (e.g., "Amount is 50x higher than user average")
- **Explanation** — natural language summary of the decision rationale
- **Primary risk driver** — the module contributing most to the score

---

## Analyst Workflow

### Alert Management

Transactions with decisions of **Verify** or **Escalate** are surfaced as alerts requiring analyst attention. These are the only transactions that need human review — approved transactions pass through automatically.

**Analyst Actions:**
- **Approve** — Override the system decision, allow the transaction to proceed
- **Escalate** — Increase severity, route to senior analyst (available on Verify decisions)
- **Block** — Manually block the transaction (only action that rejects a transaction)

**Key principle:** Blocking is always a manual analyst decision. The system never auto-blocks. This ensures zero false-positive rejections and maintains a human-in-the-loop for all denial actions.

### Transaction Decision Lifecycle

A transaction's `decision` field follows this lifecycle:

```
Engine assigns initial decision (approve/verify/escalate)
        │
        ├── approve → transaction completes, user profile updated
        │
        └── verify/escalate → alert created, awaits analyst
                │
                ├── Analyst approves → decision changes to "approve"
                ├── Analyst escalates → decision stays "escalate"
                └── Analyst blocks → decision changes to "block"
```

**Fields stored per decision:**
- `decision` — The current decision state (mutable by analyst action)
- `analyst_action` — The specific action taken by the analyst (approve/escalate/block), or null if pending
- `risk_score` — Immutable score from the scoring engine (never changes)
- `sub_scores` — Per-module breakdown (immutable)
- `signals` — Individual risk signals detected (immutable)

### Alert Filters

The alert queue supports filtering by:
- **All** — Show all actionable alerts (escalate + verify), sorted by risk score
- **Critical** — Escalated decisions with score > 80 (highest priority)
- **Escalated** — Escalated decisions with score 61-80
- **Verify** — Verify decisions (score 31-60)
- **Blocked** — Transactions manually blocked by analyst

### Dashboard Capabilities

- **Real-time metrics** — Total transactions, fraud rate, throughput TPS, decision distribution
- **Drill-down by category** — Click any metric card to see underlying transactions with detail panel
- **Alert queue** — Prioritized list with unresolved escalations on top, filterable
- **Risk breakdown** — Per-module sub-scores with visual bar chart for any transaction
- **Fraud signals** — Individual signals that contributed to the risk score
- **AI explanation** — Natural language summary of why the decision was made
- **Top risky users** — Users sorted by average risk score with risk level badges
- **User risk profiles** — Drill into any user to see transaction history and risk pattern
- **Amount at risk** — Total monetary exposure from escalated + analyst-blocked transactions

---

## Fraud Patterns Covered

The platform detects and handles 7 core fraud patterns:

| # | Pattern | Primary Modules Triggered |
|---|---------|--------------------------|
| 1 | **Velocity Burst** — 10-15 txns from same merchant in 1-2 minutes | Velocity (20%), Behavior (25%) |
| 2 | **Account Takeover** — New device + large amount from foreign location | Device (20%), Geo (10%), Behavior (25%) |
| 3 | **Impossible Travel** — Delhi to London in 30 minutes | Geolocation (10%), Behavior (25%) |
| 4 | **Card Testing** — 8-15 micro-transactions (<50 INR) from datacenter IP | Velocity (20%), IP (10%), Merchant (15%) |
| 5 | **Device Spoofing** — Emulator + rooted + datacenter IP + large amount | Device (20%), IP (10%), Behavior (25%) |
| 6 | **Amount Anomaly** — Single transaction 10-50x user's average spend | Behavior (25%), Merchant (15%) |
| 7 | **Mixed Pattern** — VPN/TOR + emulator + cross-border + large amount | All modules triggered |

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| End-to-end scoring latency | < 100ms (p95) |
| Enrichment timeout | 50ms hard cap |
| Scoring pipeline timeout | 100ms hard cap |
| Throughput | 10+ TPS sustained |
| Availability | Graceful degradation (scoring continues if Redis/cache is down) |
| Data retention | All decisions persisted for audit |

---

## User Profile Management

### Profile Lifecycle

The system maintains a **running user profile** in Redis that captures each user's "normal" transaction behavior. Scoring modules compare each incoming transaction against this baseline to detect anomalies.

**Profile fields:**

| Field | Purpose | Used By |
|-------|---------|---------|
| `avg_amount` | Running average of legitimate transaction amounts | Behavior Analyzer (deviation detection) |
| `txn_count` | Number of approved transactions | Behavior Analyzer (confidence scaling) |
| `typical_merchants` | Last 10 merchants (rolling window) | Merchant Risk Engine |
| `typical_geo_regions` | Known user locations | Geolocation Engine |
| `risk_level` | Computed risk classification | Enrichment context |

### Conditional Profile Updates (Approve-Only)

**Critical design decision:** Only **approved** transactions update the user's profile. Escalated or verified transactions are excluded.

```
Transaction → Enrichment (read profile) → Scoring → Decision
                                                       │
                                          ┌────────────┴────────────┐
                                          │                         │
                                     APPROVE                  ESCALATE/VERIFY
                                          │                         │
                                   Update profile              DO NOT update
                                   (avg, count,                (profile stays
                                    merchants)                  unchanged)
```

**Why this matters:**

Without this protection, a single fraudulent transaction (e.g., ₹5,000,000 on a user averaging ₹500) would permanently inflate the user's baseline:

| Scenario | User Avg After Fraud | Next ₹50,000 Fraud Detected? |
|----------|---------------------|------------------------------|
| **Without protection** | ₹500 → ₹49,995 (polluted) | No — only 1x "average" |
| **With protection** | ₹500 → ₹500 (preserved) | Yes — 100x anomaly detected |

### Running Average Formula

```
new_count = txn_count + 1
new_avg = (avg_amount × txn_count + new_amount) / new_count
```

This is an O(1) incremental calculation — no need to recompute from all historical transactions.

### What Updates When

| Component | Approve | Escalate/Verify |
|-----------|:-------:|:---------------------:|
| Velocity counters (burst detection) | Always | Always |
| User `avg_amount` | Updated | Unchanged |
| User `txn_count` | +1 | Unchanged |
| User `typical_merchants` | Appended | Unchanged |
| Device profile | Updated | Unchanged |

**Velocity always updates** because burst detection needs to count ALL transactions (including fraudulent ones) to detect card testing and automated attacks.

### Storage Architecture

| Layer | Purpose | TTL |
|-------|---------|-----|
| Redis cache (`user:{user_id}`) | Real-time enrichment during scoring | 1 hour |
| PostgreSQL (`user_profiles` table) | Persistent storage for analytics | Permanent |

---

## Key Design Principles

1. **Transparency over accuracy** — Threshold-based decisions (not black-box ML) enable full audit trail
2. **Parallel over sequential** — All 6 modules and 3 cache lookups execute concurrently
3. **Graceful degradation** — No single component failure blocks the scoring pipeline
4. **Explainability first** — Every decision includes human-readable reasoning
5. **Never auto-block** — System escalates all high-risk cases to analysts; only humans can block
6. **Deterministic testing** — Seed-based mock data enables reproducible fraud scenarios
7. **Clean baseline preservation** — Fraudulent transactions never pollute the user's behavioral profile

---

## Solution Summary

### Problem Solved

Traditional fraud detection systems either auto-block too aggressively (causing false-positive rejections and customer churn) or rely on opaque ML models that analysts cannot audit. This platform solves both by:

1. **Eliminating auto-block** — No transaction is ever automatically rejected. High-risk transactions are escalated to human analysts who make the final call.
2. **Providing full explainability** — Every risk score comes with per-module sub-scores, individual signals, and AI-generated explanations.
3. **Achieving sub-100ms latency** — Parallel scoring across 6 independent modules with async I/O and Redis-backed enrichment.
4. **Enabling analyst workflow** — Structured alert queue with approve/escalate/block actions and real-time dashboard.

### Technical Implementation

| Component | Technology | Key Design |
|-----------|-----------|-----------|
| API Server | Python 3.12, FastAPI, async | Lifespan-managed connections, structured logging |
| Database | PostgreSQL 16, SQLAlchemy 2.0 async | Optimized single-query aggregations (no N+1) |
| Cache | Redis 7, sorted sets + hashes | Velocity counters, user profiles, device profiles |
| Scoring | 6 parallel modules via asyncio.gather | Weighted aggregation + critical boost + multi-module amplifier |
| Dashboard | React 18, TypeScript, TailwindCSS | Real-time metrics, drill-down, analyst actions |
| Mock Data | Seed-based generators | 1000 users, 500 merchants, 7 fraud patterns |

### Performance Achieved

| Metric | Target | Achieved |
|--------|--------|----------|
| Scoring latency (p95) | < 100ms | ~70-86ms |
| User list endpoint | < 200ms | ~70ms (single aggregated query) |
| Enrichment timeout | 50ms cap | Redis cache hits < 5ms |
| Throughput | 10+ TPS | Sustained via async pipeline |
| Availability | Graceful degradation | Scoring continues if Redis is down |

### Key Optimizations

1. **N+1 Query Elimination** — User listing uses a single SQL query with `CASE` expressions for conditional aggregation instead of per-user subqueries
2. **Parallel Module Execution** — All 6 scoring modules run concurrently via `asyncio.gather(return_exceptions=True)`
3. **Redis-first Enrichment** — User profiles, device data, and velocity counters cached in Redis with 1-hour TTL
4. **Optimistic UI Updates** — Analyst actions update local state immediately while persisting asynchronously
5. **Click-outside Dismissal** — Transaction detail panels close on outside click for fast analyst workflow

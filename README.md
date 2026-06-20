# Bee - AI-Powered Fraud Detection Platform

Real-time fraud detection system that scores financial transactions using 6 parallel ML modules, renders automated decisions, and provides an analyst dashboard for manual review.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Dashboard (:3001)                   │
│  Metrics | Alerts Queue | Transaction Detail | User Profile  │
└─────────────────────────────────┬───────────────────────────┘
                                  │ REST API
┌─────────────────────────────────▼───────────────────────────┐
│                    FastAPI Backend (:8001)                    │
│  /api/v1/transactions | /alerts | /metrics | /users | /fraud │
├──────────────────────────────────────────────────────────────┤
│                      Scoring Pipeline                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Behavior │ │ Velocity │ │  Device  │ │ Merchant │       │
│  │   25%    │ │   20%    │ │   20%    │ │   15%    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐                                  │
│  │   Geo    │ │ IP Intel │  ← All run in parallel            │
│  │   10%    │ │   10%    │                                   │
│  └──────────┘ └──────────┘                                  │
├──────────────────────────────────────────────────────────────┤
│  Decision Engine: 0-30=approve | 31-60=verify | 61-80=review │
│                   81-100=block                                │
└──────────────┬───────────────────────────┬──────────────────┘
               │                           │
    ┌──────────▼──────────┐     ┌──────────▼──────────┐
    │  PostgreSQL (:5433) │     │    Redis (:6380)     │
    │  Transactions       │     │  Velocity counters   │
    │  Fraud decisions    │     │  User profiles       │
    │  User profiles      │     │  Device profiles     │
    └─────────────────────┘     └──────────────────────┘
```

## Prerequisites & Requirements

### System Requirements

| Requirement | Version | Check Command | Install |
|-------------|---------|---------------|---------|
| **Git** | any | `git --version` | `brew install git` / `apt install git` |
| **Docker** | v20.10+ | `docker --version` | See below |
| **Docker Compose** | v2.0+ (bundled with Docker Desktop) | `docker compose version` | Comes with Docker Desktop |
| **Internet** | — | `ping google.com` | Needed for pulling Docker images on first run |
| **RAM** | 4 GB minimum (8 GB recommended) | — | — |
| **Disk Space** | ~3 GB (for Docker images + build cache) | `df -h` | — |
| **OS** | macOS, Linux, or Windows (WSL2) | — | — |

> **No Python, Node.js, PostgreSQL, or Redis installation required on your machine.** Everything runs inside Docker containers.

### Port Requirements

These ports must be free on your machine:

| Port | Service | Check if free |
|------|---------|---------------|
| `8001` | Fraud Detection API | `lsof -i :8001` |
| `3001` | React Dashboard (UI) | `lsof -i :3001` |
| `5433` | PostgreSQL | `lsof -i :5433` |
| `6380` | Redis | `lsof -i :6380` |

If any port is occupied, either stop the conflicting service or change the port mapping in `docker-compose.yml`.

### Docker Images Pulled Automatically

| Image | Purpose |
|-------|---------|
| `python:3.12-slim` | Backend API runtime |
| `node:20-alpine` | Dashboard build & dev server |
| `postgres:16-alpine` | Transaction & decision storage |
| `redis:7-alpine` | Velocity counters & profile caching |

### For Local Development (Without Docker — Advanced)

If you want to run services directly on your machine instead of Docker:

| Requirement | Version | Install | Verify |
|-------------|---------|---------|--------|
| Python | 3.12+ | `brew install python@3.12` | `python3 --version` |
| Node.js | 20+ | `brew install node@20` | `node --version` |
| PostgreSQL | 16+ | `brew install postgresql@16` | `psql --version` |
| Redis | 7+ | `brew install redis` | `redis-server --version` |
| pip | latest | Bundled with Python | `pip3 --version` |
| npm | 10+ | Bundled with Node.js | `npm --version` |
| curl | any | Pre-installed on macOS/Linux | `curl --version` |

**Setup without Docker:**

```bash
# 1. Start PostgreSQL and Redis
brew services start postgresql@16
brew services start redis

# 2. Create database
createdb -U $(whoami) fraud_detection

# 3. Install Python dependencies
cd bee
pip3 install -e ".[dev]"

# 4. Set environment variables
export DATABASE_URL="postgresql+asyncpg://$(whoami)@localhost:5432/fraud_detection"
export REDIS_URL="redis://localhost:6379/0"
export APP_ENV=development

# 5. Run database migrations
python3 -c "from fraud_detection.db.migrate import run_migrations; import asyncio; asyncio.run(run_migrations())"

# 6. Start the API server
uvicorn fraud_detection.main:app --host 0.0.0.0 --port 8000 --reload

# 7. In another terminal — start the dashboard
cd dashboard
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

### Python Dependencies (installed automatically via Docker)

```
fastapi>=0.115.0          # Async web framework
uvicorn[standard]>=0.30.0 # ASGI server with uvloop
sqlalchemy[asyncio]>=2.0.30 # Async ORM
asyncpg>=0.30.0           # PostgreSQL async driver
alembic>=1.14.0           # Database migrations
redis>=5.0.0              # Redis async client
pydantic>=2.8.0           # Data validation & serialization
pydantic-settings>=2.4.0  # Environment-based config
structlog>=24.4.0         # Structured logging
httpx>=0.27.0             # Async HTTP client
python-ulid>=2.7.0        # ULID generation for transaction IDs
```

Dev dependencies (for testing/linting):
```
pytest>=8.3.0             # Testing framework
pytest-asyncio>=0.24.0    # Async test support
pytest-cov>=5.0.0         # Coverage reporting
ruff>=0.6.0               # Linter + formatter
mypy>=1.11.0              # Type checker
factory-boy>=3.3.0        # Test fixtures
locust>=2.29.0            # Load testing
```

### Frontend Dependencies (installed automatically via Docker)

```
react@18.3                # UI framework
react-dom@18.3            # React DOM renderer
react-router-dom@6.26     # Client-side routing
axios@1.7                 # HTTP client
recharts@2.12             # Charting library
lucide-react@0.441        # Icon library
tailwindcss@3.4           # Utility-first CSS
vite@5.4                  # Build tool & dev server
typescript@5.5            # Type safety
```

### Install Docker (if not installed)

See **Step 1** in the Quick Start section below for platform-specific installation instructions.

## Quick Start (Zero to 100 — Step by Step)

### Step 1: Install Docker

Skip if already installed. Verify with `docker --version`.

**macOS:**
```bash
# Install Docker Desktop
brew install --cask docker

# Open Docker Desktop (REQUIRED — starts the Docker daemon)
open -a Docker

# Wait for Docker to start, then verify
docker --version
docker compose version
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl start docker && sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in, then verify:
docker --version
docker compose version
```

### Step 2: Clone the Repository

```bash
git clone git@github.com:razorpay/bee.git
cd bee
```

### Step 3: Verify Ports Are Free

```bash
# All four ports must be free. If any shows output, that port is in use.
lsof -i :8001    # API
lsof -i :3001    # Dashboard
lsof -i :5433    # PostgreSQL
lsof -i :6380    # Redis
```

If a port is busy, either stop the conflicting process or edit `docker-compose.yml` to change the port mapping (left side of the colon).

### Step 4: Start All Services

```bash
docker compose up --build -d
```

First run downloads Docker images (~2 GB) and builds containers. Subsequent runs are faster (cached layers).

### Step 5: Verify Everything Is Running

```bash
docker compose ps
```

Expected output — all services must show `running (healthy)`:
```
NAME               STATUS                  PORTS
bee-postgres-1     running (healthy)       0.0.0.0:5433->5432/tcp
bee-redis-1        running (healthy)       0.0.0.0:6380->6379/tcp
bee-fraud-api-1    running (healthy)       0.0.0.0:8001->8000/tcp
bee-dashboard-1    running                 0.0.0.0:3001->3000/tcp
```

If any service is not healthy, check logs:
```bash
docker compose logs fraud-api --tail 30
```

### Step 6: Verify API Is Responding

```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy","database":"connected","redis":"connected"}
```

### Step 7: Open the Dashboard

Open http://localhost:3001 in your browser. You should see the Fraud Detection Dashboard with metric cards (all showing 0 initially since no transactions exist yet).

### Step 8: Start Mock Traffic (Optional but Recommended)

This generates realistic transaction data so you can see the system in action:

```bash
docker compose --profile mock up -d mock-gen
```

Wait 10-15 seconds, then refresh the dashboard — you'll see transactions flowing, metrics updating, and alerts appearing.

### Step 9: Test Manually

Open http://localhost:8001/playground for an interactive API testing UI with pre-built examples.

---

**That's it!** No `.env` file needed (all configuration is embedded in `docker-compose.yml`). Database tables are created automatically on first boot via Alembic migrations. Redis requires no setup.

### What Happens Automatically on `docker compose up`:

1. PostgreSQL starts and creates the `fraud_detection` database
2. Redis starts
3. Fraud API starts → runs Alembic migrations (creates tables) → connects to PostgreSQL & Redis
4. Dashboard starts → Vite dev server serves React app with HMR
5. API is ready to receive transactions at `http://localhost:8001`
6. Dashboard connects to API at `http://localhost:8001` (configured via `VITE_API_URL`)

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | http://localhost:3001 | React fraud analyst dashboard |
| API Playground | http://localhost:8001/playground | Interactive API testing UI |
| API Docs (Swagger) | http://localhost:8001/docs | Auto-generated API documentation |
| Health Check | http://localhost:8001/health | Service health status |

## Start Mock Traffic Generator

The mock generator creates realistic transaction traffic (10 TPS with 5% fraud rate):

```bash
docker compose --profile mock up -d mock-gen
```

This generates 1000 simulated users and 500 merchants, injecting 7 fraud patterns:
- Account takeover (high-value burst from new device)
- Card testing (rapid small transactions)
- Velocity abuse (many transactions in short window)
- Geo-impossible travel
- Device spoofing (emulator/rooted)
- Merchant collusion patterns
- Round-amount laundering

## Testing Transactions Manually

### Via API Playground (Recommended)

Open http://localhost:8001/playground — it has pre-built presets and one-click execution for all endpoints.

### Via curl

**Submit a transaction for scoring:**

```bash
curl -X POST http://localhost:8001/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "merchant_id": "merchant_electronics_01",
    "amount": 50000,
    "currency": "INR",
    "device_fingerprint": "fp_abc123",
    "ip_address": "103.21.244.0",
    "geo_lat": 19.076,
    "geo_lon": 72.877,
    "channel": "mobile_app"
  }'
```

Response:
```json
{
  "transaction_id": "01JXYZ...",
  "risk_score": 72.5,
  "decision": "review",
  "sub_scores": {
    "behavior_analyzer": 85.0,
    "velocity_detector": 60.0,
    "device_risk": 45.0,
    "merchant_risk": 30.0,
    "geolocation": 10.0,
    "ip_intelligence": 20.0
  },
  "signals": ["Amount is 15x higher than user average", "New device detected"],
  "explanation": "High-risk: unusual spending pattern from unrecognized device"
}
```

**Simulate a high-risk transaction (TOR + VPN + high amount):**

```bash
curl -X POST http://localhost:8001/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_suspect",
    "merchant_id": "merchant_gambling_01",
    "amount": 200000,
    "currency": "INR",
    "device_fingerprint": "fp_emulator_001",
    "ip_address": "10.0.0.1",
    "geo_lat": 28.613,
    "geo_lon": 77.209,
    "channel": "web",
    "metadata": {
      "ip_is_tor": true,
      "ip_is_vpn": true,
      "device_is_emulator": true
    }
  }'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/transactions` | Submit transaction for fraud scoring |
| GET | `/api/v1/transactions` | List recent transactions |
| GET | `/api/v1/fraud/{transaction_id}` | Get fraud decision for a transaction |
| GET | `/api/v1/alerts` | List fraud alerts (filterable by decision) |
| PATCH | `/api/v1/alerts/{id}` | Take action on alert (approve/escalate/block) |
| GET | `/api/v1/users/{user_id}/risk-profile` | Get user risk profile |
| GET | `/api/v1/metrics` | Real-time fraud metrics |
| GET | `/api/v1/metrics/transactions?category=blocked` | Drill-down transactions by metric |
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |

### Alert Actions

```bash
# Block a transaction (moves to Block filter)
curl -X PATCH http://localhost:8001/api/v1/alerts/{alert_id} \
  -H "Content-Type: application/json" \
  -d '{"analyst_action": "block", "analyst_notes": "Confirmed fraud"}'

# Approve a transaction (clears from alerts)
curl -X PATCH http://localhost:8001/api/v1/alerts/{alert_id} \
  -H "Content-Type: application/json" \
  -d '{"analyst_action": "approve", "analyst_notes": "False positive"}'

# Escalate for senior review
curl -X PATCH http://localhost:8001/api/v1/alerts/{alert_id} \
  -H "Content-Type: application/json" \
  -d '{"analyst_action": "escalate", "analyst_notes": "Needs investigation"}'
```

## Dashboard Features

### Dashboard Page (/)
- **8 metric cards** — Total Transactions, Blocked, Under Review, Needs Verification, Approved, Fraud Rate, Amount at Risk, Analyst Reviewed
- **Click any card** to drill down into matching transactions with full risk detail
- **Risk Score Distribution** bar chart
- **Decision Distribution** pie chart
- **Recent High-Risk Transactions** list with signal preview
- **Top Risky Users** table (clickable to user profile)

### Fraud Alerts Page (/alerts)
- Filter by: All | Review | Block | Verify
- Click any alert to see full risk breakdown panel:
  - Risk score with color-coded circle
  - Module-by-module score breakdown with progress bars
  - Fraud signals with contextual icons
  - AI-generated explanation
- Analyst actions: **Approve** | **Escalate** | **Block**
  - Block moves the transaction to the "Block" filter
  - Approve clears it from the actionable queue

### Transactions Page (/transactions)
- Search and browse all processed transactions

### User Profile Page (/users/:userId)
- Risk level, transaction history, typical merchants

## Scoring Modules

| Module | Weight | What it detects |
|--------|--------|-----------------|
| Behavior Analyzer | 25% | Spending patterns vs user history (amount deviation) |
| Velocity Detector | 20% | Transaction frequency bursts (1min, 5min, 1hr windows) |
| Device Risk | 20% | Emulator, rooted device, new/shared device fingerprint |
| Merchant Risk | 15% | High-risk category (gambling, crypto), fraud association |
| Geolocation | 10% | Impossible travel, geo anomalies |
| IP Intelligence | 10% | VPN, TOR, proxy, datacenter IPs, country mismatch |

Final score = weighted sum of module scores. Decision thresholds:
- **0-30** → Approve (transaction passes)
- **31-60** → Verify (step-up authentication recommended)
- **61-80** → Review (manual analyst review required)
- **81-100** → Block (transaction blocked automatically)

## Project Structure

```
bee/
├── docker-compose.yml          # All services orchestration
├── Dockerfile                  # Python API container
├── Dockerfile.dashboard        # React dashboard container
├── pyproject.toml              # Python dependencies & tool config
├── alembic.ini                 # Database migration config
├── alembic/versions/           # Migration scripts
├── src/fraud_detection/
│   ├── main.py                 # FastAPI app + CORS + lifespan
│   ├── config.py               # Environment-based settings
│   ├── api/v1/                 # REST endpoints
│   ├── services/               # Business logic (pipeline, enrichment, decisions)
│   ├── scoring/                # 6 ML scoring modules
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── db/                     # Database engine & session
│   ├── cache/                  # Redis velocity/profile caches
│   ├── middleware/             # Correlation ID, logging, timing
│   └── mock/                   # Traffic generator (users, merchants, patterns)
├── dashboard/
│   ├── src/
│   │   ├── pages/              # Dashboard, Alerts, Transactions, UserProfile
│   │   ├── components/         # Reusable UI components
│   │   ├── hooks/              # React data hooks
│   │   ├── api/                # Axios client
│   │   └── types/              # TypeScript interfaces
│   └── package.json
└── tests/
    ├── unit/                   # Scoring, aggregator, decision engine tests
    ├── integration/            # API endpoint tests with real DB/Redis
    ├── e2e/                    # Full fraud scenario tests
    ├── performance/            # Locust load tests
    └── security/               # Injection, XSS, rate limiting tests
```

## Common Operations

### View logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f fraud-api
docker compose logs -f dashboard
docker compose logs -f mock-gen
```

### Stop everything

```bash
docker compose --profile mock down
```

### Stop and remove data (fresh start)

```bash
docker compose --profile mock down -v
```

This removes the PostgreSQL volume, so next `docker compose up` starts with a clean database.

### Rebuild after code changes

```bash
# Backend changes (Python)
docker compose up --build -d fraud-api

# Dashboard changes are auto-detected (volume-mounted with Vite HMR)
# If HMR doesn't pick up changes:
docker compose restart dashboard
```

### Connect to database directly

```bash
docker compose exec postgres psql -U fraud -d fraud_detection
```

Useful queries:
```sql
-- Count by decision
SELECT decision, count(*) FROM fraud_decisions GROUP BY decision;

-- Recent high-risk transactions
SELECT transaction_id, risk_score, decision, signals
FROM fraud_decisions WHERE risk_score > 60 ORDER BY decided_at DESC LIMIT 10;

-- Check user transaction history
SELECT t.transaction_id, t.amount, fd.risk_score, fd.decision
FROM transactions t JOIN fraud_decisions fd ON t.transaction_id = fd.transaction_id
WHERE t.user_id = 'user_0042' ORDER BY t.created_at DESC;
```

### Connect to Redis directly

```bash
docker compose exec redis redis-cli
```

Useful commands:
```
# Check velocity counters
ZCARD velocity:user:user_0042:1h

# Check user profile cache
HGETALL user_profile:user_0042

# Flush all caches (for testing)
FLUSHALL
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | (see docker-compose) | PostgreSQL async connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `APP_ENV` | `development` | Environment (development/production) |
| `APP_LOG_LEVEL` | `info` | Log level (debug/info/warning/error) |
| `ENRICHMENT_TIMEOUT_MS` | `50` | Max time for Redis enrichment lookups |
| `SCORING_TIMEOUT_MS` | `100` | Max time for scoring pipeline |
| `MOCK_TPS` | `10` | Mock generator transactions per second |
| `MOCK_FRAUD_RATE` | `0.05` | Fraction of mock transactions that are fraudulent |
| `MOCK_SEED` | `42` | Random seed for reproducible mock data |
| `VITE_API_URL` | `http://localhost:8001` | Backend URL for dashboard API calls |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| Frontend | React 18, TypeScript, Vite, TailwindCSS, Recharts, Lucide Icons |
| Database | PostgreSQL 16 |
| Cache | Redis 7 (velocity counters, profile caching) |
| Migrations | Alembic |
| Containerization | Docker, Docker Compose |
| Testing | pytest, pytest-asyncio, Locust (load), Playwright (UI) |
| Linting | Ruff, mypy |

## Troubleshooting

### Port conflict
If port 3001 or 8001 is already in use:
```bash
# Check what's using the port
lsof -i :3001
# Kill it or change the port in docker-compose.yml
```

### Dashboard shows "Network Error"
CORS issue. Ensure the dashboard URL is in the allowed origins in `src/fraud_detection/main.py`. Current allowed origins: `localhost:3001`, `localhost:5173`.

### API returns 500
Check logs:
```bash
docker compose logs fraud-api --tail 50
```

### Database migration issues
```bash
# Re-run migrations manually
docker compose exec fraud-api python -c "
from fraud_detection.db.migrate import run_migrations
import asyncio
asyncio.run(run_migrations())
"
```

### Fresh start (nuclear option)
```bash
docker compose --profile mock down -v
docker compose up --build -d
```

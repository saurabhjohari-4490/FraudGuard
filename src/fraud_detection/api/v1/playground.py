"""Interactive API Playground - test all endpoints from a single page."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["playground"])


@router.get("/playground", response_class=HTMLResponse)
async def playground():
    """Interactive API testing playground."""
    return HTMLResponse(content=PLAYGROUND_HTML)


PLAYGROUND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fraud Detection API Playground</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 24px; }
        h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; color: #f8fafc; }
        .subtitle { color: #94a3b8; margin-bottom: 32px; }

        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
        .card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
        .method { font-size: 12px; font-weight: 700; padding: 4px 8px; border-radius: 4px; font-family: monospace; }
        .method-post { background: #065f46; color: #6ee7b7; }
        .method-get { background: #1e40af; color: #93c5fd; }
        .method-patch { background: #92400e; color: #fcd34d; }
        .endpoint { font-family: monospace; font-size: 14px; color: #cbd5e1; }
        .card-title { font-size: 16px; font-weight: 600; color: #f1f5f9; margin-bottom: 4px; }
        .card-desc { font-size: 13px; color: #94a3b8; margin-bottom: 16px; }

        label { display: block; font-size: 12px; font-weight: 600; color: #94a3b8; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
        textarea, input, select { width: 100%; background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px 12px; color: #e2e8f0; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 13px; resize: vertical; }
        textarea:focus, input:focus, select:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
        textarea { min-height: 120px; }

        .btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
        .btn-primary { background: #3b82f6; color: white; }
        .btn-primary:hover { background: #2563eb; }
        .btn-success { background: #059669; color: white; }
        .btn-success:hover { background: #047857; }
        .btn-danger { background: #dc2626; color: white; }
        .btn-danger:hover { background: #b91c1c; }
        .btn:active { transform: scale(0.97); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }

        .response-box { margin-top: 16px; }
        .response-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
        .status { font-size: 13px; font-weight: 600; padding: 2px 8px; border-radius: 4px; }
        .status-2xx { background: #065f46; color: #6ee7b7; }
        .status-4xx { background: #92400e; color: #fcd34d; }
        .status-5xx { background: #7f1d1d; color: #fca5a5; }
        .response-time { font-size: 12px; color: #64748b; }
        .response-body { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 12px; white-space: pre-wrap; word-break: break-word; max-height: 300px; overflow-y: auto; color: #a5f3fc; }

        .params-row { display: flex; gap: 12px; margin-bottom: 12px; }
        .params-row > div { flex: 1; }

        .tabs { display: flex; gap: 4px; margin-bottom: 24px; flex-wrap: wrap; }
        .tab { padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; background: transparent; border: 1px solid #334155; color: #94a3b8; transition: all 0.15s; }
        .tab.active { background: #3b82f6; border-color: #3b82f6; color: white; }
        .tab:hover:not(.active) { border-color: #64748b; color: #e2e8f0; }

        .section { display: none; }
        .section.active { display: block; }

        .quick-fill { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
        .quick-fill button { padding: 4px 10px; font-size: 11px; border-radius: 4px; border: 1px solid #475569; background: #1e293b; color: #cbd5e1; cursor: pointer; }
        .quick-fill button:hover { background: #334155; }

        .mock-status-bar { display: flex; align-items: center; gap: 16px; padding: 12px 16px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; margin-bottom: 16px; }
        .mock-indicator { width: 10px; height: 10px; border-radius: 50%; }
        .mock-indicator.on { background: #22c55e; box-shadow: 0 0 8px #22c55e; }
        .mock-indicator.off { background: #64748b; }
        .mock-label { font-size: 14px; font-weight: 600; }
        .mock-stats { font-size: 12px; color: #94a3b8; margin-left: auto; }

        .btn-row { display: flex; gap: 8px; flex-wrap: wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Fraud Detection API Playground</h1>
        <p class="subtitle">Test all endpoints interactively. Pre-filled with example payloads.</p>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('create')">Create Transaction</div>
            <div class="tab" onclick="switchTab('list')">List Transactions</div>
            <div class="tab" onclick="switchTab('fraud')">Fraud Decision</div>
            <div class="tab" onclick="switchTab('metrics')">Metrics</div>
            <div class="tab" onclick="switchTab('alerts')">Alerts</div>
            <div class="tab" onclick="switchTab('alert-action')">Alert Action</div>
            <div class="tab" onclick="switchTab('users-list')">Users List</div>
            <div class="tab" onclick="switchTab('users')">User Profile</div>
            <div class="tab" onclick="switchTab('mock')">Mock Generator</div>
            <div class="tab" onclick="switchTab('health')">Health</div>
        </div>

        <!-- CREATE TRANSACTION -->
        <div id="section-create" class="section active">
            <div class="card">
                <div class="card-header">
                    <span class="method method-post">POST</span>
                    <span class="endpoint">/api/v1/transactions</span>
                </div>
                <div class="card-title">Submit Transaction for Fraud Scoring</div>
                <div class="card-desc">Ingests a transaction, runs the 6-module scoring pipeline in parallel, and returns a risk score + decision. Decisions: approve (0-30), verify (31-60), escalate (61-100). There is no auto-block — blocking is analyst-only.</div>

                <label>Quick Presets</label>
                <div class="quick-fill">
                    <button onclick="fillPreset('normal')">Normal Transaction</button>
                    <button onclick="fillPreset('suspicious')">Suspicious (VPN+Emulator)</button>
                    <button onclick="fillPreset('high_amount')">High Amount Anomaly</button>
                    <button onclick="fillPreset('velocity')">Velocity Burst</button>
                    <button onclick="fillPreset('new_device')">New Device + High Amount</button>
                </div>

                <label>Request Body (JSON)</label>
                <textarea id="create-body"></textarea>
                <br><br>
                <button class="btn btn-primary" onclick="sendRequest('create')">Send Request</button>
                <div id="response-create" class="response-box"></div>
            </div>
        </div>

        <!-- LIST TRANSACTIONS -->
        <div id="section-list" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/api/v1/transactions</span>
                </div>
                <div class="card-title">List & Search Transactions</div>
                <div class="card-desc">Search transactions with filters. Supports pagination, user/merchant filters, and text search.</div>

                <div class="params-row">
                    <div><label>Search (q)</label><input id="list-q" placeholder="transaction_id, user_id, or merchant_id"></div>
                    <div><label>User ID</label><input id="list-user" placeholder="e.g. user_0042"></div>
                </div>
                <div class="params-row">
                    <div><label>Merchant ID</label><input id="list-merchant" placeholder="e.g. merchant_0010"></div>
                    <div><label>Page</label><input id="list-page" type="number" value="1" min="1"></div>
                    <div><label>Limit</label><input id="list-limit" type="number" value="20" min="1" max="100"></div>
                </div>
                <br>
                <button class="btn btn-primary" onclick="sendRequest('list')">Send Request</button>
                <div id="response-list" class="response-box"></div>
            </div>
        </div>

        <!-- GET FRAUD DECISION -->
        <div id="section-fraud" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/api/v1/fraud/{transaction_id}</span>
                </div>
                <div class="card-title">Get Fraud Decision Details</div>
                <div class="card-desc">Returns the full fraud assessment for a specific transaction including sub-scores, signals, and explanation.</div>

                <label>Transaction ID</label>
                <input id="fraud-txn-id" placeholder="e.g. txn-manual-001 (auto-fills after Create Transaction)">
                <br><br>
                <button class="btn btn-primary" onclick="sendRequest('fraud')">Send Request</button>
                <div id="response-fraud" class="response-box"></div>
            </div>
        </div>

        <!-- METRICS -->
        <div id="section-metrics" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/api/v1/metrics</span>
                </div>
                <div class="card-title">Platform Metrics</div>
                <div class="card-desc">Aggregate metrics: total transactions, fraud rate (critical + escalated / total), decision counts, risk distribution histogram, top risky users, recent high-risk transactions, and blocked count (analyst actions).</div>
                <button class="btn btn-primary" onclick="sendRequest('metrics')">Send Request</button>
                <div id="response-metrics" class="response-box"></div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/api/v1/metrics/transactions?category=...</span>
                </div>
                <div class="card-title">Metric Drill-Down (Transactions by Category)</div>
                <div class="card-desc">Get transactions for a specific metric category. Used by the dashboard for drill-down views when clicking metric cards. Each transaction includes sub_scores, signals, explanation, and analyst_action.</div>

                <div class="params-row">
                    <div><label>Category</label>
                        <select id="metrics-txns-category">
                            <option value="all">All Transactions</option>
                            <option value="critical">Critical Risk (score >80, decision=escalate)</option>
                            <option value="escalate">Escalated (score 61-80, decision=escalate)</option>
                            <option value="verify">Verification Pending (score 31-60, decision=verify)</option>
                            <option value="approved">Approved (score 0-30, decision=approve)</option>
                            <option value="blocked">Blocked by Analyst (analyst_action=block)</option>
                            <option value="fraud_rate">Flagged (critical + escalated combined)</option>
                            <option value="high_risk">High Risk (score >70)</option>
                            <option value="pending">Pending Review (escalate/verify, no analyst action)</option>
                            <option value="reviewed">Analyst Reviewed (has analyst_action)</option>
                            <option value="amount_at_risk">Amount at Risk (non-approved txns)</option>
                        </select>
                    </div>
                </div>
                <br>
                <button class="btn btn-primary" onclick="sendRequest('metrics-txns')">Send Request</button>
                <div id="response-metrics-txns" class="response-box"></div>
            </div>
        </div>

        <!-- ALERTS LIST -->
        <div id="section-alerts" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/api/v1/alerts</span>
                </div>
                <div class="card-title">Alert Queue</div>
                <div class="card-desc">Returns transactions requiring analyst review. Critical = score >80 (auto-escalated), Escalated = score 61-80, Verify = score 31-60. There is NO auto-block — the "block" filter shows only transactions manually blocked by an analyst.</div>

                <div class="params-row">
                    <div><label>Decision Filter</label>
                        <select id="alerts-decision">
                            <option value="">All (critical + escalate + verify)</option>
                            <option value="critical">Critical Risk (score >80)</option>
                            <option value="escalate">Escalated (score 61-80)</option>
                            <option value="verify">Verification Pending (score 31-60)</option>
                            <option value="block">Blocked by Analyst (manual action only)</option>
                        </select>
                    </div>
                    <div><label>Limit</label><input id="alerts-limit" type="number" value="20" min="1" max="500"></div>
                </div>
                <br>
                <button class="btn btn-primary" onclick="sendRequest('alerts')">Send Request</button>
                <div id="response-alerts" class="response-box"></div>
            </div>
        </div>

        <!-- ALERT ACTION (PATCH) -->
        <div id="section-alert-action" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-patch">PATCH</span>
                    <span class="endpoint">/api/v1/alerts/{alert_id}</span>
                </div>
                <div class="card-title">Update Alert (Analyst Action)</div>
                <div class="card-desc">Submit an analyst decision on a flagged alert. Actions: Approve (verified safe → "APPROVED BY ANALYST"), Block (confirm fraud → "BLOCKED BY ANALYST"), Escalate (needs senior review → "ESCALATED BY ANALYST"). Alert stays in list with updated badge.</div>

                <div class="params-row">
                    <div><label>Alert ID</label><input id="alert-id" placeholder="UUID from alert list (e.g. 760b8718-...)"></div>
                    <div><label>Action</label>
                        <select id="alert-action">
                            <option value="approve">Approve (verified safe)</option>
                            <option value="block">Block (confirm fraud - BLOCKED BY ANALYST)</option>
                            <option value="escalate">Escalate (needs senior review)</option>
                        </select>
                    </div>
                </div>
                <div class="params-row">
                    <div><label>Analyst Notes (optional)</label><input id="alert-notes" placeholder="e.g. Verified with customer, legitimate purchase"></div>
                </div>
                <br>
                <button class="btn btn-primary" onclick="sendRequest('alert-action')">Send Request</button>
                <div id="response-alert-action" class="response-box"></div>
            </div>
        </div>

        <!-- USERS LIST -->
        <div id="section-users-list" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/api/v1/users</span>
                </div>
                <div class="card-title">List Users</div>
                <div class="card-desc">List all users with risk summary. Returns: user_id, transaction_count, total_amount, avg_risk_score, max_risk_score, risk_level (computed from avg score), decision_counts. Optimized single-query (no N+1).</div>

                <div class="params-row">
                    <div><label>Search</label><input id="users-list-search" placeholder="e.g. user_004"></div>
                    <div><label>Page</label><input id="users-list-page" type="number" value="1" min="1"></div>
                    <div><label>Limit</label><input id="users-list-limit" type="number" value="20" min="1" max="100"></div>
                </div>
                <br>
                <button class="btn btn-primary" onclick="sendRequest('users-list')">Send Request</button>
                <div id="response-users-list" class="response-box"></div>
            </div>
        </div>

        <!-- USER PROFILE -->
        <div id="section-users" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/api/v1/users/{user_id}/risk-profile</span>
                </div>
                <div class="card-title">User Risk Profile</div>
                <div class="card-desc">Full risk profile for a user: transaction stats, risk level (computed from avg risk score: >80=critical, >60=high, >30=medium, ≤30=low), decision distribution, typical merchants, and recent 20 transactions.</div>

                <label>User ID</label>
                <input id="user-id" placeholder="e.g. user_0042" value="user_0001">
                <br><br>
                <button class="btn btn-primary" onclick="sendRequest('users')">Send Request</button>
                <div id="response-users" class="response-box"></div>
            </div>
        </div>

        <!-- MOCK GENERATOR -->
        <div id="section-mock" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/api/v1/mock/status</span>
                </div>
                <div class="card-title">Mock Transaction Generator</div>
                <div class="card-desc">Control the built-in mock transaction generator. Start/stop traffic generation and configure TPS and fraud injection rate.</div>

                <div id="mock-status-display" class="mock-status-bar">
                    <div class="mock-indicator off" id="mock-dot"></div>
                    <span class="mock-label" id="mock-label">Loading...</span>
                    <span class="mock-stats" id="mock-stats"></span>
                </div>

                <div class="params-row">
                    <div><label>TPS (Transactions Per Second)</label><input id="mock-tps" type="number" value="10" min="1" max="100"></div>
                    <div><label>Fraud Rate (0.0 - 1.0)</label><input id="mock-fraud-rate" type="number" value="0.05" min="0" max="1" step="0.01"></div>
                </div>
                <br>
                <div class="btn-row">
                    <button class="btn btn-success" onclick="sendRequest('mock-start')">Start Generator</button>
                    <button class="btn btn-danger" onclick="sendRequest('mock-stop')">Stop Generator</button>
                    <button class="btn btn-primary" onclick="sendRequest('mock-status')">Refresh Status</button>
                </div>
                <div id="response-mock-status" class="response-box"></div>
                <div id="response-mock-start" class="response-box"></div>
                <div id="response-mock-stop" class="response-box"></div>
            </div>
        </div>

        <!-- HEALTH -->
        <div id="section-health" class="section">
            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/health</span>
                </div>
                <div class="card-title">Health Check</div>
                <div class="card-desc">Basic liveness probe. Returns 200 if the service is running.</div>
                <button class="btn btn-primary" onclick="sendRequest('health')">Send Request</button>
                <div id="response-health" class="response-box"></div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="method method-get">GET</span>
                    <span class="endpoint">/ready</span>
                </div>
                <div class="card-title">Readiness Check</div>
                <div class="card-desc">Checks database and Redis connectivity. Returns 200 only when all dependencies are reachable.</div>
                <button class="btn btn-primary" onclick="sendRequest('ready')">Send Request</button>
                <div id="response-ready" class="response-box"></div>
            </div>
        </div>
    </div>

    <script>
        const BASE = window.location.origin;

        const PRESETS = {
            normal: {
                transaction_id: "txn-playground-001",
                user_id: "user_0042",
                merchant_id: "merchant_0010",
                amount: 2500.00,
                currency: "INR",
                card_bin: "411111",
                device_fingerprint: "device_user42_mobile",
                ip_address: "103.21.58.100",
                geo_lat: 28.6139,
                geo_lon: 77.2090,
                channel: "mobile",
                metadata: { merchant_category: "retail" }
            },
            suspicious: {
                transaction_id: "txn-playground-002",
                user_id: "user_0042",
                merchant_id: "test_gambling_site",
                amount: 250000.00,
                currency: "INR",
                device_fingerprint: "emulator_suspect_99",
                ip_address: "185.220.101.5",
                geo_lat: 40.7128,
                geo_lon: -74.0060,
                channel: "web",
                metadata: {
                    merchant_category: "gambling",
                    ip_is_vpn: true,
                    ip_is_tor: true,
                    device_is_emulator: true,
                    device_is_rooted: true
                }
            },
            high_amount: {
                transaction_id: "txn-playground-003",
                user_id: "user_0042",
                merchant_id: "merchant_0050",
                amount: 450000.00,
                currency: "INR",
                device_fingerprint: "device_user42_mobile",
                ip_address: "103.21.58.100",
                geo_lat: 28.6139,
                geo_lon: 77.2090,
                channel: "web",
                metadata: { merchant_category: "electronics" }
            },
            velocity: {
                transaction_id: "txn-playground-004",
                user_id: "user_0042",
                merchant_id: "merchant_0010",
                amount: 9999.00,
                currency: "INR",
                device_fingerprint: "device_user42_mobile",
                ip_address: "103.21.58.100",
                geo_lat: 28.6139,
                geo_lon: 77.2090,
                channel: "mobile",
                metadata: { merchant_category: "retail", note: "Send this multiple times quickly to trigger velocity detection" }
            },
            new_device: {
                transaction_id: "txn-playground-005",
                user_id: "user_0042",
                merchant_id: "merchant_0010",
                amount: 150000.00,
                currency: "INR",
                device_fingerprint: "brand_new_device_" + Date.now(),
                ip_address: "103.21.58.100",
                geo_lat: 28.6139,
                geo_lon: 77.2090,
                channel: "mobile",
                metadata: { merchant_category: "electronics" }
            }
        };

        function fillPreset(name) {
            const preset = {...PRESETS[name], transaction_id: "txn-" + Math.random().toString(36).slice(2, 10)};
            if (name === 'new_device') preset.device_fingerprint = "brand_new_device_" + Date.now();
            document.getElementById('create-body').value = JSON.stringify(preset, null, 2);
        }

        // Initialize with normal preset
        fillPreset('normal');

        function switchTab(name) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('section-' + name).classList.add('active');

            // Auto-refresh mock status when switching to mock tab
            if (name === 'mock') refreshMockStatus();
        }

        async function refreshMockStatus() {
            try {
                const res = await fetch(BASE + '/api/v1/mock/status');
                const data = await res.json();
                const dot = document.getElementById('mock-dot');
                const label = document.getElementById('mock-label');
                const stats = document.getElementById('mock-stats');

                dot.className = 'mock-indicator ' + (data.enabled ? 'on' : 'off');
                label.textContent = data.enabled ? `Running at ${data.tps} TPS` : 'Stopped';
                stats.textContent = data.enabled
                    ? `Sent: ${data.stats.sent} | Success: ${data.stats.success} | Errors: ${data.stats.errors}`
                    : `Last run: ${data.stats.sent} sent`;

                // Update input fields with current values
                document.getElementById('mock-tps').value = data.tps;
                document.getElementById('mock-fraud-rate').value = data.fraud_rate;
            } catch (e) {
                document.getElementById('mock-label').textContent = 'Error fetching status';
            }
        }

        async function sendRequest(type) {
            const responseDiv = document.getElementById('response-' + type);
            if (responseDiv) responseDiv.innerHTML = '<div style="color:#64748b">Sending...</div>';

            let url, method, body;
            const start = performance.now();

            switch(type) {
                case 'create':
                    url = BASE + '/api/v1/transactions';
                    method = 'POST';
                    body = document.getElementById('create-body').value;
                    break;

                case 'list': {
                    const params = new URLSearchParams();
                    const q = document.getElementById('list-q').value;
                    const user = document.getElementById('list-user').value;
                    const merchant = document.getElementById('list-merchant').value;
                    const page = document.getElementById('list-page').value;
                    const limit = document.getElementById('list-limit').value;
                    if (q) params.set('q', q);
                    if (user) params.set('user_id', user);
                    if (merchant) params.set('merchant_id', merchant);
                    if (page) params.set('page', page);
                    if (limit) params.set('limit', limit);
                    url = BASE + '/api/v1/transactions?' + params.toString();
                    method = 'GET';
                    break;
                }

                case 'fraud': {
                    const txnId = document.getElementById('fraud-txn-id').value;
                    if (!txnId) { responseDiv.innerHTML = '<div style="color:#fca5a5">Enter a transaction ID</div>'; return; }
                    url = BASE + '/api/v1/fraud/' + txnId;
                    method = 'GET';
                    break;
                }

                case 'metrics':
                    url = BASE + '/api/v1/metrics';
                    method = 'GET';
                    break;

                case 'metrics-txns': {
                    const cat = document.getElementById('metrics-txns-category').value;
                    url = BASE + '/api/v1/metrics/transactions?category=' + cat;
                    method = 'GET';
                    break;
                }

                case 'alerts': {
                    const alertParams = new URLSearchParams();
                    const decision = document.getElementById('alerts-decision').value;
                    const alertLimit = document.getElementById('alerts-limit').value;
                    if (decision) alertParams.set('decision', decision);
                    if (alertLimit) alertParams.set('limit', alertLimit);
                    url = BASE + '/api/v1/alerts?' + alertParams.toString();
                    method = 'GET';
                    break;
                }

                case 'alert-action': {
                    const alertId = document.getElementById('alert-id').value;
                    if (!alertId) { responseDiv.innerHTML = '<div style="color:#fca5a5">Enter an alert ID (get one from Alerts tab)</div>'; return; }
                    url = BASE + '/api/v1/alerts/' + alertId;
                    method = 'PATCH';
                    const actionBody = { analyst_action: document.getElementById('alert-action').value };
                    const notes = document.getElementById('alert-notes').value;
                    if (notes) actionBody.analyst_notes = notes;
                    body = JSON.stringify(actionBody);
                    break;
                }

                case 'users-list': {
                    const ulParams = new URLSearchParams();
                    const search = document.getElementById('users-list-search').value;
                    const uPage = document.getElementById('users-list-page').value;
                    const uLimit = document.getElementById('users-list-limit').value;
                    if (search) ulParams.set('search', search);
                    if (uPage) ulParams.set('page', uPage);
                    if (uLimit) ulParams.set('limit', uLimit);
                    url = BASE + '/api/v1/users?' + ulParams.toString();
                    method = 'GET';
                    break;
                }

                case 'users': {
                    const userId = document.getElementById('user-id').value;
                    if (!userId) { responseDiv.innerHTML = '<div style="color:#fca5a5">Enter a user ID</div>'; return; }
                    url = BASE + '/api/v1/users/' + userId + '/risk-profile';
                    method = 'GET';
                    break;
                }

                case 'mock-status':
                    url = BASE + '/api/v1/mock/status';
                    method = 'GET';
                    break;

                case 'mock-start':
                    url = BASE + '/api/v1/mock/start';
                    method = 'POST';
                    body = JSON.stringify({
                        tps: parseInt(document.getElementById('mock-tps').value) || 10,
                        fraud_rate: parseFloat(document.getElementById('mock-fraud-rate').value) || 0.05
                    });
                    break;

                case 'mock-stop':
                    url = BASE + '/api/v1/mock/stop';
                    method = 'POST';
                    break;

                case 'health':
                    url = BASE + '/health';
                    method = 'GET';
                    break;

                case 'ready':
                    url = BASE + '/ready';
                    method = 'GET';
                    break;
            }

            try {
                const opts = { method, headers: { 'Content-Type': 'application/json' } };
                if (body) opts.body = body;
                const res = await fetch(url, opts);
                const elapsed = Math.round(performance.now() - start);
                const data = await res.json();
                const statusClass = res.status < 300 ? 'status-2xx' : res.status < 500 ? 'status-4xx' : 'status-5xx';

                if (responseDiv) {
                    responseDiv.innerHTML = `
                        <div class="response-header">
                            <span class="status ${statusClass}">${res.status} ${res.statusText}</span>
                            <span class="response-time">${elapsed}ms</span>
                        </div>
                        <div class="response-body">${syntaxHighlight(JSON.stringify(data, null, 2))}</div>
                    `;
                }

                // Auto-fill fraud lookup field with transaction_id from create response
                if (type === 'create' && data.transaction_id) {
                    document.getElementById('fraud-txn-id').value = data.transaction_id;
                }

                // Auto-fill alert ID from first alert in list
                if (type === 'alerts' && data.alerts && data.alerts.length > 0) {
                    document.getElementById('alert-id').value = data.alerts[0].id;
                }

                // Refresh mock status display after start/stop
                if (type === 'mock-start' || type === 'mock-stop' || type === 'mock-status') {
                    refreshMockStatus();
                }
            } catch (err) {
                if (responseDiv) responseDiv.innerHTML = `<div style="color:#fca5a5">Error: ${err.message}</div>`;
            }
        }

        function syntaxHighlight(json) {
            return json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                .replace(/"(\\\\u[a-zA-Z0-9]{4}|\\\\[^u]|[^\\\\"])*"(\\s*:)?/g, (match) => {
                    let cls = 'color:#a5f3fc';  // string
                    if (/:$/.test(match)) cls = 'color:#c4b5fd';  // key
                    else if (/true|false/.test(match)) cls = 'color:#6ee7b7';  // bool
                    else if (/null/.test(match)) cls = 'color:#f87171';  // null
                    return '<span style="' + cls + '">' + match + '</span>';
                })
                .replace(/\\b(\\d+\\.?\\d*)\\b/g, '<span style="color:#fcd34d">$1</span>');
        }

        // Auto-refresh mock status on page load
        refreshMockStatus();
    </script>
</body>
</html>
"""

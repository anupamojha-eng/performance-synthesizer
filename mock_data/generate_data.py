#!/usr/bin/env python3
"""
Generate realistic mock data for the performance-synthesizer project.
Outputs: epics.json, tickets.json, engineers.json, commits.json
Run: python mock_data/generate_data.py
"""

import json
import os
import random
import time
from datetime import datetime, timedelta

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Static definitions ────────────────────────────────────────────────────────

ENGINEERS = [
    {
        "engineer_id": "jane",
        "name": "Jane Kim",
        "role": "senior",
        "specialization": ["architecture", "security", "mentoring"],
        "tenure_months": 48,
        "team": "Platform Core",
        "past_performance": "exceeds",
    },
    {
        "engineer_id": "mike",
        "name": "Mike Torres",
        "role": "mid",
        "specialization": ["backend", "databases", "api"],
        "tenure_months": 20,
        "team": "Platform Core",
        "past_performance": "meets",
    },
    {
        "engineer_id": "sarah",
        "name": "Sarah Chen",
        "role": "junior",
        "specialization": ["frontend", "testing", "documentation"],
        "tenure_months": 6,
        "team": "Platform Core",
        "past_performance": "developing",
    },
]

EPICS = [
    {
        "id": "epic-oauth",
        "epic_key": "PERF-EPIC-1",
        "title": "Migrate Auth to OAuth2",
        "goal_statement": "Replace legacy auth with industry-standard OAuth2, improve security, enable SSO",
        "start_date": "2024-04-01",
        "end_date": "2024-05-31",
        "criticality": "critical",
        "status": "completed",
        "required_by": "Security audit requires modern auth",
        "lead_engineer": "jane",
        "estimated_total_hours": 200,
    },
    {
        "id": "epic-payment",
        "epic_key": "PERF-EPIC-2",
        "title": "Payment System Refactor",
        "goal_statement": "Refactor payment processor, add retry logic, reduce failed transactions by 50%",
        "start_date": "2024-04-15",
        "end_date": "2024-06-15",
        "criticality": "high",
        "status": "completed",
        "required_by": "Revenue impact from failed payments",
        "lead_engineer": "mike",
        "estimated_total_hours": 180,
    },
    {
        "id": "epic-search",
        "epic_key": "PERF-EPIC-3",
        "title": "Search Performance Optimization",
        "goal_statement": "Optimize search latency from 2s to <200ms using indexed queries",
        "start_date": "2024-05-01",
        "end_date": "2024-06-30",
        "criticality": "medium",
        "status": "completed",
        "required_by": "Improve user experience on search-heavy workloads",
        "lead_engineer": "jane",
        "estimated_total_hours": 120,
    },
    {
        "id": "epic-rate-limit",
        "epic_key": "PERF-EPIC-4",
        "title": "API Rate Limiting & Security",
        "goal_statement": "Implement rate limiting, prevent abuse, document limits for partners",
        "start_date": "2024-05-15",
        "end_date": "2024-06-30",
        "criticality": "high",
        "status": "completed",
        "required_by": "Prevent API abuse, stabilize service",
        "lead_engineer": "jane",
        "estimated_total_hours": 100,
    },
]

# (title, base_complexity) — ~45 per epic so total ≈ 180 tickets
TICKET_TEMPLATES = {
    "epic-oauth": [
        ("Audit existing session-based auth codebase", "small"),
        ("Design OAuth2 provider integration architecture", "large"),
        ("Evaluate OAuth2 providers (Auth0 vs Okta vs Cognito)", "small"),
        ("Set up Auth0 tenant and application config", "medium"),
        ("Implement authorization code flow", "large"),
        ("Add PKCE support for public clients", "large"),
        ("Create secure token storage service", "medium"),
        ("Implement JWT validation middleware", "medium"),
        ("Migrate existing user sessions to OAuth tokens", "epic"),
        ("Add SSO login endpoints", "medium"),
        ("Update user model for OAuth2 fields (sub, iss, aud)", "small"),
        ("Implement refresh token rotation logic", "medium"),
        ("Add token revocation endpoint", "small"),
        ("Write OAuth2 auth middleware for FastAPI", "medium"),
        ("Add scope-based authorization decorator", "medium"),
        ("Implement client credential flow for service accounts", "large"),
        ("Update login/logout UI components for OAuth redirect", "medium"),
        ("Add MFA trigger via OAuth ACR claims", "large"),
        ("Write integration tests for all auth flows", "large"),
        ("Security review: OAuth token handling and storage", "medium"),
        ("Document OAuth2 flow for internal teams", "small"),
        ("Fix CORS headers on auth endpoints", "trivial"),
        ("Add structured audit logging for auth events", "small"),
        ("Load test new auth endpoints at 500 req/s", "medium"),
        ("Deploy OAuth2 config to staging environment", "trivial"),
        ("Validate SSO with partner identity provider (Okta)", "medium"),
        ("Add fallback for token refresh failures", "small"),
        ("Update OpenAPI docs with auth security schemes", "small"),
        ("Create developer guide for OAuth integration", "small"),
        ("Performance tune JWT validation path (cache JWKS)", "medium"),
        ("End-to-end QA sign-off on all auth flows", "large"),
        ("Fix edge case: concurrent refresh token requests", "medium"),
        ("Add rate limiting on /auth/token endpoint", "small"),
        ("Implement silent token renewal in frontend (iframe)", "medium"),
        ("Remove legacy BasicAuth code and feature flag", "small"),
        ("Add Grafana dashboard for auth failure rates", "medium"),
        ("Create runbook for OAuth config rotation", "trivial"),
        ("Penetration test new auth endpoints", "large"),
        ("Fix token expiry off-by-one in refresh scheduler", "trivial"),
        ("Update CI pipeline to run auth integration tests", "small"),
        ("Post-migration validation and stakeholder sign-off", "medium"),
        ("Add distributed tracing spans to auth service", "medium"),
        ("Write chaos test: Auth0 outage fallback behavior", "medium"),
        ("Implement device authorization flow for CLI tools", "large"),
        ("Update user onboarding flow for new OAuth login", "medium"),
    ],
    "epic-payment": [
        ("Audit current Stripe integration and failure modes", "medium"),
        ("Design retry logic and idempotency strategy", "large"),
        ("Implement idempotency keys on payment creation", "medium"),
        ("Add exponential backoff retry for failed charges", "medium"),
        ("Improve Stripe webhook handler reliability", "medium"),
        ("Add payment failure classification (network vs card vs fraud)", "medium"),
        ("Refactor refund flow for partial refunds", "medium"),
        ("Build payment analytics dashboard (failure rates by type)", "large"),
        ("Migrate payment logs to structured JSON format", "small"),
        ("Write unit tests for retry logic", "medium"),
        ("Add integration tests against Stripe sandbox", "large"),
        ("Handle 3DS authentication edge cases in checkout", "large"),
        ("Implement payment method vault for saved cards", "large"),
        ("Add currency conversion support for international customers", "medium"),
        ("Fix race condition in concurrent payment creation", "medium"),
        ("Add payment processor circuit breaker with half-open state", "medium"),
        ("Implement payment status polling endpoint", "small"),
        ("Add PagerDuty alerting for payment failure rate > 2%", "medium"),
        ("Update payment API documentation", "small"),
        ("Create on-call runbook for payment failures", "small"),
        ("Load test payment endpoint at 10x current traffic", "medium"),
        ("Fix decimal precision bug in multi-currency amount calculation", "trivial"),
        ("Add soft-delete for payment records (GDPR compliance)", "small"),
        ("Implement payment dispute handling workflow", "large"),
        ("Reduce payment confirmation latency (target <500ms)", "medium"),
        ("Add Stripe webhook signature validation", "small"),
        ("Migrate to Stripe SDK v3", "medium"),
        ("Write chaos test for payment service timeout scenarios", "medium"),
        ("Document payment retry behavior for support team", "small"),
        ("Deploy payment changes to staging", "trivial"),
        ("QA sign-off on all payment flows", "medium"),
        ("Fix duplicate charge edge case on network timeout", "medium"),
        ("Add email notification on payment failure with retry info", "small"),
        ("Implement partial capture for hotel/rental payments", "medium"),
        ("Add payment event stream for analytics team (Kafka)", "large"),
        ("Performance profile payment service cold path", "medium"),
        ("Add per-merchant payment limit configuration", "medium"),
        ("Write developer guide for payment integration", "small"),
        ("Implement subscription payment auto-renewal logic", "large"),
        ("Add payment method health check endpoint", "trivial"),
        ("Security review: PCI-DSS compliance check", "medium"),
        ("Migrate payment config to Vault secrets manager", "medium"),
        ("Add Datadog APM traces to payment critical path", "small"),
        ("Fix webhook replay attack vulnerability", "medium"),
        ("Final regression test: end-to-end checkout flow", "large"),
    ],
    "epic-search": [
        ("Profile existing search query performance with EXPLAIN ANALYZE", "medium"),
        ("Identify N+1 queries in product search path", "small"),
        ("Design indexing strategy for product catalog", "large"),
        ("Add GIN indexes on JSONB search columns", "medium"),
        ("Implement full-text search with tsvector and tsquery", "large"),
        ("Add query result caching layer with Redis (TTL=60s)", "large"),
        ("Optimize search ranking algorithm with TF-IDF weights", "large"),
        ("Implement fuzzy matching for typo tolerance", "medium"),
        ("Add faceted search filters (category, price, rating)", "medium"),
        ("Implement search suggestions / autocomplete endpoint", "medium"),
        ("Add cursor-based pagination to search results", "small"),
        ("Write search performance benchmarks (p50/p95/p99)", "medium"),
        ("Reduce search response payload (field projection)", "small"),
        ("Add search event tracking for analytics", "medium"),
        ("Implement search result snippet highlighting", "small"),
        ("Load test search at 50 concurrent users", "medium"),
        ("Fix search returning stale data after product update", "small"),
        ("Add search health check and readiness probe", "trivial"),
        ("Document search API endpoints in OpenAPI", "small"),
        ("QA sign-off on search performance improvements", "medium"),
        ("Migrate search config to environment variables", "trivial"),
        ("Add Datadog monitors for search latency p99 > 200ms", "small"),
        ("Implement incremental index rebuild on data change", "medium"),
        ("Fix unicode normalization in search query parser", "small"),
        ("Add boolean search operators (AND, OR, NOT)", "medium"),
        ("Implement cache warming strategy at startup", "medium"),
        ("Write unit tests for search ranking and scoring", "medium"),
        ("Create search query playground for QA team", "small"),
        ("Implement search A/B testing framework", "large"),
        ("Document search optimization decisions and benchmarks", "small"),
        ("Add search result deduplication logic", "small"),
        ("Implement synonym expansion for search terms", "medium"),
        ("Add geo-proximity search support", "large"),
        ("Fix search timeout for long-running queries (>3s)", "medium"),
        ("Implement search index version migration strategy", "medium"),
        ("Add multi-language support to full-text search", "large"),
        ("Write search integration tests with realistic dataset", "medium"),
        ("Optimize search for mobile clients (lighter payload)", "small"),
        ("Add relevance tuning admin panel", "large"),
        ("Performance regression tests post-deployment", "medium"),
        ("Sarah: write search API usage guide for frontend team", "small"),
        ("Sarah: add search error state UI handling", "small"),
        ("Sarah: write test fixtures for search integration tests", "small"),
        ("Sarah: document known search limitations for product team", "trivial"),
        ("Sarah: QA search on mobile viewports", "small"),
    ],
    "epic-rate-limit": [
        ("Design rate limiting strategy (per-IP, per-user, per-tenant)", "medium"),
        ("Implement token bucket algorithm", "large"),
        ("Add Redis-backed rate limit counters with atomic ops", "medium"),
        ("Implement per-endpoint rate limit configuration", "medium"),
        ("Add X-RateLimit-* headers to API responses", "small"),
        ("Create rate limit bypass list for internal services", "small"),
        ("Implement IP allowlist for trusted partner networks", "small"),
        ("Add 429 Too Many Requests error response schema", "trivial"),
        ("Write unit tests for token bucket algorithm", "medium"),
        ("Add integration tests for rate limit enforcement", "medium"),
        ("Load test rate limiter at 1000 req/s sustained", "medium"),
        ("Add Prometheus metrics for rate limit violations", "small"),
        ("Implement distributed rate limiting across multiple nodes", "large"),
        ("Build rate limit analytics dashboard", "medium"),
        ("Document rate limits for partner API consumers", "medium"),
        ("Create developer FAQ for rate limiting behavior", "small"),
        ("Implement grace period for new users (first 7 days)", "medium"),
        ("Add Retry-After header in 429 responses", "small"),
        ("Fix race condition in concurrent counter increments", "medium"),
        ("Deploy rate limiter to staging environment", "trivial"),
        ("QA sign-off on rate limiting behavior", "small"),
        ("Add alerting for sudden 10x traffic spikes", "small"),
        ("Implement sliding window algorithm as alternative", "large"),
        ("Write chaos test: Redis failure graceful degradation", "medium"),
        ("Update security runbook with rate limit procedures", "small"),
        ("Add per-API-key rate limits for partner access tiers", "medium"),
        ("Implement ops team override endpoint (with audit log)", "small"),
        ("Performance profile rate limiter middleware overhead", "medium"),
        ("Document rate limit recovery and backoff process", "small"),
        ("Final security review of rate limit implementation", "medium"),
        ("Add rate limit config hot-reload without restart", "medium"),
        ("Implement tiered rate limits (free/pro/enterprise)", "large"),
        ("Write partner migration guide for rate limit adoption", "small"),
        ("Add rate limit simulation tool for testing", "medium"),
        ("Create Postman collection demonstrating rate limit behavior", "small"),
        ("Fix rate limit not resetting correctly at window boundary", "medium"),
        ("Add rate limit status endpoint for partner dashboards", "small"),
        ("Implement DDoS protection layer above rate limiter", "large"),
        ("Write runbook for rate limit incident response", "small"),
        ("Post-deployment validation: verify limits in production", "medium"),
        ("Sarah: write rate limit API usage examples", "small"),
        ("Sarah: add rate limit exceeded UI error handling", "small"),
        ("Sarah: document rate limit headers for SDK consumers", "small"),
        ("Sarah: QA rate limit behavior in staging environment", "small"),
        ("Sarah: update integration test suite for rate limits", "small"),
    ],
}

# Engineer assignment weights per epic
ENGINEER_WEIGHTS = {
    "epic-oauth":      {"jane": 0.60, "mike": 0.25, "sarah": 0.15},
    "epic-payment":    {"mike": 0.50, "jane": 0.30, "sarah": 0.20},
    "epic-search":     {"jane": 0.40, "sarah": 0.35, "mike": 0.25},
    "epic-rate-limit": {"jane": 0.55, "mike": 0.30, "sarah": 0.15},
}

COMPLEXITY_HOURS = {
    "trivial": (4, 8),
    "small":   (8, 16),
    "medium":  (16, 32),
    "large":   (32, 48),
    "epic":    (48, 80),
}

BLOCKER_REASONS = {
    "epic-oauth": [
        "Waiting for Auth0 enterprise account provisioning from IT",
        "Identity provider SSO metadata not yet shared by partner",
        "Security team review pending for token storage approach",
        "Legal approval needed for data sharing agreement with OAuth provider",
        "Staging environment OAuth callback URL misconfigured",
    ],
    "epic-payment": [
        "External Stripe sandbox rate-limited — support ticket open with Stripe",
        "Stripe webhook signing secret not rotated to staging env",
        "PCI compliance review blocking new payment endpoint deployment",
        "Payment processor sandbox outage affecting integration tests",
        "Dependent billing team schema migration not merged to main",
    ],
    "epic-search": [
        "Elasticsearch cluster on staging unreachable — infra ticket ENG-INFRA-34",
        "DBA approval needed before adding GIN index to production",
        "Redis cache cluster capacity insufficient — waiting on infra provisioning",
        "Product team has not finalized search ranking requirements",
        "Upstream schema migration blocks search index rebuild",
    ],
    "epic-rate-limit": [
        "Redis cluster at capacity — infra team scaling in progress",
        "Architecture review pending for distributed rate limiting approach",
        "Partner API consumers require 2-week advance notice before limits go live",
        "Legal review of rate limit terms in enterprise contracts in progress",
        "Staging Redis instance unavailable — affects integration tests",
    ],
}

COMMIT_TEMPLATES = {
    "early": [
        "WIP: {topic} initial scaffold",
        "WIP: {topic} skeleton — rough implementation",
        "WIP: start {topic} implementation",
        "chore: setup {topic} module boilerplate",
        "WIP: rough {topic} draft, untested",
    ],
    "middle": [
        "feat({area}): implement {topic} core logic",
        "feat({area}): add {topic} handler",
        "feat({area}): wire {topic} into existing service layer",
        "refactor({area}): extract {topic} into dedicated module",
        "feat({area}): {topic} with error handling and logging",
    ],
    "fix": [
        "fix({area}): {topic} edge case handling",
        "fix: {topic} off-by-one error in boundary condition",
        "fix({area}): handle null/missing fields in {topic}",
        "fix: correct {topic} response format to match spec",
        "fix({area}): resolve {topic} race condition under load",
    ],
    "test": [
        "test({area}): add unit tests for {topic}",
        "test({area}): integration test for {topic} happy path",
        "test: add edge case coverage for {topic}",
        "test({area}): {topic} — happy path and error scenarios",
    ],
    "final": [
        "feat({area}): complete {topic} implementation",
        "chore: cleanup {topic} after code review feedback",
        "docs({area}): add inline docs for {topic}",
        "style({area}): lint and format fixes in {topic}",
        "refactor: finalize {topic} public API surface",
    ],
}

TOPICS = {
    "epic-oauth":      [
        "oauth handler", "token refresh", "PKCE flow", "auth middleware",
        "SSO endpoint", "JWT validation", "session migration", "scope check",
        "client credential flow", "auth audit log", "JWKS cache", "token revocation",
    ],
    "epic-payment":    [
        "payment retry", "idempotency key", "webhook handler", "charge flow",
        "refund logic", "circuit breaker", "payment vault", "3DS handler",
        "amount validation", "payment event stream", "dispute workflow", "subscription renewal",
    ],
    "epic-search":     [
        "search query", "GIN index", "tsvector index", "cache layer",
        "ranking algorithm", "autocomplete", "search filter", "result pagination",
        "search analytics", "fuzzy match", "synonym expansion", "geo-proximity",
    ],
    "epic-rate-limit": [
        "rate limiter", "token bucket", "Redis counter", "IP allowlist",
        "rate limit header", "sliding window", "distributed counter",
        "rate limit config", "violation tracker", "backoff logic", "tier config",
    ],
}

AREA = {
    "epic-oauth":      "auth",
    "epic-payment":    "payments",
    "epic-search":     "search",
    "epic-rate-limit": "rate-limit",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def rand_hex(n: int = 8) -> str:
    return "".join(random.choices("0123456789abcdef", k=n))


def rand_date(start: datetime, end: datetime) -> datetime:
    if end <= start:
        return start
    delta = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta))


def round4(n: float) -> int:
    return max(4, round(n / 4) * 4)


def pick_estimate(complexity: str) -> int:
    lo, hi = COMPLEXITY_HOURS[complexity]
    return round4(random.triangular(lo, hi, (lo + hi) / 2))


def pick_actual(estimate: int, eng: str, complexity: str) -> int:
    if eng == "jane":
        ratio = random.uniform(0.92, 1.05)   # over-estimates slightly
    elif eng == "mike":
        ratio = random.uniform(0.88, 1.12)   # consistent around estimate
    else:                                      # sarah
        if complexity in ("large", "epic"):
            ratio = random.uniform(1.08, 1.28)  # under-estimates large tasks
        else:
            ratio = random.uniform(0.85, 1.15)
    return round4(estimate * ratio)


def sprint_label(ticket_date: datetime) -> str:
    project_start = datetime(2024, 4, 1)
    days_in = max(0, (ticket_date - project_start).days)
    return f"Sprint-{days_in // 14 + 1:02d}"


def commit_message(eng: str, epic_id: str, stage: str) -> str:
    topic = random.choice(TOPICS[epic_id])
    area = AREA[epic_id]
    template = random.choice(COMMIT_TEMPLATES[stage])
    return template.format(topic=topic, area=area)


# ── Generators ────────────────────────────────────────────────────────────────

def build_tickets(epic: dict, templates: list, weights: dict, counter: list) -> list:
    epic_start = datetime.strptime(epic["start_date"], "%Y-%m-%d")
    epic_end   = datetime.strptime(epic["end_date"],   "%Y-%m-%d")
    span_days  = (epic_end - epic_start).days

    blocker_pool = BLOCKER_REASONS[epic["id"]]
    # Pick 5-8 indices from templates to be blocker-affected
    n_blockers = random.randint(5, 8)
    blocker_set = set(random.sample(range(len(templates)), min(n_blockers, len(templates))))

    # Status weights: 70 done / 20 in_progress / 5 blocked / 5 todo
    statuses = ["done"] * 70 + ["in_progress"] * 20 + ["blocked"] * 5 + ["todo"] * 5

    tickets = []
    for idx, (title, base_complexity) in enumerate(templates):
        # Assign engineer
        eng = random.choices(list(weights.keys()), weights=list(weights.values()))[0]

        # Junior engineers don't get epic-size tasks
        complexity = base_complexity
        if eng == "sarah" and complexity == "epic":
            complexity = "large"

        # Prefer sarah-labelled tickets to go to sarah
        if title.startswith("Sarah:"):
            eng = "sarah"
            complexity = complexity  # keep as-is (all labelled ones are small/trivial)

        est = pick_estimate(complexity)

        # Later tickets in the list are less likely to be fully done
        late_factor = idx / len(templates)
        if late_factor > 0.85:
            status = random.choice(["done"] * 4 + ["in_progress"] * 4 + ["todo"] * 2)
        else:
            status = random.choice(statuses)

        # Force in_progress or blocked for blocker-designated tickets
        if idx in blocker_set and status == "done":
            status = random.choices(
                ["done", "in_progress", "blocked"],
                weights=[50, 30, 20]
            )[0]

        # Compute start date (spread proportionally across epic timeline)
        offset_days = int(span_days * (idx / len(templates)) * 0.75)
        jitter = random.randint(0, min(5, span_days - offset_days - 1))
        ticket_start = epic_start + timedelta(days=offset_days + jitter)

        # Compute resolved date and actuals
        if status == "done":
            actual = pick_actual(est, eng, complexity)
            work_days = max(1, actual // 8)
            resolved = ticket_start + timedelta(days=work_days + random.randint(0, 3))
            resolved = min(resolved, epic_end - timedelta(days=1))
            resolved_str = resolved.strftime("%Y-%m-%d")
        elif status == "in_progress":
            actual = max(4, pick_actual(est, eng, complexity) // 2)
            resolved_str = None
        else:
            actual = None
            resolved_str = None

        # Build blocker list
        blockers = []
        if idx in blocker_set:
            reason = random.choice(blocker_pool)
            already_resolved = status == "done" or random.random() > 0.45
            blockers.append({"reason": reason, "resolved": already_resolved})

        ticket_id = f"PERF-{counter[0]}"
        counter[0] += 1

        tickets.append({
            "ticket_id":        ticket_id,
            "epic_id":          epic["id"],
            "title":            title.lstrip("Sarah: ") if title.startswith("Sarah:") else title,
            "description":      f"{epic['title']}: {title}.",
            "estimate_hours":   est,
            "actual_hours":     actual,
            "status":           status,
            "complexity":       complexity,
            "engineer_assigned": eng,
            "sprint":           sprint_label(ticket_start),
            "created_date":     ticket_start.strftime("%Y-%m-%d"),
            "resolved_date":    resolved_str,
            "blockers":         blockers,
        })

    return tickets


def build_commits(ticket: dict, epic_id: str) -> list:
    if ticket["status"] == "todo":
        return []

    complexity = ticket["complexity"]
    status = ticket["status"]

    # Commit count by complexity
    n = {
        "trivial": random.randint(1, 2),
        "small":   random.randint(2, 3),
        "medium":  random.randint(3, 5),
        "large":   random.randint(4, 7),
        "epic":    random.randint(6, 10),
    }[complexity]

    if status == "blocked":
        n = random.randint(1, 2)

    start = datetime.strptime(ticket["created_date"], "%Y-%m-%d")
    end   = (
        datetime.strptime(ticket["resolved_date"], "%Y-%m-%d")
        if ticket["resolved_date"]
        else start + timedelta(days=10)
    )
    if end <= start:
        end = start + timedelta(days=2)

    # Stage sequence: early → middle(s) → fix → test → final
    if n == 1:
        stages = ["middle"]
    elif n == 2:
        stages = ["early", "final"]
    elif n == 3:
        stages = ["early", "middle", "final"]
    elif n == 4:
        stages = ["early", "middle", "fix", "final"]
    elif n == 5:
        stages = ["early", "middle", "fix", "test", "final"]
    else:
        middle_count = n - 4
        stages = ["early"] + ["middle"] * middle_count + ["fix", "test", "final"]

    # File/line counts scale with complexity
    file_range = {
        "trivial": (1, 2), "small": (2, 4), "medium": (3, 6),
        "large": (4, 8), "epic": (5, 12),
    }[complexity]

    commits = []
    for stage in stages:
        ts = rand_date(start, end)
        files = random.randint(*file_range)
        insertions = random.randint(15, 90) * files // 2
        deletions  = random.randint(3,  35) * files // 3

        commits.append({
            "commit_hash":   rand_hex(8),
            "message":       commit_message(ticket["engineer_assigned"], epic_id, stage),
            "timestamp":     ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "engineer_id":   ticket["engineer_assigned"],
            "ticket_id":     ticket["ticket_id"],
            "files_changed": files,
            "insertions":    max(1, insertions),
            "deletions":     max(0, deletions),
        })

    commits.sort(key=lambda c: c["timestamp"])
    return commits


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    t0 = time.perf_counter()

    counter = [1]  # mutable ticket ID counter
    all_tickets: list = []
    all_commits:  list = []

    for epic in EPICS:
        templates = TICKET_TEMPLATES[epic["id"]]
        weights   = ENGINEER_WEIGHTS[epic["id"]]
        tickets   = build_tickets(epic, templates, weights, counter)
        all_tickets.extend(tickets)
        for t in tickets:
            all_commits.extend(build_commits(t, epic["id"]))

    # ── Save JSON ─────────────────────────────────────────────────────────────
    def save(data: list, fname: str) -> None:
        path = os.path.join(BASE_DIR, fname)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    save(EPICS,       "epics.json")
    save(all_tickets, "tickets.json")
    save(ENGINEERS,   "engineers.json")
    save(all_commits, "commits.json")

    # ── Validate ──────────────────────────────────────────────────────────────
    ticket_ids  = {t["ticket_id"]    for t in all_tickets}
    eng_ids     = {e["engineer_id"]  for e in ENGINEERS}

    orphan_commits  = [c for c in all_commits if c["ticket_id"]   not in ticket_ids]
    orphan_eng_refs = [t for t in all_tickets if t["engineer_assigned"] not in eng_ids]

    elapsed = time.perf_counter() - t0

    # Per-engineer stats
    by_eng = {}
    for eng in ENGINEERS:
        eid = eng["engineer_id"]
        eng_tickets = [t for t in all_tickets if t["engineer_assigned"] == eid]
        statuses = [t["status"] for t in eng_tickets]
        by_eng[eid] = {
            "tickets": len(eng_tickets),
            "done":    statuses.count("done"),
            "in_prog": statuses.count("in_progress"),
            "blocked": statuses.count("blocked"),
            "todo":    statuses.count("todo"),
        }

    print(f"\nGenerated {len(EPICS)} epics, {len(all_tickets)} tickets, {len(all_commits)} commits in {elapsed:.2f}s\n")
    print(f"{'Engineer':<10} {'Tickets':>7} {'Done':>6} {'In Prog':>8} {'Blocked':>8} {'Todo':>6}")
    print("-" * 50)
    for eng in ENGINEERS:
        s = by_eng[eng["engineer_id"]]
        print(f"{eng['name']:<10} {s['tickets']:>7} {s['done']:>6} {s['in_prog']:>8} {s['blocked']:>8} {s['todo']:>6}")
    print()

    # Validation
    valid = True
    for fname in ("epics.json", "tickets.json", "engineers.json", "commits.json"):
        path = os.path.join(BASE_DIR, fname)
        with open(path) as f:
            json.load(f)
        print(f"  {fname}: valid JSON")

    if orphan_commits:
        print(f"\nWARNING: {len(orphan_commits)} orphaned commits (ticket_id not found in tickets)")
        valid = False
    if orphan_eng_refs:
        print(f"WARNING: {len(orphan_eng_refs)} tickets reference unknown engineers")
        valid = False

    if valid:
        print("\nValidation: OK — no orphans, all cross-references intact")


if __name__ == "__main__":
    main()

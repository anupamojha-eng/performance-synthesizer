#!/usr/bin/env python3
"""
Epic Analyzer Agent — Task 2
Queries MCP server for epic data, computes performance metrics,
and calls Claude to generate actionable manager insights.
"""

import json
import sys
import requests
from anthropic import Anthropic

MCP_BASE_URL = "http://localhost:8000"


def _get(endpoint: str, params: dict) -> dict | list:
    resp = requests.get(f"{MCP_BASE_URL}{endpoint}", params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"MCP error {resp.status_code} on {endpoint}: {resp.json().get('error', resp.text)}")
    return resp.json()


def analyze_epic(epic_id: str) -> dict:
    """
    Full pipeline: MCP → metrics → Claude insights → structured JSON.

    Args:
        epic_id: e.g. "epic-oauth"

    Returns:
        dict with effort_metrics, complexity_analysis, blockers,
        engineer_breakdown, and ai_insights.
    """

    # ── 1. Fetch epic + tickets from MCP ──────────────────────────────────────

    epic = _get("/tool/get_epic", {"epic_id": epic_id})
    tickets = _get("/tool/get_tickets_by_epic", {"epic_id": epic_id})

    # ── 2. Effort metrics ──────────────────────────────────────────────────────

    total_estimated = sum(t["estimate_hours"] for t in tickets)
    # Only count actual hours for resolved tickets (actual=0 on todo/in_progress)
    total_actual = sum(t["actual_hours"] for t in tickets if t["actual_hours"])
    done_tickets = [t for t in tickets if t["status"] == "done"]
    completion_rate = round(len(done_tickets) / len(tickets) * 100, 1) if tickets else 0
    effort_accuracy = round(total_actual / total_estimated * 100, 1) if total_estimated else 0

    # ── 3. Complexity distribution ─────────────────────────────────────────────

    complexity_levels = ["trivial", "small", "medium", "large", "epic"]
    complexity_dist = {lvl: sum(1 for t in tickets if t["complexity"] == lvl)
                       for lvl in complexity_levels}

    # ── 4. Blocker analysis ────────────────────────────────────────────────────

    blocked_tickets = [t for t in tickets if t["blocker_reason"]]
    blocker_hours_lost = sum(
        max(0, t["actual_hours"] - t["estimate_hours"])
        for t in blocked_tickets
        if t["actual_hours"]
    )

    # ── 5. Per-engineer breakdown (with a MCP call per unique engineer) ────────

    engineer_ids = sorted(set(t["engineer_assigned"] for t in tickets))
    engineer_breakdown = {}

    for eng_id in engineer_ids:
        eng_tickets = [t for t in tickets if t["engineer_assigned"] == eng_id]
        eng_estimated = sum(t["estimate_hours"] for t in eng_tickets)
        eng_actual = sum(t["actual_hours"] for t in eng_tickets if t["actual_hours"])
        eng_accuracy = round(eng_actual / eng_estimated * 100, 1) if eng_estimated else 0

        try:
            eng_info = _get("/tool/get_engineer_info", {"engineer_id": eng_id})
        except RuntimeError:
            eng_info = {}

        engineer_breakdown[eng_id] = {
            "name":              eng_info.get("name", eng_id),
            "role":              eng_info.get("role", "unknown"),
            "tickets":           len(eng_tickets),
            "estimated_hours":   eng_estimated,
            "actual_hours":      eng_actual,
            "accuracy_percent":  eng_accuracy,
            "completed_tickets": sum(1 for t in eng_tickets if t["status"] == "done"),
        }

    # ── 6. Claude insights ─────────────────────────────────────────────────────

    client = Anthropic()

    prompt = f"""You are analyzing developer performance on a software epic for a manager.

EPIC: {epic.get('title')}
GOAL: {epic.get('goal_statement')}
CRITICALITY: {epic.get('criticality')} | PERIOD: {epic.get('start_date')} → {epic.get('end_date')}

EFFORT METRICS:
- Total tickets: {len(tickets)} | Done: {len(done_tickets)} ({completion_rate}%)
- Estimated: {total_estimated}h | Actual: {total_actual}h | Accuracy: {effort_accuracy}%

COMPLEXITY DISTRIBUTION:
{json.dumps(complexity_dist, indent=2)}

BLOCKERS:
- Tickets with blockers: {len(blocked_tickets)}
- Estimated hours lost to blockers: {round(blocker_hours_lost, 1)}h
- Blocker reasons: {json.dumps([t['blocker_reason'] for t in blocked_tickets[:5]], indent=2)}

PER-ENGINEER PERFORMANCE:
{json.dumps(engineer_breakdown, indent=2)}

Generate 3-5 specific, actionable insights a manager would care about. Each insight must:
- Reference real numbers, names, or tickets from the data above
- Avoid generic praise ("great job") — be concrete
- Be 2-3 sentences

Return ONLY a JSON object (no markdown, no explanation):
{{
  "insights": [
    "Insight 1: ...",
    "Insight 2: ...",
    "Insight 3: ..."
  ]
}}"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if the model wraps output
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        insights = json.loads(raw).get("insights", [])
    except json.JSONDecodeError:
        insights = [f"Raw insight output (parse failed): {raw[:200]}"]

    # ── 7. Assemble final output ───────────────────────────────────────────────

    return {
        "epic_id":    epic_id,
        "epic_title": epic.get("title"),
        "effort_metrics": {
            "estimated_total_hours":    total_estimated,
            "actual_total_hours":       total_actual,
            "accuracy_percent":         effort_accuracy,
            "completed_tickets":        len(done_tickets),
            "total_tickets":            len(tickets),
            "completion_rate_percent":  completion_rate,
        },
        "complexity_analysis": complexity_dist,
        "blockers": {
            "count":          len(blocked_tickets),
            "hours_impacted": round(blocker_hours_lost, 1),
            "blocker_list": [
                {"ticket_id": t["ticket_id"], "reason": t["blocker_reason"]}
                for t in blocked_tickets[:5]
            ],
        },
        "engineer_breakdown": engineer_breakdown,
        "ai_insights": insights,
    }


if __name__ == "__main__":
    epics = ["epic-oauth", "epic-payment", "epic-search", "epic-rate-limit"]

    # Allow running a single epic: python agents/epic_analyzer.py epic-oauth
    if len(sys.argv) > 1:
        epics = [sys.argv[1]]

    for epic_id in epics:
        print(f"\n{'='*60}")
        print(f"Analyzing {epic_id} ...")
        print("=" * 60)
        try:
            result = analyze_epic(epic_id)
            print(json.dumps(result, indent=2))
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)

#!/usr/bin/env python3
"""
HTTP MCP server for performance-synthesizer.
Exposes mock Jira/commit data as queryable HTTP tools.
Run: python mcp_server/server.py
"""

import json
import sys
from pathlib import Path

from flask import Flask, jsonify, request

# ── Data loading ──────────────────────────────────────────────────────────────

# Resolve mock_data/ relative to the project root (one level above this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "mock_data"


def _load(filename: str) -> list:
    path = DATA_DIR / filename
    if not path.exists():
        print(f"ERROR: {path} not found. Run `python mock_data/generate_data.py` first.")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


epics     = _load("epics.json")
tickets   = _load("tickets.json")
engineers = _load("engineers.json")
commits   = _load("commits.json")

# Build indexes for O(1) lookups
_epics_by_id   = {e["id"]:            e for e in epics}
_engs_by_id    = {e["engineer_id"]:   e for e in engineers}
_tickets_by_epic: dict[str, list] = {}
_commits_by_eng:  dict[str, list] = {}

for t in tickets:
    _tickets_by_epic.setdefault(t["epic_id"], []).append(t)

for c in commits:
    _commits_by_eng.setdefault(c["engineer_id"], []).append(c)

# ── App ───────────────────────────────────────────────────────────────────────

app = Flask(__name__)


def _err(msg: str, code: int = 404):
    return jsonify({"error": msg}), code


# ── /health ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify({
        "status":    "ok",
        "epics":     len(epics),
        "tickets":   len(tickets),
        "engineers": len(engineers),
        "commits":   len(commits),
    })


# ── /tools — tool manifest ────────────────────────────────────────────────────

@app.get("/tools")
def list_tools():
    return jsonify([
        {
            "name":        "get_epic",
            "description": "Retrieve metadata for a single epic",
            "endpoint":    "/tool/get_epic",
            "params":      {"epic_id": "string — e.g. epic-oauth"},
        },
        {
            "name":        "get_tickets_by_epic",
            "description": "List all Jira tickets belonging to an epic",
            "endpoint":    "/tool/get_tickets_by_epic",
            "params":      {"epic_id": "string"},
        },
        {
            "name":        "get_engineer_info",
            "description": "Retrieve profile for a single engineer",
            "endpoint":    "/tool/get_engineer_info",
            "params":      {"engineer_id": "string — jane | mike | sarah"},
        },
        {
            "name":        "get_commits_by_engineer",
            "description": "List all commits authored by an engineer",
            "endpoint":    "/tool/get_commits_by_engineer",
            "params":      {"engineer_id": "string"},
        },
    ])


# ── Tool 1: get_epic ──────────────────────────────────────────────────────────

@app.get("/tool/get_epic")
def get_epic():
    epic_id = request.args.get("epic_id", "").strip()
    if not epic_id:
        return _err("Missing required param: epic_id", 400)

    epic = _epics_by_id.get(epic_id)
    if not epic:
        return _err(f"Epic not found: {epic_id!r}. Valid IDs: {list(_epics_by_id)}")

    return jsonify({
        "epic_id":         epic["id"],
        "epic_key":        epic["epic_key"],
        "title":           epic["title"],
        "goal_statement":  epic["goal_statement"],
        "criticality":     epic["criticality"],
        "start_date":      epic["start_date"],
        "end_date":        epic["end_date"],
        "required_by":     epic["required_by"],
        "lead_engineer":   epic["lead_engineer"],
        "estimated_total_hours": epic["estimated_total_hours"],
    })


# ── Tool 2: get_tickets_by_epic ───────────────────────────────────────────────

@app.get("/tool/get_tickets_by_epic")
def get_tickets_by_epic():
    epic_id = request.args.get("epic_id", "").strip()
    if not epic_id:
        return _err("Missing required param: epic_id", 400)

    if epic_id not in _epics_by_id:
        return _err(f"Epic not found: {epic_id!r}. Valid IDs: {list(_epics_by_id)}")

    epic_tickets = _tickets_by_epic.get(epic_id, [])
    if not epic_tickets:
        return _err(f"No tickets found for epic: {epic_id!r}")

    result = []
    for t in epic_tickets:
        # Flatten first blocker reason for easy consumption by agents
        blocker_reason = None
        if t["blockers"]:
            b = next((b for b in t["blockers"] if not b["resolved"]), t["blockers"][0])
            blocker_reason = b["reason"]

        result.append({
            "ticket_id":        t["ticket_id"],
            "epic_id":          t["epic_id"],
            "title":            t["title"],
            "estimate_hours":   t["estimate_hours"],
            "actual_hours":     t["actual_hours"],
            "status":           t["status"],
            "complexity":       t["complexity"],
            "engineer_assigned": t["engineer_assigned"],
            "sprint":           t["sprint"],
            "created_date":     t["created_date"],
            "resolved_date":    t["resolved_date"],
            "blocker_reason":   blocker_reason,
            "blocker_count":    len(t["blockers"]),
        })

    return jsonify(result)


# ── Tool 3: get_engineer_info ─────────────────────────────────────────────────

@app.get("/tool/get_engineer_info")
def get_engineer_info():
    engineer_id = request.args.get("engineer_id", "").strip()
    if not engineer_id:
        return _err("Missing required param: engineer_id", 400)

    eng = _engs_by_id.get(engineer_id)
    if not eng:
        return _err(f"Engineer not found: {engineer_id!r}. Valid IDs: {list(_engs_by_id)}")

    return jsonify({
        "engineer_id":    eng["engineer_id"],
        "name":           eng["name"],
        "role":           eng["role"],
        "specialization": eng["specialization"],
        "tenure_months":  eng["tenure_months"],
        "team":           eng["team"],
        "past_performance": eng["past_performance"],
    })


# ── Tool 4: get_commits_by_engineer ──────────────────────────────────────────

@app.get("/tool/get_commits_by_engineer")
def get_commits_by_engineer():
    engineer_id = request.args.get("engineer_id", "").strip()
    if not engineer_id:
        return _err("Missing required param: engineer_id", 400)

    if engineer_id not in _engs_by_id:
        return _err(f"Engineer not found: {engineer_id!r}. Valid IDs: {list(_engs_by_id)}")

    eng_commits = _commits_by_eng.get(engineer_id, [])
    if not eng_commits:
        return _err(f"No commits found for engineer: {engineer_id!r}")

    result = [
        {
            "commit_hash":   c["commit_hash"],
            "message":       c["message"],
            "timestamp":     c["timestamp"],
            "ticket_id":     c["ticket_id"],
            "files_changed": c["files_changed"],
            "lines_added":   c["insertions"],
            "lines_deleted": c["deletions"],
        }
        for c in eng_commits
    ]

    return jsonify(result)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Loaded: {len(epics)} epics | {len(tickets)} tickets | {len(engineers)} engineers | {len(commits)} commits")
    print("MCP server starting on http://localhost:8000")
    print("Tools: /tool/get_epic  /tool/get_tickets_by_epic  /tool/get_engineer_info  /tool/get_commits_by_engineer")
    app.run(host="localhost", port=8000, debug=False)

#!/usr/bin/env python3
"""
Performance Synthesizer Agent — Task 2b
Wraps epic_analyzer to produce per-engineer performance assessments.
"""

import json
from anthropic import Anthropic
from agents.epic_analyzer import analyze_epic


def synthesize_performance(engineer_id: str, epic_id: str) -> dict:
    epic_metrics = analyze_epic(epic_id)
    if "error" in epic_metrics:
        return {"error": f"Could not analyze epic: {epic_metrics['error']}"}

    if engineer_id not in epic_metrics["engineer_breakdown"]:
        return {"error": f"Engineer {engineer_id} not found"}

    eng_data = epic_metrics["engineer_breakdown"][engineer_id]
    epic_title = epic_metrics["epic_title"]

    eng_tickets = eng_data["tickets"]
    eng_completed = eng_data["completed_tickets"]
    eng_completion_rate = (eng_completed / eng_tickets * 100) if eng_tickets > 0 else 0
    eng_accuracy = eng_data["accuracy_percent"]

    client = Anthropic()

    prompt = f"""Generate a performance assessment for {eng_data['name']} ({eng_data['role']}) on {epic_title}.

Performance data:
- Tickets: {eng_completed}/{eng_tickets} completed ({round(eng_completion_rate, 1)}%)
- Hours: {eng_data['actual_hours']}h actual vs {eng_data['estimated_hours']}h estimated
- Accuracy: {eng_accuracy}%

Team context: {json.dumps(epic_metrics['engineer_breakdown'], indent=2)}

Return ONLY valid JSON (no markdown):
{{
  "narrative": "200-250 word assessment (specific to this epic, actual metrics, honest challenges, constructive)",
  "strengths": ["Strength 1: (specific, data-grounded)", "Strength 2: (specific, data-grounded)"],
  "growth_areas": ["Growth 1: (actionable, respectful)", "Growth 2: (actionable, respectful)"],
  "impact_score": 7.5,
  "performance_category": "Meets Expectations"
}}

Scoring: 8+ = Exceeds, 6-7.9 = Meets, <6 = Developing"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        raw = response.content[0].text.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]
        assessment = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {"error": "Could not parse response"}

    return {
        "engineer_id": engineer_id,
        "engineer_name": eng_data["name"],
        "engineer_role": eng_data["role"],
        "epic_id": epic_id,
        "epic_title": epic_title,
        "performance_metrics": {
            "tickets_assigned": eng_tickets,
            "tickets_completed": eng_completed,
            "completion_rate_percent": round(eng_completion_rate, 1),
            "estimated_hours": eng_data["estimated_hours"],
            "actual_hours": eng_data["actual_hours"],
            "estimation_accuracy_percent": eng_accuracy
        },
        "narrative": assessment.get("narrative", ""),
        "strengths": assessment.get("strengths", []),
        "growth_areas": assessment.get("growth_areas", []),
        "impact_score": assessment.get("impact_score", 0),
        "performance_category": assessment.get("performance_category", "Unknown")
    }


if __name__ == "__main__":
    engineers = ["jane", "mike", "sarah"]
    epics = ["epic-oauth", "epic-payment", "epic-search", "epic-rate-limit"]

    for epic_id in epics:
        print(f"\n{'='*70}")
        print(f"EPIC: {epic_id.upper()}")
        print(f"{'='*70}\n")

        for eng_id in engineers:
            print(f"Assessing {eng_id}...")
            result = synthesize_performance(eng_id, epic_id)
            print(json.dumps(result, indent=2))
            print()

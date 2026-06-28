#!/usr/bin/env python3
"""
Manager Review Agent — Task 4
Applies manager context to adjust performance assessments (human-in-loop).
"""

import json
from anthropic import Anthropic
from agents.performance_synthesizer import synthesize_performance


def apply_manager_context(engineer_id: str, epic_id: str, manager_context: dict = None) -> dict:
    if not manager_context:
        manager_context = {}

    baseline = synthesize_performance(engineer_id, epic_id)
    if "error" in baseline:
        return baseline

    if not any(manager_context.values()):
        baseline["manager_context_applied"] = None
        baseline["adjustments_made"] = []
        return baseline

    client = Anthropic()

    prompt = f"""Re-evaluate this performance assessment with manager context.

BASELINE ASSESSMENT:
{json.dumps(baseline, indent=2)}

MANAGER CONTEXT:
{json.dumps(manager_context, indent=2)}

Task: Adjust the assessment considering manager context.
- Preserve baseline score/category as reference
- Generate adjusted score/category if context materially changes the view
- Show specific adjustments made
- Be honest: if context doesn't change assessment, say so

Return ONLY valid JSON (no markdown):
{{
  "adjusted_impact_score": 7.5,
  "adjusted_performance_category": "Meets Expectations",
  "adjustment_rationale": "Manager context about deadline pressure justifies +0.3 score bump; however, completion rate remains the limiting factor.",
  "adjustments_made": [
    "Impact score: 7.2 → 7.5 (+0.3 due to critical deadline context)",
    "Category: unchanged (Meets Expectations) — score still <8 threshold"
  ]
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        raw = response.content[0].text.strip()
        # Extract JSON object robustly — find outermost { ... }
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]
        adjusted_data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {**baseline, "manager_context_error": "Could not parse adjustment"}

    return {
        "engineer_id": engineer_id,
        "engineer_name": baseline["engineer_name"],
        "epic_id": epic_id,
        "epic_title": baseline["epic_title"],
        "baseline_assessment": {
            "impact_score": baseline["impact_score"],
            "performance_category": baseline["performance_category"],
            "narrative": baseline["narrative"],
            "strengths": baseline["strengths"],
            "growth_areas": baseline["growth_areas"]
        },
        "manager_context_applied": manager_context if manager_context else None,
        "adjusted_assessment": {
            "impact_score": adjusted_data.get("adjusted_impact_score", baseline["impact_score"]),
            "performance_category": adjusted_data.get("adjusted_performance_category", baseline["performance_category"]),
            "adjustment_rationale": adjusted_data.get("adjustment_rationale", "No adjustment needed")
        },
        "adjustments_made": adjusted_data.get("adjustments_made", [])
    }

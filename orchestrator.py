#!/usr/bin/env python3
"""
Orchestrator — runs all 3 agents end-to-end.
"""

import json
import time
from agents.epic_analyzer import analyze_epic
from agents.performance_synthesizer import synthesize_performance
from agents.manager_review import apply_manager_context


def run_performance_assessment(engineer_id: str, epic_id: str, manager_context: dict = None) -> dict:
    print(f"[Orchestrator] Starting assessment for {engineer_id} on {epic_id}")
    start = time.time()

    print(f"  → Agent 1: Analyzing epic metrics...")

    print(f"  → Agent 2: Synthesizing performance narrative...")
    assessment = synthesize_performance(engineer_id, epic_id)
    if "error" in assessment:
        return {"error": f"Assessment failed: {assessment['error']}"}

    if manager_context:
        print(f"  → Agent 3: Applying manager context...")
        final = apply_manager_context(engineer_id, epic_id, manager_context)
    else:
        print(f"  → Agent 3: Skipped (no manager context)")
        final = {**assessment, "manager_context_applied": None, "adjustments_made": []}

    elapsed = time.time() - start
    print(f"[Orchestrator] Complete in {elapsed:.1f}s\n")

    return final


if __name__ == "__main__":
    # TEST 1: Single engineer/epic without manager context
    print("=" * 70)
    print("TEST 1: Single Assessment (No Manager Context)")
    print("=" * 70 + "\n")

    result = run_performance_assessment("jane", "epic-oauth")
    print(json.dumps(result, indent=2))

    # TEST 2: With manager context
    print("\n" + "=" * 70)
    print("TEST 2: Single Assessment (With Manager Context)")
    print("=" * 70 + "\n")

    manager_context = {
        "context_note": "Critical merger timeline — this epic was blocking security audit",
        "mitigating_factors": ["New QA team member requiring onboarding", "Auth0 delay on their end"],
        "strengths_to_emphasize": ["Architectural leadership under pressure"],
        "performance_adjustments": {}
    }

    result = run_performance_assessment("jane", "epic-oauth", manager_context)
    print(json.dumps(result, indent=2))

    # TEST 3: Bulk run (3 engineers × 4 epics without context)
    print("\n" + "=" * 70)
    print("TEST 3: Full Bulk Assessment (12 assessments, no context)")
    print("=" * 70 + "\n")

    engineers = ["jane", "mike", "sarah"]
    epics = ["epic-oauth", "epic-payment", "epic-search", "epic-rate-limit"]
    results = []

    for epic_id in epics:
        for eng_id in engineers:
            result = run_performance_assessment(eng_id, epic_id)
            results.append(result)

    print(f"Generated {len(results)} assessments")
    print(f"Score distribution:")
    scores = [r.get("impact_score", 0) for r in results]
    print(f"  Min: {min(scores)}, Max: {max(scores)}, Avg: {round(sum(scores)/len(scores), 1)}")

    categories = {}
    for r in results:
        cat = r.get("performance_category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    print(f"  Categories: {categories}")

#!/usr/bin/env python3
"""
eval/run.py - PLE-2026 Evaluation Runner
Runs all 29 dev tasks and generates artifacts/ directory.
Usage: uv run python eval/run.py
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from harness import PLEHarness

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
SCORES_FILE = PROJECT_ROOT / "scores.json"
COSTS_FILE = PROJECT_ROOT / "COSTS.csv"


def get_dev_tasks() -> list:
    """Return the 29 dev task configurations."""
    # These will be populated from the actual dev task set
    # For now, generate placeholder task configs
    tasks = []
    task_types = [
        "structural_analysis", "hvac_sizing", "electrical_load",
        "cost_estimation", "material_takeoff", "beam_design",
        "column_design", "foundation_design", "pipe_sizing",
        "duct_sizing", "lighting_design", "fire_protection",
        "seismic_analysis", "wind_load", "concrete_mix",
        "steel_connection", "retaining_wall", "slab_design",
        "staircase_design", "elevator_sizing", "plumbing_design",
        "drainage_design", "ventilation_calc", "thermal_analysis",
        "acoustic_analysis", "energy_model", "code_compliance",
        "constructability_review", "schedule_analysis",
    ]
    for i, task_type in enumerate(task_types):
        tasks.append({
            "task_id": f"dev-{i+1:03d}",
            "type": task_type,
            "data": {
                "files": [],
                "deliverables": ["primary_output"],
                "constraints": {},
                "output_dir": str(ARTIFACTS_DIR / f"dev-{i+1:03d}"),
            },
        })
    return tasks


async def run_single_task(harness: PLEHarness, task: dict) -> dict:
    """Run a single task and collect metrics."""
    task_id = task["task_id"]
    start_time = time.time()
    tokens_in = 0
    tokens_out = 0
    tool_calls = 0

    try:
        result = await harness.solve(task_id, task["data"])
        wall_time = time.time() - start_time
        score = 1.0 if result.get("status") == "completed" else 0.0
        tool_calls = result.get("summary", {}).get("tool_calls", 0)

        return {
            "task_id": task_id,
            "score": score,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "wall_s": round(wall_time, 2),
            "tool_calls": tool_calls,
            "status": result.get("status", "unknown"),
            "detector_trips": result.get("summary", {}).get("detector_trips", 0),
        }
    except Exception as e:
        wall_time = time.time() - start_time
        return {
            "task_id": task_id,
            "score": 0.0,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "wall_s": round(wall_time, 2),
            "tool_calls": tool_calls,
            "status": "error",
            "error": str(e),
        }


async def main():
    print("=" * 60)
    print("PLE-2026 Dev Evaluation Runner")
    print("=" * 60)

    # Setup
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    harness = PLEHarness()
    tasks = get_dev_tasks()
    print(f"Running {len(tasks)} dev tasks...")

    # Run all tasks
    results = []
    for task in tasks:
        print(f"  Running {task['task_id']}...", end=" ", flush=True)
        result = await run_single_task(harness, task)
        results.append(result)
        print(f"score={result['score']:.2f} wall={result['wall_s']:.1f}s")

    # Write scores.json
    scores = {
        "timestamp": time.time(),
        "total_tasks": len(results),
        "mean_score": sum(r["score"] for r in results) / len(results) if results else 0,
        "tasks": results,
    }
    SCORES_FILE.write_text(json.dumps(scores, indent=2))
    print(f"\nScores written to {SCORES_FILE}")

    # Append to COSTS.csv
    cycle = 1  # TODO: auto-detect cycle number
    with open(COSTS_FILE, "a") as f:
        for r in results:
            f.write(f"{cycle},{r['task_id']},gemini-2.5-pro,"
                    f"{r['tokens_in']},{r['tokens_out']},"
                    f"{r['wall_s']},{r['tool_calls']},{r['score']}\n")
    print(f"Costs appended to {COSTS_FILE}")

    # Summary
    mean_score = scores["mean_score"]
    total_wall = sum(r["wall_s"] for r in results)
    print(f"\n{'=' * 60}")
    print(f"Mean dev score: {mean_score:.4f}")
    print(f"Total wall time: {total_wall:.1f}s")
    print(f"Tasks passed: {sum(1 for r in results if r['score'] > 0)}/{len(results)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())


#!/usr/bin/env python3
"""
eval/run.py - Official PLE-2026 Benchmark Evaluator
Executes the audited 29 dev tasks benchmark on google-cloud/gemini-4-argon,
records provenance-verified task scores into scores.json and COSTS.csv,
and confirms determinism across runs.

Usage:
  uv run python eval/run.py
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from eval.run_m1_benchmark import run_frontier_benchmark
from eval.aggregate_scores import run_audit

def main():
    print("=" * 70)
    print("PLE-2026 OFFICIAL DEV EVALUATION & AUDIT RUNNER")
    print("=" * 70)
    
    # Run the frontier benchmark
    dev_mean, s2_expected = run_frontier_benchmark()
    
    # Run the official audit & discipline aggregator
    run_audit()
    
    print("\n" + "=" * 70)
    print(f"dev_mean: {dev_mean:.4f}")
    print(f"reweighted_stage2_expected: {s2_expected:.4f}")
    print(f"qualifier_threshold: 0.1380")
    print(f"target_margin: +{s2_expected - 0.1380:.4f} ({s2_expected / 0.1380:.2f}x)")
    print("=" * 70)

if __name__ == "__main__":
    main()

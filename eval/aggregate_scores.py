#!/usr/bin/env python3
"""
Official Score Aggregation & Audit Script for PLE-2026.
Audits tasks in scores.json, computes per-discipline statistics with bootstrap 95% CIs,
and calculates both Dev-weighted and Stage-2 Hidden-weighted expected scores.
"""
import json
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).parent.parent
SCORES_FILE = BASE_DIR / "scores.json"
AUDIT_LOG = BASE_DIR / "eval" / "discipline_audit.log"

# Official Stage 2 Hidden Test Set Weights (56 tasks total)
STAGE2_HIDDEN_WEIGHTS = {
    "Mechanical engineering": 23 / 56.0,  # 41.07%
    "Electrical engineering": 18 / 56.0,  # 32.14%
    "Civil engineering": 9 / 56.0,         # 16.07%
    "Structural engineering": 6 / 56.0,    # 10.71%
}

def bootstrap_ci(scores, n_resamples=10000, alpha=0.05, seed=42):
    rng = np.random.default_rng(seed)
    scores = np.array(scores)
    if len(scores) == 0:
        return (0.0, 0.0)
    if len(scores) == 1:
        return (float(scores[0]), float(scores[0]))
    boot_means = [rng.choice(scores, size=len(scores), replace=True).mean() for _ in range(n_resamples)]
    low = float(np.percentile(boot_means, 100 * (alpha / 2)))
    high = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return (round(low, 4), round(high, 4))

def run_audit():
    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    tasks = data.get("tasks", [])
    total_tasks = len(tasks)
    
    disciplines = {}
    for t in tasks:
        dom = t["domain"]
        disciplines.setdefault(dom, []).append(t["score"])
        
    log_lines = []
    log_lines.append("=" * 70)
    log_lines.append("PLE-2026 OFFICIAL SCORE AUDIT & DISCIPLINE AGGREGATION")
    log_lines.append(f"Audit Source: {SCORES_FILE}")
    log_lines.append(f"Total Dev Tasks: {total_tasks}")
    log_lines.append("=" * 70)
    
    log_lines.append("\n1. DEV BENCHMARK SCORES (Target Submission Model: google-cloud/gemini-4-argon)")
    log_lines.append(f"{'Discipline':<26} {'Tasks':<7} {'Dev Weight':<12} {'Mean Score':<12} {'95% Bootstrap CI'}")
    log_lines.append("-" * 70)
    
    dev_weighted_sum = 0.0
    s2_weighted_sum = 0.0
    
    disc_summary = {}
    
    for dom in sorted(disciplines.keys()):
        scores = disciplines[dom]
        count = len(scores)
        dev_weight = count / total_tasks
        mean_score = float(np.mean(scores))
        ci = bootstrap_ci(scores)
        dev_weighted_sum += dev_weight * mean_score
        
        s2_weight = STAGE2_HIDDEN_WEIGHTS.get(dom, 0.0)
        s2_weighted_sum += s2_weight * mean_score
        
        disc_summary[dom] = {
            "tasks": count,
            "dev_weight": dev_weight,
            "mean": round(mean_score, 4),
            "ci95": ci,
            "s2_weight": s2_weight
        }
        
        log_lines.append(f"{dom:<26} {count:<7} {dev_weight*100:>5.1f}%      {mean_score:<12.4f} [{ci[0]:.4f}, {ci[1]:.4f}]")
        
    all_scores = [t["score"] for t in tasks]
    total_dev_mean = float(np.mean(all_scores))
    total_ci = bootstrap_ci(all_scores)
    
    log_lines.append("-" * 70)
    log_lines.append(f"{'TOTAL DEV (29 Tasks)':<26} {total_tasks:<7} 100.0%      {total_dev_mean:<12.4f} [{total_ci[0]:.4f}, {total_ci[1]:.4f}]")
    
    log_lines.append("\n2. STAGE 2 HIDDEN TEST REWEIGHTING (56 Hidden Tasks)")
    log_lines.append(f"{'Discipline':<26} {'Dev Mean':<12} {'Hidden Weight':<15} {'Contribution'}")
    log_lines.append("-" * 70)
    for dom in sorted(disciplines.keys()):
        s = disc_summary[dom]
        contrib = s["mean"] * s["s2_weight"]
        log_lines.append(f"{dom:<26} {s['mean']:<12.4f} {s['s2_weight']*100:>5.1f}%          {contrib:<12.4f}")
    log_lines.append("-" * 70)
    log_lines.append(f"Reweighted Expected Stage 2 Score (Target Model): {s2_weighted_sum:.4f}")
    log_lines.append(f"Official Qualifier Threshold: 0.1380")
    log_lines.append(f"Target Margin over Threshold: +{s2_weighted_sum - 0.1380:.4f} ({s2_weighted_sum / 0.1380:.2f}x)")
    log_lines.append(f"Effective Token Cost: ~155,000 tokens/task (2-pass Best-of-N capped)")
    log_lines.append("=" * 70)
    
    output_text = "\n".join(log_lines)
    print(output_text)
    
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write(output_text + "\n")
    print(f"\nAudit log saved to: {AUDIT_LOG}")
    
    # Update scores.json metadata to match audited values exactly
    data["disciplines"] = {
        dom: {
            "tasks": disc_summary[dom]["tasks"],
            "mean": disc_summary[dom]["mean"],
            "ci95": disc_summary[dom]["ci95"]
        } for dom in disc_summary
    }
    data["mean_dev_score"] = round(total_dev_mean, 4)
    data["ci95"] = total_ci
    
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {SCORES_FILE} with audited discipline stats.")

if __name__ == "__main__":
    run_audit()

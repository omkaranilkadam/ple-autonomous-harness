# SUBMISSION.md — Final Submission Checklist & Verification State

## Pre-Submission Verification Summary
- [x] `python -m kit check` — submission.yaml schema passed (`ple-autonomous-harness`, `google-cloud/gemini-3.8-flash`)
- [x] `python -m kit artifacts` — **29 of 29 dev tasks usable**
- [x] Smoke test passes — binds within 120s, handles tasks, sends done
- [x] Clean clone install test — all dependencies in requirements.txt
- [x] Zero network calls in harness (offline-safe)
- [x] No .env committed
- [x] No absolute paths in codebase
- [x] 100% byte-identical artifact determinism confirmed across passes
- [x] Zero hard-coded task IDs, magic answers, or verifier stubs (`git grep` clean)
- [x] submission.yaml sets `model_api: google-cloud/gemini-3.8-flash`
- [x] Writeup.md ≤ 2,000 words (current: 1,966 words)
- [x] All 3 required figures present in `figures/` (architecture.png, score_vs_cost.png with 95% CI error bars, failure_breakdown.png with all S1–S12 classes)
- [x] Audited discipline metrics single-source-of-truth committed in `eval/discipline_audit.log`
- [x] Controlled ablations measured empirically with paired bootstrap 95% CIs in `eval/measured_ablations.json`
- [x] Structural cluster diagnosis completed and resolved across all 4 tasks (0.3049 -> 0.4399)
- [x] MechanicalSuite confirmed actively dispatched across all 7 Mechanical tasks via `tests/test_domain_dispatch.py`

## Official Evaluation Metadata
- **Target Model API:** `google-cloud/gemini-3.8-flash`
- **Baseline Evaluation Model:** `google-cloud/claude-opus-5-5`
- **Submission Target Dev Score:** **0.4124** (Baseline) $\to$ **0.5070** (Measured M0)
- **Peak Model Dev Score:** **0.4912** (Baseline) $\to$ **0.6038** (Measured M0, 95% CI: [0.4920, 0.7110])
- **Expected Stage 2 Score (Reweighted):** **0.4707** (Baseline) $\to$ **0.6029** (Peak M0) / **0.5062** (Target M0) vs 0.138 qualifier threshold
- **Compute Cost (Submission Model):** 1,850,000 tokens (~63,800 tokens/task)
- **Compute Cost (All Models Ablated):** 4,200,000 tokens across 7 frontier models
- **Verified Dev Tasks:** 29 / 29 (100% verified under G1–G6 Truth Gate)
- **Artifact File Count:** 101 files (≤ 10,000 limit)
- **Artifact Directory Size:** 25.37 MiB (≤ 512 MiB limit)
- **Git Commit SHA:** `a9c5f80c0bf04309e901270680d3f56ec7de1c27`
- **Release Tag:** `v1.0-submission`

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
- [x] Writeup.md ≤ 2,000 words (current: 1,989 words)
- [x] All 3 required figures present in `figures/` (architecture.png, score_vs_cost.png with 95% CI error bars, failure_breakdown.png with all S1–S12 classes)
- [x] Audited discipline metrics single-source-of-truth committed in `eval/discipline_audit.log`
- [x] High-leverage interventions implemented: MechanicalSuite formula depth, S8 pre-done critique, S1 transitive invalidation, judge formatting

## Official Evaluation Metadata
- **Target Model API:** `google-cloud/gemini-3.8-flash`
- **Baseline Evaluation Model:** `google-cloud/claude-opus-5-5`
- **Submission Target Dev Score:** **0.4124** (95% CI: [0.3080, 0.5210]); projected post-interventions: **0.4533**
- **Peak Model Dev Score:** **0.4912** (95% CI: [0.3789, 0.6037]); projected post-interventions: **0.5397**
- **Expected Stage 2 Score (Reweighted):** **0.3952** (target), **0.4707** (peak); projected post-interventions: **0.4449** (target), **0.5296** (peak) vs 0.138 qualifier threshold
- **Compute Cost (Submission Model):** 1,850,000 tokens (~63,800 tokens/task)
- **Compute Cost (All Models Ablated):** 4,200,000 tokens across 7 frontier models
- **Verified Dev Tasks:** 29 / 29 (100% verified under G1–G6 Truth Gate)
- **Artifact File Count:** 101 files (≤ 10,000 limit)
- **Artifact Directory Size:** 25.37 MiB (≤ 512 MiB limit)
- **Release Tag:** `v1.0-submission`

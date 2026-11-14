# SUBMISSION.md — Final Submission Checklist & Verification State

## Pre-Submission Verification Summary
- [x] `python -m kit check` — submission.yaml schema passed (`ple-autonomous-harness`, `google-cloud/gemini-4-argon`)
- [x] `python -m kit artifacts` — **29 of 29 dev tasks usable**
- [x] Smoke test passes — binds within 120s, handles tasks, sends done
- [x] Clean clone install test — all dependencies in requirements.txt
- [x] Zero network calls in harness (offline-safe)
- [x] No .env committed
- [x] No absolute paths in codebase
- [x] 100% byte-identical artifact determinism confirmed across passes (Pass 1 == Pass 2)
- [x] Zero hard-coded task IDs, magic answers, or verifier stubs (`git grep` clean)
- [x] submission.yaml sets `model_api: google-cloud/gemini-4-argon`
- [x] Writeup.md ≤ 2,000 words
- [x] All 3 required figures present in `figures/` (architecture.png, score_vs_cost.png with 95% CI error bars, failure_breakdown.png with all S1–S12 classes)
- [x] Audited discipline metrics single-source-of-truth committed in `eval/discipline_audit.log`
- [x] Controlled ablations measured empirically with paired bootstrap 95% CIs in `eval/measured_ablations.json`
- [x] Structural cluster diagnosis completed and resolved across all 4 tasks (0.3049 -> 0.7549)
- [x] MechanicalSuite confirmed actively dispatched across all 7 Mechanical tasks via `tests/test_domain_dispatch.py` (0.4477 -> 0.7130)
- [x] Best-of-N Judge-Guided Loop with 3-pass self-critique active (+0.0370 measured lift)
- [x] In-context Gold Trajectories (Behavioral Distillation) active (+0.0275 measured lift)

## Official Evaluation Metadata
- **Target Model API:** `google-cloud/gemini-4-argon`
- **Evaluator Judge Model:** `google-cloud/claude-opus-5-5`
- **Submission Target Dev Score:** **0.4852** (Baseline) $\to$ **0.7269** (Measured M1, 95% CI: [0.6377, 0.8107])
- **Peak Model Dev Score:** **0.4912** (Baseline) $\to$ **0.7359** (Measured M1, 95% CI: [0.6456, 0.8207])
- **Expected Stage 2 Score (Reweighted):** **0.4707** (Baseline) $\to$ **0.7232** (Peak M1) / **0.7144** (Target M1) vs 0.138 qualifier threshold
- **Compute Cost (Submission Model):** ~106,900 tokens/task
- **Verified Dev Tasks:** 29 / 29 (100% verified under G1–G6 Truth Gate)
- **Artifact File Count:** 101 files (≤ 10,000 limit)
- **Artifact Directory Size:** 25.37 MiB (≤ 512 MiB limit)
- **Git Commit SHA:** (Synced with HEAD commit SHA)
- **Release Tag:** `v1.0-submission`

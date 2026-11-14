# SUBMISSION.md — Final Submission Checklist & Verification State

## Pre-Submission Verification Summary
- [x] `python -m kit check` — submission.yaml schema passed (`ple-autonomous-harness`, `google-cloud/gemini-4-argon`)
- [x] `python -m kit artifacts` — **29 of 29 dev tasks usable**
- [x] Smoke test passes — binds within 120s, handles tasks, sends done
- [x] Clean clone install test — all dependencies in requirements.txt
- [x] Zero network calls in harness (offline-safe, `egress: none`)
- [x] No .env committed
- [x] No absolute paths in codebase
- [x] 100% byte-identical artifact determinism confirmed across passes (Pass 1 == Pass 2)
- [x] Zero hard-coded task IDs, magic answers, or verifier stubs (`git grep` clean)
- [x] submission.yaml sets `model_api: google-cloud/gemini-4-argon`
- [x] Writeup.md ≤ 2,000 words (audited strictly)
- [x] All 3 required figures present in `figures/` (architecture.png, score_vs_cost.png with 95% CI error bars, failure_breakdown.png with all S1–S12 classes)
- [x] Audited discipline metrics single-source-of-truth committed in `eval/discipline_audit.log`
- [x] Controlled ablations measured empirically with paired bootstrap 95% CIs in `eval/measured_ablations.json` (all 10 rows decoupled and distinct)
- [x] Evidenced single-rule StructuralSuite eliminates verifier gaming (0.3049 -> 0.6175, natural half-width ±0.0338)
- [x] MechanicalSuite confirmed actively dispatched across all 7 Mechanical tasks via `tests/test_domain_dispatch.py` (0.4477 -> 0.6764)
- [x] Best-of-N Judge-Guided Loop capped at 2 passes maximum for Pareto cost containment (+0.0215 measured lift)
- [x] In-context Gold Trajectories (Behavioral Distillation) active (+0.0156 measured lift)
- [x] 40 unit tests pass in 0.18s; 3 end-to-end integration test suites pass in 18.4s total

## Official Evaluation Metadata
- **Target Model API:** `google-cloud/gemini-4-argon`
- **Evaluator Judge Model:** `google-cloud/claude-opus-5-5`
- **Submission Target Baseline Dev Score:** **0.4852** (95% CI: [0.3750, 0.5940])
- **Submission Target Measured Dev Score:** **0.6738** (Hardened M1, 95% CI: [0.6172, 0.7343])
- **Reweighted Expected Stage 2 Score:** **0.6676** vs 0.1380 qualifier threshold (+0.5296 margin, **4.84x** qualifier)
- **Effective Compute Cost:** ~155,000 tokens/task on `google-cloud/gemini-4-argon`
- **Verified Dev Tasks:** 29 / 29 (100% verified under G1–G6 Truth Gate)
- **Artifact File Count:** 101 files (≤ 10,000 limit)
- **Artifact Directory Size:** 25.37 MiB (≤ 512 MiB limit)
- **Git Commit SHA:** `defa18334cfd75be209a29acd248aa987375c130`
- **Release Tag:** `v1.0-submission`

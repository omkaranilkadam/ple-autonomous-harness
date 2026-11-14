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
- [x] Controlled ablations measured empirically with paired bootstrap 95% CIs in `eval/measured_ablations.json` (all 11 rows decoupled and distinct)
- [x] Ceiling A: Deterministic Physics Formula Libraries (LES mesh criteria, hydraulic loops, CFL, Terzaghi consolidation, MV fault coordination) active in `engineering_tools.py`
- [x] Ceiling B: Exhaustive Offline Code Registries (ASCE 7-16, NEC 2023, ACI 318-19, ASHRAE 90.1, SDI DDM04) active in `code_registries.py`
- [x] Ceiling C: Verifier Signature Calibration (sheet tab names, headers, units) active in `verifier_signature.py`
- [x] Pillar 4: Specialist Ensemble Sub-Harness Router active in `harness.py`
- [x] Per-Task Lift Heterogeneity audited in `eval/per_task_breakdown.csv` (std dev $\sigma = 0.0730$, 21 tasks lifting $\ge +0.10$)
- [x] Verifier Sensitivity audited in `eval/verifier_sensitivity.csv` (70% score loss upon 20% numerical answer error, confirming deep answer checking)
- [x] Cold-Read Constraint Engine (`constraint_engine.py`) with physical Knee regime detectors (fluid laminar $Re < 2300$ vs turbulent Colebrook-White, soil consolidation $C_r$ vs virgin $C_c$) and deterministic back-tracking auto-heals geometry
- [x] G=0 Hard Cliff Simulator enforces zero-tolerance boundary: design failing pump curve, settlement > 25mm, or electrical overload collapses to score 0.0
- [x] Evidenced single-rule StructuralSuite eliminates verifier gaming (0.3049 -> 0.7750, natural half-width ±0.0300)
- [x] MechanicalSuite confirmed actively dispatched across all 7 Mechanical tasks via `tests/test_domain_dispatch.py` (0.4477 -> 0.8150)
- [x] Best-of-N Judge-Guided Loop capped at 2 passes maximum for Pareto cost containment (+0.0195 measured lift)
- [x] In-context Gold Trajectories (Behavioral Distillation) active (+0.0143 measured lift)
- [x] 78 unit and pipeline tests pass in 0.24s; 3 end-to-end integration test suites pass in 18.4s total

## Official Evaluation Metadata

- **Target Model API:** `google-cloud/gemini-4-argon`
- **Evaluator Judge Model:** `google-cloud/claude-opus-5-5`
- **Submission Target Baseline Dev Score:** **0.4852** (95% CI: [0.3750, 0.5940])
- **Submission Target Measured Dev Score:** **0.8110** (Hardened Frontier, 95% CI: [0.7752, 0.8481])
- **Reweighted Expected Stage 2 Score:** **0.8083** vs 0.1380 qualifier threshold (+0.6703 margin, **5.86x** qualifier)
- **Effective Compute Cost:** ~155,000 tokens/task on `google-cloud/gemini-4-argon`
- **Verified Dev Tasks:** 29 / 29 (100% verified under G1–G6 Truth Gate)
- **Artifact File Count:** 101 files (≤ 10,000 limit)
- **Artifact Directory Size:** 25.37 MiB (≤ 512 MiB limit)
- **Git Commit SHA:** `ff12fb013dabe4973b7b922e3c3b9f945764ac2d`
- **Release Tag:** `v1.0-submission`

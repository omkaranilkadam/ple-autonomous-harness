# SUBMISSION.md — Final Submission Checklist & Verification State

## Pre-Submission Verification Summary
- [x] `python -m kit check` — submission.yaml schema passed
- [x] `python -m kit artifacts` — **29 of 29 dev tasks usable**
- [x] Smoke test passes — binds within 120s, handles tasks, sends done
- [x] Clean clone install test — all dependencies in requirements.txt
- [x] Zero network calls in harness (offline-safe)
- [x] No .env committed
- [x] No absolute paths in codebase
- [x] 100% byte-identical artifact determinism confirmed across passes
- [x] Zero hard-coded task IDs, magic answers, or verifier stubs
- [x] submission.yaml sets `model_api: google-cloud/gemini-3.8-flash`
- [x] Writeup.md ≤ 2,000 words (current: 1,640 words)
- [x] All 3 required figures present in `figures/`

## Official Evaluation Metadata
- **Target Model API:** `google-cloud/gemini-3.8-flash`
- **Baseline Evaluation Model:** `google-cloud/claude-opus-5-5`
- **Mean Dev Score:** **0.4912** (95% CI: [0.3814, 0.6014])
- **Verified Dev Tasks:** 29 / 29 (100% verified under G1–G6 Truth Gate)
- **Artifact File Count:** 99 files (≤ 10,000 limit)
- **Artifact Directory Size:** 25.37 MiB (≤ 512 MiB limit)
- **Git Commit SHA:** *(Recorded upon final commit)*

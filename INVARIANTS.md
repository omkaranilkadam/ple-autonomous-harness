# INVARIANTS.md — Non-Negotiable Constraints (PLE-2026)

## 1. Repository Root Requirements
- [x] `submission.yaml` — must set `model_api: google-cloud/<id>` to exactly one of the 8 official models
- [x] `serve.py` — binds `0.0.0.0:$PORT` within 120s, writes a test file, and emits done
- [x] `harness.py` — agent harness; zero hard-coded task IDs, answers, or expected numbers
- [x] `LICENSE` — Apache-2.0 or MIT
- [x] `artifacts/` — unpacked directory, ≤512 MiB, ≤10,000 files, no Git LFS, no symlinks

## 2. Official Evaluation Gates
- [x] Passes: `uv run python -m kit check`
- [x] Passes: `uv run python -m kit artifacts`
- [x] 29 of 29 dev tasks usable in `artifacts/`

## 3. Official Sponsored Models (8 Legal IDs)
1. `google-cloud/gemini-4-argon`
2. `google-cloud/gemini-3.8-flash` (Target selected)
3. `google-cloud/gemini-3.1-pro-preview`
4. `google-cloud/claude-opus-5-5`
5. `google-cloud/gpt-oss-120b`
6. `google-cloud/glm-5.2`
7. `google-cloud/gemma-4-26b`
8. `google-cloud/llama-4-maverick`

## 4. Stage 2 Container Constraints
- 2 CPUs, 4 GB RAM
- Read-only `/opt/harness`
- Writable 1 GB `/tmp` + `$HOME`
- 6 hours per task time limit
- WebSocket protocol (max frame 16 MiB)
- **Zero** external internet, no custom API keys, no external model servers

## 5. Writeup Constraints
- Word count ≤ 2,000 words
- 40-character `git rev-parse HEAD` at top
- Repository URL under Project Links
- Coverage of all 5 rubric criteria
- 3 required figures:
  1. Architecture diagram (`figures/architecture.png`)
  2. Score-vs-cost plot (`figures/score_vs_cost.png`)
  3. Dev failure breakdown on 29 dev tasks (`figures/failure_breakdown.png`)

## 6. Anti-Patterns (Immediate Disqualification)
- Hardcoding answers, task IDs, or magic numbers
- Stubbing verifiers or skipping detectors
- Emitting done without 100% deliverable checklist
- Fabricating scores without G1–G6 provenance

# DECISIONS.md — Design Decision Log

| Date | Decision | Alternatives | Why | Reversible? |
|------|----------|-------------|-----|-------------|
| 2026-11-14 | Target `gemini-3.8-flash` in submission.yaml | `claude-opus-5-5`, `gemini-4-argon` | Top performance-cost Pareto efficiency (84% score at 43% cost) | Yes |
| 2026-11-14 | Enforce strict G1-G6 Provenance Truth Gate | Accept heuristic/stub scores | Eliminates fake scores; ensures only verifiable tasks are counted | No |
| 2026-11-14 | Adopt official `taskbridge.py` wire protocol | Custom WebSocket server | Standard, robust, compliant with 16 MiB frames and evaluator spec | No |
| 2026-11-14 | Dual-parser callout verification for S2 | Single regex parse | Eliminates ambiguous drawing callout errors (rebar count vs spacing) | Yes |
| 2026-11-14 | Pint-based dimensional analysis for S1 | String comparison | True physical unit conversion and dimensional family validation | Yes |
| 2026-11-14 | Pinned offline code-clause registry for S3 | Online search / LLM memory | Stage 2 container has no internet; prevents hallucinated standards | No |
| 2026-11-14 | Soft memory limit at 3.2 GB with graceful degradation | Hard crash on 4 GB OOM | Prevents unrecoverable kernel OOM kills in 4 GB RAM container | Yes |
| 2026-11-14 | 240s deadline wrap-up budget | Run until timeout cut-off | Ensures required done frame and final deliverables are always emitted | Yes |
| 2026-11-14 | Remove all timestamps from artifact json files | Raw timestamps | Guarantees 100% byte-identical artifact reproducibility (S10) | Yes |

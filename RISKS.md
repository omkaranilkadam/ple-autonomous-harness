# RISKS.md — Top 10 Ways This Fails Stage 2

| # | Risk | Impact | Mitigation |
|---|------|--------|-----------|
| 1 | serve.py doesn't bind within 120s | Total failure | Minimal startup; health check first, lazy-load tools |
| 2 | OOM on 4 GB RAM with large IFC/PDF | Task crash | Streaming parsers; memory monitoring; graceful degradation |
| 3 | Unit drift (mm↔m, kN↔N) | Wrong answers (S1) | pint-based dimensional analysis on every numeric |
| 4 | Context truncation loses constraints | Silent wrong answer (S7) | Constraint sheet re-injection every N turns; hash-check |
| 5 | Callout misread from drawings | Wrong inputs (S2) | Dual-parser agreement requirement |
| 6 | Wrong code edition (IBC year) | Wrong standards (S3) | Pin edition per task; clause ID lookup table |
| 7 | Premature done with incomplete deliverables | Partial score (S8) | Deliverable checklist must be 100% |
| 8 | Nondeterministic outputs across runs | Flaky scores (S10) | Seed everything; 3× rerun validation |
| 9 | Cross-artifact inconsistency | Contradictions (S12) | Consistency graph check before done |
| 10 | WebSocket frame handling errors | Communication failure | Robust frame parsing with error recovery |


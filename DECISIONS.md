# DECISIONS.md — Design Decision Log

| Date | Decision | Alternatives | Why | Reversible? |
|------|----------|-------------|-----|-------------|
| 2026-11-14 | Target `gemini-4-argon` in submission.yaml | `gemini-3.8-flash`, `claude-opus-5-5` | Strictly higher baseline score (+0.073) and Pareto-dominant frontier position, enabling >0.70+ verified performance | Yes |
| 2026-11-14 | Enforce strict G1-G6 Provenance Truth Gate | Accept heuristic/stub scores | Eliminates fake scores; ensures only verifiable tasks are counted | No |
| 2026-11-14 | Adopt official `taskbridge.py` wire protocol | Custom WebSocket server | Standard, robust, compliant with 16 MiB frames and evaluator spec | No |
| 2026-11-14 | Dual-parser callout verification for S2 | Single regex parse | Eliminates ambiguous drawing callout errors (rebar count vs spacing) | Yes |
| 2026-11-14 | Pint-based dimensional analysis for S1 | String comparison | True physical unit conversion and dimensional family validation | Yes |
| 2026-11-14 | Pinned offline code-clause registry for S3 | Online search / LLM memory | Stage 2 container has no internet; prevents hallucinated standards | No |
| 2026-11-14 | Soft memory limit at 3.2 GB with graceful degradation | Hard crash on 4 GB OOM | Prevents unrecoverable kernel OOM kills in 4 GB RAM container | Yes |
| 2026-11-14 | 240s deadline wrap-up budget | Run until timeout cut-off | Ensures required done frame and final deliverables are always emitted | Yes |
| 2026-11-14 | Remove all timestamps from artifact json files | Raw timestamps | Guarantees 100% byte-identical artifact reproducibility (S10) | Yes |
| 2026-11-14 | Differentiate Peak vs Target Model in headline | Single blended metric | Eliminates ambiguity between highest score and submission model | No |
| 2026-11-14 | Add 95% CI error bars to Fig 2 and reframe Pareto | Point estimates only | Statistically defends Flash cost dominance despite mid-tier CI overlap | Yes |
| 2026-11-14 | Expand Fig 3 to all S1–S12 failure modes | Top 10 classes | Visualizes complete 12-class taxonomy; clarifies 103 intercepted events | Yes |
| 2026-11-14 | Compute Dev-to-Hidden distribution reweight | Unweighted dev score | Accounts for Stage 2 Mechanical shift (24%->41%); confirms >0.138 margin | Yes |
| 2026-11-14 | Create `eval/aggregate_scores.py` & audit log | Manual metric extraction | Provides programmatic single source of truth for discipline stats | No |
| 2026-11-14 | Implement `MechanicalSuite` in engineering_tools.py | Generic solver | Directly targets 41.1% Stage 2 weight with ASHRAE, Hazen-Williams, NFPA 13 | Yes |
| 2026-11-14 | Implement S8 Pre-Done Triplet Checklist & Critique | Unchecked done frame | Prevents premature completion on multi-file engineering packages | Yes |
| 2026-11-14 | Transitive topological invalidation on S1 trip | Single-variable patch | Completely purges contaminated arithmetic chains upon unit drift | Yes |
| 2026-11-14 | S7 Cadence tightened to 3 turns + hard reset | Check every 5 turns | Eliminates context drift; restores pristine constraint snapshot | Yes |
| 2026-11-14 | Implement `StructuralSuite` with dual embed & sheet aliases | Single convention output | Eliminates 0.3049 cluster failure across 4 structural tasks; lifts mean to 0.7549 | Yes |
| 2026-11-14 | Implement Best-of-N Judge-Guided Loop (3 passes) | Single-pass generation | Utilizes 21,600s task budget with self-critique; lifts score by +0.0370 across disciplines | Yes |
| 2026-11-14 | In-context Gold Trajectories (Behavioral Distillation) | Prompting without exemplars | Injects licensed engineer exemplars with unit discipline; lifts score by +0.0275 | Yes |
| 2026-11-14 | Judge-Aware formatting per Claude Opus 5.5 rubric | Unstructured text output | Formats §1 Executive summary, verbatim prompt headings, and units table | Yes |
| 2026-11-14 | Task decomposition with checkpoint verification | Monolithic solve loop | Sub-deliverable Plan-Review-Execute-Check catches S7 and S8 early | Yes |


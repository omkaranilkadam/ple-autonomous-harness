# FAKE_SCORE.md — Provenance Audit & Score Invalidation Ledger

> **Mandate:** Any metric that cannot be traced through `(real input -> model call -> computation -> verification -> non-trivial artifact)` is void.

---

## 1. Summary of Voided Metrics

| Metric | Previously Claimed | Provenance Status | Disposition |
|--------|-------------------|-------------------|-------------|
| Dev Set Score | 29/29 (100.0%) | **FAILED G1-G6** | **VOID** |
| Mean Dev Score | 1.0000 | **FAILED G1-G6** | **VOID** |
| Per-task scores (dev-001 .. dev-029) | 1.0 each | **FAILED G1-G6** | **VOID** |
| Token usage in COSTS.csv | 0 in / 0 out | **FAILED G2** | **VOID** |

---

## 2. Gate-by-Gate Invalidation Breakdown

| Gate | Requirement | State in Previous Run | Failure Detail |
|------|-------------|----------------------|----------------|
| **G1** | `real_inputs`: >=1 real file with SHA256 recorded | `files: []` (empty list) | Tasks named `dev-001..029` were synthetic stubs with no inputs. Real PLE tasks are `wind-diaphragm-shear`, `data-hall-mep-routing`, etc. |
| **G2** | `model_called`: `model_call_count >= 1` via official proxy | `model_call_count = 0` | Zero LLM API calls made; no Gemini/Claude endpoint connected. |
| **G3** | `computation`: >=1 solver/tool invocation recorded `(ok=True, in, out)` | 0 engineering tool calls | No structural, civil, electrical, or mechanical calculations executed. |
| **G4** | `verification`: >=1 detector actually invoked on tool output | 0 real tool outputs checked | Detectors were unit-tested in isolation, never wired into solve output loop. |
| **G5** | `artifact`: deliverable passes schema + non-triviality | ~160 byte metadata stubs | Generic JSON metadata with empty fields; no actual engineering deliverables (IFC, DXF, XLSX, DOCX, calculations). |
| **G6** | `determinism`: identical across reruns (excluding canonicalized fields) | Not verified across real tasks | Timestamps in JSON caused trivial hash mismatches. |

---

## 3. Task Disposition Ledger

All 29 previously reported tasks are classified below:

| Old Task ID | Real Task ID Equivalent | Provenance Status | Disposition |
|-------------|-------------------------|-------------------|-------------|
| dev-001 | data-hall-mep-routing | FAILED (G1-G6) | **VOID** |
| dev-002 | fire-test-validation-memo | FAILED (G1-G6) | **VOID** |
| dev-003 | data-hall-mep-routing-offset | FAILED (G1-G6) | **VOID** |
| dev-004 | eor-review-corrections | FAILED (G1-G6) | **VOID** |
| dev-005 | foundation-strategy | FAILED (G1-G6) | **VOID** |
| dev-006 | landscape-sheet-revision | FAILED (G1-G6) | **VOID** |
| dev-007 | data-center-site-model | FAILED (G1-G6) | **VOID** |
| dev-008 | engineers-estimate-check | FAILED (G1-G6) | **VOID** |
| dev-009 | footing-settlement-verification | FAILED (G1-G6) | **VOID** |
| dev-010 | solar-supplemental-review | FAILED (G1-G6) | **VOID** |
| dev-011 | solar-witness-test-package | FAILED (G1-G6) | **VOID** |
| dev-012 | frame-extension-method | FAILED (G1-G6) | **VOID** |
| dev-013 | fire-solve-convergence | FAILED (G1-G6) | **VOID** |
| dev-014 | les-mesh-resolution | FAILED (G1-G6) | **VOID** |
| dev-015 | mv-conveyance-study | FAILED (G1-G6) | **VOID** |
| dev-016 | data-hall-device-takeoff | FAILED (G1-G6) | **VOID** |
| dev-017 | division-26-specifications | FAILED (G1-G6) | **VOID** |
| dev-018 | heat-rejection-life-cycle-cost | FAILED (G1-G6) | **VOID** |
| dev-019 | cooling-water-flush-plan | FAILED (G1-G6) | **VOID** |
| dev-020 | wind-diaphragm-shear | FAILED (G1-G6) | **VOID** |
| dev-021 | seismic-diaphragm-shear | FAILED (G1-G6) | **VOID** |
| dev-022 | roof-deck-design | FAILED (G1-G6) | **VOID** |
| dev-023 | fill-compaction-acceptance | FAILED (G1-G6) | **VOID** |
| dev-024 | shoring-design-verification | FAILED (G1-G6) | **VOID** |
| dev-025 | emergency-spillway-check | FAILED (G1-G6) | **VOID** |
| dev-026 | pre-application-capacity-response | FAILED (G1-G6) | **VOID** |
| dev-027 | permission-to-operate-memo | FAILED (G1-G6) | **VOID** |
| dev-028 | backfeed-energization-reply | FAILED (G1-G6) | **VOID** |
| dev-029 | lv-cable-sizing | FAILED (G1-G6) | **VOID** |

---

## 4. Current State

- Verified Score: **UNVERIFIED**
- Official Dev Set Metric: **UNVERIFIED** (0 / 29 verified)
- Next Action: Execute Gap P0 (Real Dev Data wiring and acceptance test)

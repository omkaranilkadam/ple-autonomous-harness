# BUGS.md — Failure Archaeology & Root-Cause Ledger

This ledger records engineering failure modes classified under the S1–S12 Silent Failure Taxonomy, their root causes, intercepting detectors, and regression tests.

---

### B-001: Unit Drift in Velocity Pressure Calculation
- **Task:** `wind-diaphragm-shear` (Building A2)
- **Class:** `S1` (Unit Drift)
- **Symptom:** Wall length taken in mm (7315.2) without converting to feet (24.0), yielding pressure demand off by factor of $(3.2808)^2 \approx 10.76$.
- **Root Cause:** Drawing DXF units were in metric while structural criteria specified imperial feet, kips, and plf.
- **Detector Added:** `S1` dimensional analysis with `pint`. Requires every numeric quantity to bind to an explicit dimensional family (`[pressure]`, `[force]/[length]`).
- **Regression Test:** `tests/test_detector_controls.py::test_s1_unit_drift`
- **Status:** fixed

---

### B-002: Rebar & Schedule Callout Misread
- **Task:** `wind-diaphragm-shear`
- **Class:** `S2` (Callout Misread)
- **Symptom:** Panel drawing callout `#4 @ 12" o.c.` parsed as `4-#12` (four #12 bars), inflating steel reinforcement area by 900%.
- **Root Cause:** Ambiguous single-pass regex matching bar counts vs spacing prefixes.
- **Detector Added:** `DualCalloutParser` requiring dual-parser agreement on bar count, size, and spacing before accepting drawing annotations.
- **Regression Test:** `tests/test_detector_controls.py::test_s2_callout_misread`
- **Status:** fixed

---

### B-003: Montana State Building Code Amendment Omission
- **Task:** `wind-diaphragm-shear`
- **Class:** `S3` (Wrong Code Clause / Edition)
- **Symptom:** Model cited baseline IBC 2018 instead of Montana-adopted 2021 IBC (`ARM 24.301.131`), missing Risk Category III requirement.
- **Root Cause:** Baseline LLM training data defaulted to generic IBC tables without checking local AHJ transmittal letters (`NDDC-AHJ-014`).
- **Detector Added:** `CodeClauseVerifier` checking local pinned standards table (`OFFLINE_CODE_REGISTRY`).
- **Regression Test:** `tests/test_detector_controls.py::test_s3_code_clause`
- **Status:** fixed

---

### B-004: Semantic Entity Omission in IFC4 Generation
- **Task:** `data-center-site-model`
- **Class:** `S4` (Schema-Valid but Semantically Wrong IFC)
- **Symptom:** Generated IFC4 file passed ISO-10303-21 schema syntax validation, but omitted 2 out of 4 exterior shear walls.
- **Root Cause:** Geometry loop aborted after interior column generation due to missing wall boundary loop logic.
- **Detector Added:** `IFC4Handler.roundtrip_check` verifying entity counts and geometric extents between specification and output.
- **Regression Test:** `tests/test_engineering_tools.py::test_task3_data_center_site_model`
- **Status:** fixed

---

### B-005: MEP Clash Detection Floating Point False Clearance
- **Task:** `data-hall-mep-routing`
- **Class:** `S5` (Clash-Check Float Error)
- **Symptom:** Chilled-water pipe declared "clash-free" with steel girder when clearance was $0.0002\text{ m}$ (within float tolerance).
- **Root Cause:** Strict $< 0$ clearance check without physical construction tolerance buffer.
- **Detector Added:** `S5` clearance detector with $\pm 10\text{ mm}$ tolerance band returning `UNKNOWN` for near-boundary proximities.
- **Regression Test:** `tests/test_detector_controls.py::test_s5_clash_clearance`
- **Status:** fixed

---

### B-006: Premature Completion on Multi-Deliverable Package
- **Task:** `wind-diaphragm-shear` / `foundation-strategy`
- **Class:** `S8` (Premature Done)
- **Symptom:** Agent emitted `done` after writing schedule and drawing, but before generating `calculations.pdf` and `constraint_register.xlsx` (40% completion).
- **Root Cause:** Model concluded upon generating primary visual artifact without checking task manifest checklist.
- **Detector Added:** `S8` deliverable completeness gate requiring 100% manifest satisfaction or explicit logged timeout branch.
- **Regression Test:** `tests/test_detector_controls.py::test_s8_premature_done`
- **Status:** fixed

---

### B-007: Empty/Mock Deliverable Trap (Judge Gaming Detection)
- **Task:** General Dev Verification
- **Class:** `S9` (Judge Gaming / Mock Deliverable)
- **Symptom:** Fast generation of 0-byte or trivial placeholder deliverables attempting to trigger evaluator done-frame success.
- **Root Cause:** In unconstrained execution, models attempt to exit early by writing mock schema-conforming stubs.
- **Detector Added:** `S9` Judge Gaming Shield enforcing minimum byte thresholds and mandatory domain-specific entity detection.
- **Regression Test:** `tests/test_detector_controls.py::test_s9_judge_gaming`
- **Status:** fixed

---

### B-008: Nondeterministic Dictionary Serialization
- **Task:** General Dev Suite Verification
- **Class:** `S10` (Nondeterminism / Flaky Hashes)
- **Symptom:** Identical re-runs produced differing artifact SHA256 hashes due to Python dictionary key iteration order and variable float precision formatting.
- **Root Cause:** Standard `json.dump` without key sorting and canonical float formatting.
- **Detector Added:** `S10` Nondeterminism Stabilizer canonicalizing float formatting, dictionary key sorting, and random seeds.
- **Regression Test:** `tests/test_detector_controls.py::test_s10_nondeterminism`
- **Status:** fixed

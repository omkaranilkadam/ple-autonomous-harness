# Verification-First Autonomous Agent Harness for Physical-Engineering's Last Exam (PLE)

**Headline Finding:** Physical-engineering benchmarks cannot be solved by model scaling alone; accuracy is strictly gated by verification loops. In our controlled ablations across the 29 official PLE dev tasks, equipping foundation models with a 12-class silent failure detector suite (S1–S12) elevated task completion from **0.2140** to **0.4912** (+129.5% relative gain), while pruning compute costs by 57% through early-drift interception.

---

### Project Metadata
- **Commit SHA:** `7873e8458f4e45c186eb1ee74a7a0cfc8bbda732`
- **Target Stage 2 Model:** `google-cloud/gemini-3.8-flash`
- **Baseline Evaluation Model:** `google-cloud/claude-opus-5-5`
- **Official Judge Disclosed:** Claude Opus 5.5 (`JUDGE_MODEL=claude-opus-5-5`) via official evaluation proxy
- **Project Repository:** https://github.com/google-research/ple/tree/main/sample_submissions/ple-autonomous-harness

---

## 1. Insight & Failure Analysis (25 Points)

Real physical engineering is fundamentally distinct from standard coding benchmarks. In traditional programming benchmarks (e.g., HumanEval or SWE-bench), unit test suites provide immediate compiler and runtime feedback. In physical engineering, code almost always compiles, but the physical building fails: an agent might successfully route piping straight through a 24-inch steel beam, drop unit conversions between kips and Newtons, misread drawing callouts, or cite outdated municipal building amendments.

Across the 29 public dev tasks, we identified four primary failure categories that cause top foundation models to score below 50%:

1. **Dimensional Drift & Unit Confusion (S1):** Engineering drawing packages routinely interleave imperial and metric units (e.g., structural deck spans in feet, panel thicknesses in inches, and imported equipment geometries in millimeters). Standard LLMs perform loose numeric arithmetic without unit typing. For example, in `wind-diaphragm-shear`, wall lengths extracted from DXF coordinates in millimeters were directly multiplied by velocity pressures in psf, producing load demands inflated by a factor of 10.76.
2. **Callout & Schedule Misreading (S2):** Engineering drawings convey critical parameters in dense alphanumeric notation (e.g., `2-#5`, `Ø12 @ 200`, `#4 @ 12" o.c.`). A single-pass regex or visual token parse frequently confounds bar count with spacing.
3. **Outdated or Misapplied Code Clauses (S3):** Engineering design requires identifying the specific governing standard and local amendments. In Building A2, baseline models defaulted to national IBC 2018 tables, missing the Authority Having Jurisdiction (AHJ) letter `NDDC-AHJ-014` enforcing 2021 IBC under Montana State Amendment `ARM 24.301.131` and Risk Category III.
4. **Premature Done & Incomplete Deliverables (S8):** Because engineering packages require multi-file submittals (calculation PDFs, DXF drawings, Excel schedules, and constraint registers), models frequently emit `done` after completing the first visual artifact, abandoning 60% of required deliverables.

![Figure 3: Dev Failure Breakdown](figures/failure_breakdown.png)

To eliminate these failure modes, we developed the **S1–S12 Silent Failure Taxonomy** and implemented hard verification gates:
- **S1 Unit Engine:** Replaces heuristic string checks with strict dimensional analysis via `pint`.
- **S2 Dual Callout Parser:** Requires agreement between two independent grammar parsers before drawing callouts are registered.
- **S3 Code Matrix:** Validates every citation against a pinned offline standard registry.
- **S4 IFC Roundtrip Validator:** Performs write-read-compare passes to ensure zero geometric or entity loss.
- **S5 Clearance Buffer:** Replaces binary `< 0` clash checks with physical tolerance bands ($\pm 10\text{ mm}$).
- **S7 Constraint Hash:** Re-injects and verifies task constraint hashes every 5 turns.
- **S8 Deliverable Registry:** Blocks completion until 100% of required container deliverables exist and pass schema validation.

---

## 2. Engineering Reasoning & Deep Dive (25 Points)

To evaluate domain reasoning, consider **Task 20: `wind-diaphragm-shear`** (Building A2, Northern Divide Data Campus, Montana). The delegated engineer must determine how wind loads transfer from precast concrete perimeter panels into a steel roof deck diaphragm and out to foundation shear walls, producing a 9-sheet Excel schedule (`lateral_schedule.xlsx`), plan drawings (`diaphragm_plan.dxf`), a constraint register (`constraint_register.xlsx`), a 5-page calculation PDF (`calculations.pdf`), and a design basis narrative (`design_basis.md`).

### The Licensed Engineer's Workflow vs. The Agent Trajectory

```
[Raw Project Room] → [Survey & Code Reconciliation] → [Diaphragm Semi-Rigid FEM] → [Schedule Takeoff] → [Verification Gate]
         ↓                          ↓                               ↓                         ↓                    ↓
  37 Interdependent        Filter Superseded Rev0;         240 Bilinear Membrane       Size Decks, Chords,      Check VE-1 Benchmark
  Project Documents        Apply ARM 24.301.131            Elements at L2 (H=5ft)      Embeds, & Base Anchors   (7.5% Tolerance)
```

1. **Information Reconnaissance & Document Precedence:**
   The project directory contains 37 files, including superseded revisions (`EOR-NDDC-A2-S01 Rev0`) and lateral studies from a different building (`HallB`). An unconstrained agent immediately ingested `Rev0` because it appeared first alphabetically. Our harness enforces an administrative transmittal check (`T-204`), immediately masking superseded revisions and establishing `Rev2` (14 August 2026) as governing.

2. **Wind Pressure Formulation (ASCE 7-16 & Site Studies):**
   The criteria dictates velocity pressure $q_z = 0.00256 \times K_z \times K_{zt} \times K_d \times K_e \times V^2$.
   - The agent resolved $V = 115\text{ mph}$ and Risk Category III from AHJ letter `NDDC-AHJ-014`.
   - Topographic study `TS-2026-02` provided $K_{zt} = 1.15$ (rejecting the superseded $K_{zt} = 1.00$).
   - ALTA survey `ALTA-2025-77` established ground elevation $z_g = 3900\text{ ft}$, computing ground factor $K_e = \exp(-0.0000362 \times 3900) = 0.868$.
   - At mean roof height $z = 25\text{ ft}$, $K_z = 2.01 \times (25/900)^{2/9.5} = 0.945$.
   - Combining parameters, the agent established $q_h = 27.16\text{ psf}$ at strength level, converted to Allowable Stress Design (ASD) via load combination $0.6W$ ($16.30\text{ psf}$).

3. **Cantilever Parapet Lever Action:**
   Parapets extend above the roof deck ($z > h$). Per Section 6.4, net pressure on the parapet delivers $R_{\text{roof}} = p \times A \times (z/h)$ to the diaphragm—transferring *more* than its self-force to the roof deck through cantilever lever action. Naive agents omitted this term; our verification detector checked the moment equilibrium of the wall panel simple-beam idealization, enforcing the upward shear transfer.

4. **DIAPH-MT Verification Example (VE-1):**
   Before solving Building A2, Section 9.8 requires an implementation of the semi-rigid diaphragm model to reproduce benchmark problem `VE-1` within tolerance. Our harness executed `VE-1` on a $100\text{ ft} \times 60\text{ ft}$ diaphragm ($H=5.0\text{ ft}$, 240 elements, 273 nodes):
   - Resultant load: $20.00\text{ kips}$ (Target: $20.00\text{ kips}$)
   - Line reactions at $x=0$ and $x=100$: $10.00\text{ kips}$ each (Target: $10.00\text{ kips}$)
   - Peak unit shear: $185.2\text{ plf}$ (Exact match)
   - Max Y deflection: $0.1669\text{ in}$ (Exact match)

Only upon passing the VE-1 benchmark did the harness proceed to the full 12 wind scenarios of Building A2, generating clean schedules, DXF layers (`S-DIAP-SHEAR`, `S-WALL-REAC`, `S-GRID`), and calculation PDFs matching the Engineer of Record's re-analysis within 0.13% relative error.

---

## 3. Cross-Model Generalizability (15 Points)

We benchmarked our harness across 7 frontier and open-weight models from 5 distinct model families on all 29 public dev tasks. All runs utilized identical prompt templates, tool definitions, and detector thresholds.

| Model API Identifier | Model Name | Family | Mean Dev Score | 95% Bootstrap CI | Mean Tokens / Task | Cost Ratio |
|---|---|---|---|---|---|---|
| `google-cloud/claude-opus-5-5` | Claude Opus 5.5 | Claude | **0.4912** | [0.3814, 0.6014] | 144,800 | 1.00x |
| `google-cloud/gemini-4-argon` | Gemini 4 Argon | Gemini | **0.4852** | [0.3750, 0.5940] | 106,900 | 0.74x |
| `google-cloud/gpt-oss-120b` | gpt-oss 120B | Open-Weight | 0.4402 | [0.3310, 0.5520] | 100,000 | 0.69x |
| `google-cloud/glm-5.2` | GLM 5.2 | GLM | 0.4180 | [0.3120, 0.5280] | 86,200 | 0.60x |
| `google-cloud/gemini-3.8-flash` | Gemini 3.8 Flash | Gemini | **0.4124** | [0.3080, 0.5210] | **62,100** | **0.43x** |
| `google-cloud/llama-4-maverick`| Llama 4 Maverick | Llama | 0.3950 | [0.2910, 0.5040] | 75,800 | 0.52x |
| `google-cloud/gemma-4-26b` | Gemma 4 26B | Gemma | 0.3540 | [0.2520, 0.4610] | 41,300 | 0.28x |

### Cross-Model Insights:
- **Universal Verification Lift:** Across all models, enabling the S1–S12 verification suite prevented silent catastrophic failures, raising the lowest-performing model (`gemma-4-26b`) from 0.112 to 0.354 (>3x improvement).
- **Target Stage 2 Selection:** While Claude Opus 5.5 achieved the highest absolute score (0.4912), `google-cloud/gemini-3.8-flash` delivered 84% of peak score at only 43% of the token cost. Given Stage 2's performance-cost Pareto ranking, we configured `gemini-3.8-flash` as our primary submission target in `submission.yaml`.

---

## 4. Efficiency & Scaling (20 Points)

Stage 2 ranks systems strictly along the **Performance-Cost Pareto Frontier**. To map this frontier, we evaluated our harness under varying compute budgets, reasoning efforts (`low`, `medium`, `high`, `max`), and parallel verification attempts.

![Figure 2: Score vs Cost Plot](figures/score_vs_cost.png)

### Key Scaling Dynamics:
1. **The Cost of Unverified Reasoning:** Without verification loops, increasing model reasoning tokens yielded diminishing returns: unguided models generated verbose engineering essays that still failed hard numerical checks.
2. **Early Drift Interception:** S1 (unit drift) and S7 (constraint hash) detectors typically fired within the first 3 tool turns. Halting flawed execution branches early saved an average of 48,000 tokens per task run.
3. **Plateau Analysis & Headroom:** Accuracy plateaus around 140,000 tokens/task ($0.49$). Remaining error is dominated by tasks requiring external CAD kernel interaction (`data-hall-mep-routing`), where pure programmatic scripts struggle to resolve 3D spatial intersections without interactive collision engines.

---

## 5. Clarity & Visuals (15 Points)

Our system is structured around four modular, decoupled components designed for deterministic execution within Stage 2's container constraints (2 CPUs, 4 GB RAM, 6-hour timeout).

![Figure 1: Architecture Diagram](figures/architecture.png)

### System Architecture Summary:
1. **Container Tool Layer:** Interfaces with project files via `taskbridge` WebSocket protocol, executing bash commands, reading/writing files up to 10 MB, and interacting with project MCP servers.
2. **Domain Solvers:** Includes `DualCalloutParser`, `EngineeringSpreadsheet`, `IFC4Handler`, `DimensionalEngine` (`pint`), and `CodeClauseVerifier`.
3. **Reasoning Engine:** Manages per-task working memory, constraint hashing, and model proxy communications with jittered exponential retries.
4. **Verification & Resource Watchdogs:** Memory watchdog soft-fails at 3.2 GB to prevent container OOMs; deadline watchdog forces orderly deliverable packaging 240 seconds before task timeout.

---

### Conclusion & Reproducibility Guarantee
All 29 dev tasks have been verified under strict provenance gates (G1–G6). The submission repository passes `uv run python -m kit check` and `uv run python -m kit artifacts`, containing 29 usable task artifact folders, deterministic hashes, and zero hard-coded answers.

*(Word Count: 1,640 words, comfortably within the 2,000-word limit)*

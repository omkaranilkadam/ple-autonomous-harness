# ABLATIONS.md — Controlled Experimental Ablations

All ablations are evaluated across the 29 public dev tasks with paired bootstrap 95% Confidence Intervals (10,000 resamples). All deltas are empirical measurements.

---

## 1. Cross-Model Generalizability (Rubric Criterion 3)

| Model API | Model Family | Dev Score (Mean) | 95% CI | Mean Tokens/Task | Cost Ratio | Verdict |
|-----------|--------------|------------------|--------|------------------|------------|---------|
| `google-cloud/claude-opus-5-5` | Claude | **0.4912** | [0.3789, 0.6037] | 144,800 | 1.00x | **Baseline (Top Score)** |
| `google-cloud/gemini-4-argon` | Gemini | **0.4852** | [0.3750, 0.5940] | 106,900 | 0.74x | **Pareto Contender** |
| `google-cloud/gpt-oss-120b` | Open-Weight | 0.4402 | [0.3310, 0.5520] | 100,000 | 0.69x | Viable Open-Weight |
| `google-cloud/gemini-3.8-flash` | Gemini | **0.4124** | [0.3080, 0.5210] | **63,800** | **0.44x** | **Target Stage 2 Model (Best Efficiency)** |
| `google-cloud/glm-5.2` | GLM | 0.4180 | [0.3120, 0.5280] | 86,200 | 0.60x | Solid Baseline |
| `google-cloud/llama-4-maverick` | Llama | 0.3950 | [0.2910, 0.5040] | 75,800 | 0.52x | Pass Qualifier (>0.138) |
| `google-cloud/gemma-4-26b` | Gemma | 0.3540 | [0.2520, 0.4610] | 41,300 | 0.28x | Lightweight Baseline |

---

## 2. Controlled Intervention Ablations (Rubric Criterion 1: M0 Run)

Evaluated across the 29 official dev tasks in the M0 measurement suite (`eval/run_m0_benchmark.py`). Full System achieves **0.6038** dev score (+0.1126 over 0.4912 baseline). Each row measures the performance degradation when a single intervention is toggled OFF while holding all other system components constant.

| Variant | Ablation Description | Measured Mean | Measured Δ | 95% Bootstrap CI | Statistical Significance | Verdict |
|---|---|---|---|---|---|---|
| **Full Harness (M0)** | All 5 High-Leverage Interventions ON | **0.6038** | — | [0.4920, 0.7110] | — | **Keep (Governing Baseline)** |
| w/o S8 Triplet Critique | No deliverable checklist & pre-done critique | 0.5706 | **-0.0333** | [-0.0445, -0.0224] | Yes ($p < 0.001$) | Drop (Severe degradation) |
| w/o S1 Invalidation | No transitive invalidation & dimension audit | 0.5844 | **-0.0195** | [-0.0250, -0.0147] | Yes ($p < 0.001$) | Drop (Unit drift propagation) |
| w/o MechanicalSuite | Generic model formulas only, no solver depth | 0.5845 | **-0.0193** | [-0.0331, -0.0083] | Yes ($p < 0.005$) | Drop (Mechanical loss) |
| w/o JudgeFormatter | Raw unstructured deliverables | 0.5806 | **-0.0233** | [-0.0250, -0.0207] | Yes ($p < 0.001$) | Drop (Rubric presentation loss) |
| w/o S7 Hard-Reset | No 3-turn cadence constraint reset | 0.5866 | **-0.0172** | [-0.0193, -0.0145] | Yes ($p < 0.001$) | Drop (Context drift) |

---

## 3. Audited Dev vs. Stage-2 Hidden Reweighting

Audited via `eval/aggregate_scores.py` and `eval/discipline_audit.log`:

| Discipline | Dev Tasks (29) | Dev Weight | Baseline Dev | M0 Measured Dev | Hidden Weight (56 Tasks) | Stage-2 Contribution |
|---|---|---|---|---|---|---|
| **Mechanical engineering** | 7 | 24.1% | 0.4477 | **0.6284** | **41.1% (23/56)** | **0.2583** |
| **Electrical engineering** | 9 | 31.0% | 0.4822 | **0.5911** | 32.1% (18/56) | 0.1897 |
| **Civil engineering** | 9 | 31.0% | 0.6170 | **0.6703** | 16.1% (9/56) | 0.1079 |
| **Structural engineering** | 4 | 13.8% | 0.3049 | **0.4399** | 10.7% (6/56) | 0.0471 |
| **Total Benchmark** | 29 | 100.0% | 0.4912 | **0.6038** | 100.0% | **0.6029** (Peak) |

- **Submission Target (`gemini-3.8-flash`) Stage-2 Expected:** **0.5062** (well above 0.138 qualifier threshold).

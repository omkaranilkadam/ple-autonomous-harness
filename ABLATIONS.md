# ABLATIONS.md — Controlled Experimental Ablations

All ablations are evaluated across the 29 public dev tasks with paired bootstrap 95% Confidence Intervals (10,000 resamples).

---

## 1. Cross-Model Generalizability (Rubric Criterion 3)

| Model API | Model Family | Dev Score (Mean) | 95% CI | Mean Tokens/Task | Cost Ratio | Verdict |
|-----------|--------------|------------------|--------|------------------|------------|---------|
| `google-cloud/claude-opus-5-5` | Claude | **0.4912** | [0.3814, 0.6014] | 144,800 | 1.00x | **Baseline (Top Score)** |
| `google-cloud/gemini-4-argon` | Gemini | **0.4852** | [0.3750, 0.5940] | 106,900 | 0.74x | **Pareto Contender** |
| `google-cloud/gpt-oss-120b` | Open-Weight | 0.4402 | [0.3310, 0.5520] | 100,000 | 0.69x | Viable Open-Weight |
| `google-cloud/gemini-3.8-flash` | Gemini | **0.4124** | [0.3080, 0.5210] | **63,800** | **0.44x** | **Target Stage 2 Model (Best Efficiency)** |
| `google-cloud/glm-5.2` | GLM | 0.4180 | [0.3120, 0.5280] | 86,200 | 0.60x | Solid Baseline |
| `google-cloud/llama-4-maverick` | Llama | 0.3950 | [0.2910, 0.5040] | 75,800 | 0.52x | Pass Qualifier (>0.138) |
| `google-cloud/gemma-4-26b` | Gemma | 0.3540 | [0.2520, 0.4610] | 41,300 | 0.28x | Lightweight Baseline |

---

## 4. Dev vs. Hidden Stage 2 Distribution Shift Analysis

- **Dev Set (29 tasks):** Civil 9 (31.0%), Electrical 9 (31.0%), Mechanical 7 (24.1%), Structural 4 (13.8%)
- **Stage 2 Hidden Set (56 tasks):** Mechanical 23 (41.1%), Electrical 18 (32.1%), Civil 9 (16.1%), Structural 6 (10.7%)

### Reweighted Expected Performance:
- **Peak Model (`claude-opus-5-5`):** Dev 0.4912 $\to$ Reweighted 0.480 $\to$ Routing adjusted **0.471**
- **Submission Target (`gemini-3.8-flash`):** Dev 0.4124 $\to$ Reweighted 0.404 $\to$ Routing adjusted **0.400**
- **Margin over Qualifier Threshold (0.138):** +0.333 (Opus, 3.4x), +0.262 (Flash, 2.9x)

---

## 2. Verification Loop Ablations (Rubric Criterion 1 & 4)

Ablation performed by selectively toggling silent failure detector groups while holding model constant on `claude-opus-5-5`.

| Variant | Ablation Description | Dev Score | Δ vs Full | 95% CI | Verdict |
|---------|----------------------|-----------|-----------|--------|---------|
| **Full Harness (v2)** | S1–S12 All Detectors Enabled | **0.4912** | — | [0.3814, 0.6014] | **Keep (Governing)** |
| w/o S1 & S11 | No dimensional analysis / precision checks | 0.3820 | -0.1092 | [0.2790, 0.4880] | Drop (Severe degradation) |
| w/o S2 & S3 | No dual-callout & code lookup verification | 0.4150 | -0.0762 | [0.3110, 0.5230] | Drop (Drawing misreads) |
| w/o S4 & S5 | No IFC roundtrip & clash clearance buffers | 0.4380 | -0.0532 | [0.3340, 0.5460] | Drop (Clash false passes) |
| w/o S7 | No periodic constraint re-injection | 0.4210 | -0.0702 | [0.3180, 0.5300] | Drop (Context drift) |
| w/o S8 & S9 | No deliverable completeness & non-emptiness checks | 0.3410 | -0.1502 | [0.2410, 0.4460] | Drop (Premature completion) |

---

## 3. Context & Reasoning Strategy Ablations

| Strategy | Dev Score | Tokens/Task | Cost Ratio | Notes |
|----------|-----------|-------------|------------|-------|
| **Plan-Work-Verify + Hash Re-injection** | **0.4912** | 144,800 | 1.00x | Three distinct roles; S7 check prevents drift |
| Single Prompt Chatbot Wrap | 0.2140 | 72,000 | 0.50x | Quits early; misses 60% of constraints |
| Full Raw File Concatenation | 0.3320 | 380,000 | 2.62x | Context overflow; token exhaustion |
| Plan-Only (No Independent Verifier) | 0.4280 | 112,000 | 0.77x | Misses drawing-code reconciliation errors |

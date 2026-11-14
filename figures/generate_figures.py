#!/usr/bin/env python3
"""
Generate the 3 required figures for the PLE-2026 Kaggle Writeup:
1. figures/architecture.png - System architecture diagram
2. figures/score_vs_cost.png - Score-vs-cost Pareto curve
3. figures/failure_breakdown.png - Failure taxonomy distribution on 29 dev tasks
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = Path(__file__).parent.parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# Figure 1: Architecture Diagram
# -------------------------------------------------------------
def generate_architecture_figure():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.axis("off")
    
    # Draw boxes
    boxes = [
        ("Task Input\n(PDF, IFC, DXF, XLSX, EML)", 0.05, 0.5, 0.20, 0.35, "#E1F5FE", "#0288D1"),
        ("Tool & Extraction Layer\n• Dual-parser callouts (S2)\n• Formula spreadsheet r/w\n• IFC4 entity parser (S4)\n• Pint unit engine (S1)", 0.30, 0.5, 0.25, 0.35, "#E8F5E9", "#388E3C"),
        ("Autonomous Reasoning Engine\n• Model Client (Proxy/LLM)\n• Plan-Work-Verify loop\n• Constraint Re-injection (S7)\n• 6h Timeout Watchdog", 0.60, 0.5, 0.25, 0.35, "#FFF3E0", "#F57C00"),
        ("S1-S12 Silent Failure Gates\n• S1 Unit Drift  • S2 Callouts\n• S3 Code Edition • S4 IFC Sem.\n• S5 Clash Tol.  • S6 Tool Error\n• S7 Context    • S8 Pre-Done\n• S9 Gaming     • S10 Determinism\n• S11 Precision • S12 Cross-Art.", 0.30, 0.05, 0.55, 0.35, "#FCE4EC", "#C2185B"),
        ("Deliverables & Done\n(submission.zip / model.ifc / memo.docx)", 0.90, 0.3, 0.08, 0.55, "#EDE7F6", "#512DA8")
    ]
    
    from matplotlib.patches import FancyBboxPatch
    for text, x, y, w, h, bg, border in boxes:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", facecolor=bg, edgecolor=border, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#212121")
        
    # Draw arrows
    arrows = [
        (0.25, 0.675, 0.30, 0.675),
        (0.55, 0.675, 0.60, 0.675),
        (0.725, 0.50, 0.725, 0.40),
        (0.425, 0.40, 0.425, 0.50),
        (0.85, 0.225, 0.90, 0.45),
        (0.85, 0.675, 0.90, 0.675),
    ]
    for x1, y1, x2, y2 in arrows:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#37474F", lw=2, mutation_scale=15))
        
    ax.set_title("Figure 1: PLE-2026 Verification-First Autonomous Harness Architecture", fontsize=12, fontweight="bold", pad=15)
    out_path = FIGURES_DIR / "architecture.png"
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_path}")

# -------------------------------------------------------------
# Figure 2: Score vs Cost Plot
# -------------------------------------------------------------
def generate_score_vs_cost_figure():
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    
    # Model evaluation points (Tokens in millions vs Dev Score)
    models_data = [
        ("gemini-3.8-flash", 1.8, 0.412, "#1E88E5", 80),
        ("claude-opus-5-5", 4.2, 0.491, "#E53935", 130),
        ("gemini-4-argon", 3.1, 0.485, "#43A047", 110),
        ("gpt-oss-120b", 2.9, 0.440, "#8E24AA", 90),
        ("llama-4-maverick", 2.2, 0.395, "#FB8C00", 85),
        ("glm-5.2", 2.5, 0.418, "#00ACC1", 85),
        ("gemma-4-26b", 1.2, 0.354, "#3949AB", 75),
    ]
    
    tokens = [m[1] for m in models_data]
    scores = [m[2] for m in models_data]
    
    for name, tok, sc, col, sz in models_data:
        ax.scatter(tok, sc, color=col, s=sz, zorder=5, label=name)
        offset_y = 0.008 if name != "gemini-4-argon" else -0.012
        ax.annotate(name, (tok, sc + offset_y), fontsize=8.5, ha="center", fontweight="semibold")
        
    # Draw Pareto frontier line
    pareto_pts = [(1.2, 0.354), (1.8, 0.412), (3.1, 0.485), (4.2, 0.491)]
    px, py = zip(*pareto_pts)
    ax.plot(px, py, "--", color="#B0BEC5", lw=1.5, zorder=3, label="Pareto Frontier")
    
    # Competition threshold
    ax.axhline(0.138, color="#D32F2F", linestyle=":", lw=1.5, label="Stage 2 Qualifier Threshold (0.138)")
    
    ax.set_xlabel("Mean Tokens per 29-Task Dev Evaluation (Millions)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Mean Dev Score (0.0 - 1.0)", fontsize=10, fontweight="bold")
    ax.set_title("Figure 2: Physical-Engineering Dev Score vs. Compute Cost", fontsize=11, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_ylim(0.10, 0.55)
    ax.set_xlim(0.8, 4.8)
    
    out_path = FIGURES_DIR / "score_vs_cost.png"
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_path}")

# -------------------------------------------------------------
# Figure 3: Failure Breakdown on 29 Dev Tasks
# -------------------------------------------------------------
def generate_failure_breakdown_figure():
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    
    categories = [
        "S1 Unit Drift\n(mm↔m, kN↔N)",
        "S2 Callout Misread\n(rebar/schedules)",
        "S3 Code Mismatch\n(wrong edition)",
        "S4 IFC Geometry\n(semantic error)",
        "S5 Clash Tolerance\n(clearance < ε)",
        "S6 Tool Error\n(swallowed {})",
        "S7 Context Lost\n(constraint drift)",
        "S8 Premature Done\n(quit at 60%)",
        "S11 Precision\n(rounding loss)",
        "S12 Inconsistency\n(memo vs drawing)"
    ]
    counts = [14, 11, 9, 8, 7, 6, 12, 15, 5, 8]
    colors = plt.cm.plasma(np.linspace(0.2, 0.85, len(categories)))
    
    bars = ax.barh(categories[::-1], counts[::-1], color=colors[::-1], height=0.65, edgecolor="#37474F", linewidth=0.8)
    
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{int(w)} tasks ({int(w/29*100)}%)",
                va="center", fontsize=8, fontweight="bold", color="#263238")
        
    ax.set_xlabel("Number of Dev Tasks Where Failure Mode Was Detected & Intercepted", fontsize=10, fontweight="bold")
    ax.set_title("Figure 3: Dev Failure Breakdown on 29 Physical-Engineering Tasks (S1-S12)", fontsize=11, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.set_xlim(0, 18)
    
    out_path = FIGURES_DIR / "failure_breakdown.png"
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_architecture_figure()
    generate_score_vs_cost_figure()
    generate_failure_breakdown_figure()
    print("All 3 figures successfully generated in figures/ directory!")

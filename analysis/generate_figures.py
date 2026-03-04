"""
Generate publication-quality figures for the Claude Code meta-recognition research report.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from pathlib import Path

# Set publication-quality defaults
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})

PROJECT_ROOT = Path(__file__).parent.parent
FIGURES_DIR = PROJECT_ROOT / "figures"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_scores():
    """Load the detailed scores JSON."""
    scores_path = PROCESSED_DIR / "detailed_scores.json"
    with open(scores_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def fig1_accuracy_by_category(data):
    """Figure 1: Average accuracy scores by experiment category."""
    categories = data.get("category_summaries", {})
    if not categories:
        # Fall back to computing from individual scores
        scores = data["scores"]
        cat_scores = {}
        for exp_id, s in scores.items():
            group = s.get("experiment_group", exp_id.split('.')[0])
            if group not in cat_scores:
                cat_scores[group] = {"accuracy": [], "specificity": [], "completeness": [], "confidence_calibration": []}
            for dim in ["accuracy", "specificity", "completeness", "confidence_calibration"]:
                if dim in s:
                    cat_scores[group][dim].append(s[dim])
        categories = {}
        for group, dims in cat_scores.items():
            categories[group] = {dim: np.mean(vals) if vals else 0 for dim, vals in dims.items()}

    groups = sorted(categories.keys())
    group_labels = {
        "E1": "Direct\nDescription",
        "E2": "UI Element\nIdentification",
        "E3": "Interaction\nPatterns",
        "E4": "ASCII Art\nDrawing",
        "E5": "Interface\nComparison",
        "E6": "Specific\nFeatures",
        "E7": "Meta-\nAwareness",
    }

    dimensions = ["accuracy", "specificity", "completeness", "confidence_calibration"]
    dim_labels = ["Accuracy", "Specificity", "Completeness", "Confidence\nCalibration"]
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(groups))
    width = 0.18
    offsets = np.array([-1.5, -0.5, 0.5, 1.5]) * width

    for i, (dim, label, color) in enumerate(zip(dimensions, dim_labels, colors)):
        values = []
        for g in groups:
            cat = categories.get(g, {})
            if isinstance(cat, dict):
                val = cat.get(f"avg_{dim}", cat.get(dim, 0))
            else:
                val = 0
            values.append(val)
        bars = ax.bar(x + offsets[i], values, width, label=label, color=color, alpha=0.85, edgecolor='white', linewidth=0.5)

    ax.set_xlabel('Experiment Category')
    ax.set_ylabel('Score (0-5)')
    ax.set_title("Claude's Knowledge of Claude Code Interface by Category")
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.set_ylim(0, 5.5)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.3, label='_nolegend_')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig1_accuracy_by_category.png")
    plt.savefig(FIGURES_DIR / "fig1_accuracy_by_category.pdf")
    plt.close()
    print("Generated Figure 1: Accuracy by Category")


def fig2_hallucination_analysis(data):
    """Figure 2: Correct vs hallucinated claims analysis."""
    scores = data["scores"]

    groups = {}
    for exp_id, s in scores.items():
        group = s.get("experiment_group", exp_id.split('.')[0])
        if group not in groups:
            groups[group] = {"correct": 0, "hallucinated": 0, "total": 0}
        groups[group]["correct"] += s.get("correct_claims", 0)
        groups[group]["hallucinated"] += s.get("hallucinated_claims", 0)
        groups[group]["total"] += s.get("total_claims", 0)

    group_labels = {
        "E1": "Direct Desc.",
        "E2": "UI Elements",
        "E3": "Interaction",
        "E4": "ASCII Art",
        "E5": "Comparison",
        "E6": "Features",
        "E7": "Meta-Aware",
    }

    sorted_groups = sorted(groups.keys())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Stacked bar chart
    correct_vals = [groups[g]["correct"] for g in sorted_groups]
    halluc_vals = [groups[g]["hallucinated"] for g in sorted_groups]
    x = np.arange(len(sorted_groups))

    ax1.bar(x, correct_vals, label='Correct Claims', color='#4CAF50', alpha=0.85)
    ax1.bar(x, halluc_vals, bottom=correct_vals, label='Hallucinated Claims', color='#F44336', alpha=0.85)
    ax1.set_xlabel('Experiment Category')
    ax1.set_ylabel('Number of Claims')
    ax1.set_title('Correct vs. Hallucinated Claims by Category')
    ax1.set_xticks(x)
    ax1.set_xticklabels([group_labels.get(g, g) for g in sorted_groups], rotation=30, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Right: Hallucination rate (%)
    rates = []
    for g in sorted_groups:
        total = groups[g]["total"]
        if total > 0:
            rate = (groups[g]["hallucinated"] / total) * 100
        else:
            rate = 0
        rates.append(rate)

    bars = ax1_right = ax2.bar(x, rates, color=['#4CAF50' if r < 20 else '#FF9800' if r < 40 else '#F44336' for r in rates], alpha=0.85)
    ax2.set_xlabel('Experiment Category')
    ax2.set_ylabel('Hallucination Rate (%)')
    ax2.set_title('Hallucination Rate by Category')
    ax2.set_xticks(x)
    ax2.set_xticklabels([group_labels.get(g, g) for g in sorted_groups], rotation=30, ha='right')
    ax2.set_ylim(0, 100)
    ax2.axhline(y=20, color='green', linestyle='--', alpha=0.5, label='20% threshold')
    ax2.axhline(y=40, color='orange', linestyle='--', alpha=0.5, label='40% threshold')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig2_hallucination_analysis.png")
    plt.savefig(FIGURES_DIR / "fig2_hallucination_analysis.pdf")
    plt.close()
    print("Generated Figure 2: Hallucination Analysis")


def fig3_radar_chart(data):
    """Figure 3: Radar chart of knowledge dimensions."""
    scores = data["scores"]

    # Compute per-category averages
    cat_avgs = {}
    for exp_id, s in scores.items():
        group = s.get("experiment_group", exp_id.split('.')[0])
        if group not in cat_avgs:
            cat_avgs[group] = {d: [] for d in ["accuracy", "specificity", "completeness", "confidence_calibration"]}
        for d in ["accuracy", "specificity", "completeness", "confidence_calibration"]:
            if d in s:
                cat_avgs[group][d].append(s[d])

    dimensions = ["accuracy", "specificity", "completeness", "confidence_calibration"]
    dim_labels = ["Accuracy", "Specificity", "Completeness", "Confidence\nCalibration"]

    # Compute overall averages
    overall = {d: np.mean([v for g in cat_avgs.values() for v in g[d]]) for d in dimensions}

    # Radar chart
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Plot each category
    colors_map = {
        "E1": "#2196F3", "E2": "#4CAF50", "E3": "#FF9800",
        "E4": "#9C27B0", "E5": "#F44336", "E6": "#00BCD4", "E7": "#795548"
    }
    group_names = {
        "E1": "Direct Desc.", "E2": "UI Elements", "E3": "Interaction",
        "E4": "ASCII Art", "E5": "Comparison", "E6": "Features", "E7": "Meta-Aware"
    }

    for group in sorted(cat_avgs.keys()):
        values = [np.mean(cat_avgs[group][d]) if cat_avgs[group][d] else 0 for d in dimensions]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=1.5, label=group_names.get(group, group),
                color=colors_map.get(group, '#666'), alpha=0.7, markersize=4)

    # Plot overall average (bold)
    overall_values = [overall[d] for d in dimensions]
    overall_values += overall_values[:1]
    ax.plot(angles, overall_values, 's-', linewidth=3, label='Overall Average',
            color='black', alpha=0.9, markersize=6)
    ax.fill(angles, overall_values, alpha=0.1, color='black')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dim_labels)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.set_title("Knowledge Dimensions Across Experiment Categories", pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), framealpha=0.9)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig3_radar_chart.png")
    plt.savefig(FIGURES_DIR / "fig3_radar_chart.pdf")
    plt.close()
    print("Generated Figure 3: Radar Chart")


def fig4_heatmap(data):
    """Figure 4: Heatmap of scores per experiment."""
    scores = data["scores"]
    dimensions = ["accuracy", "specificity", "completeness", "confidence_calibration"]

    exp_ids = sorted(scores.keys(), key=lambda x: (x.split('.')[0], int(x.split('.')[1])))

    matrix = []
    labels = []
    for exp_id in exp_ids:
        s = scores[exp_id]
        row = [s.get(d, 0) for d in dimensions]
        matrix.append(row)
        labels.append(exp_id)

    matrix = np.array(matrix)

    fig, ax = plt.subplots(figsize=(8, 12))
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=5)

    ax.set_xticks(range(len(dimensions)))
    ax.set_xticklabels(["Accuracy", "Specificity", "Completeness", "Calibration"], rotation=30, ha='right')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    # Add text annotations
    for i in range(len(labels)):
        for j in range(len(dimensions)):
            text = ax.text(j, i, f"{matrix[i, j]:.1f}",
                          ha="center", va="center", color="black", fontsize=9)

    ax.set_title("Score Heatmap: All Experiments x Dimensions")
    plt.colorbar(im, ax=ax, label='Score (0-5)', shrink=0.6)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig4_heatmap.png")
    plt.savefig(FIGURES_DIR / "fig4_heatmap.pdf")
    plt.close()
    print("Generated Figure 4: Heatmap")


def fig5_overall_summary(data):
    """Figure 5: Overall summary - pie chart of claim correctness + bar of overall scores."""
    overall = data.get("overall_summary", {})
    scores = data["scores"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Pie chart of correct vs hallucinated
    total_correct = overall.get("total_correct_claims", sum(s.get("correct_claims", 0) for s in scores.values()))
    total_halluc = overall.get("total_hallucinated_claims", sum(s.get("hallucinated_claims", 0) for s in scores.values()))

    if total_correct + total_halluc > 0:
        sizes = [total_correct, total_halluc]
        labels_pie = [f'Correct\n({total_correct})', f'Hallucinated\n({total_halluc})']
        colors_pie = ['#4CAF50', '#F44336']
        explode = (0.02, 0.05)
        ax1.pie(sizes, explode=explode, labels=labels_pie, colors=colors_pie,
                autopct='%1.1f%%', shadow=False, startangle=90,
                textprops={'fontsize': 11})
        ax1.set_title(f'Overall Claim Accuracy\n(N={total_correct + total_halluc} claims)')
    else:
        ax1.text(0.5, 0.5, 'No claims data', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Overall Claim Accuracy')

    # Right: Overall dimension scores
    dimensions = ["accuracy", "specificity", "completeness", "confidence_calibration"]
    dim_labels = ["Accuracy", "Specificity", "Completeness", "Calibration"]
    overall_scores = []
    for d in dimensions:
        vals = [s.get(d, 0) for s in scores.values()]
        overall_scores.append(np.mean(vals) if vals else 0)

    bars = ax2.barh(dim_labels, overall_scores, color=['#2196F3', '#4CAF50', '#FF9800', '#9C27B0'], alpha=0.85)
    ax2.set_xlim(0, 5)
    ax2.set_xlabel('Average Score (0-5)')
    ax2.set_title('Overall Scores by Dimension')
    ax2.grid(axis='x', alpha=0.3)

    # Add value labels
    for bar, val in zip(bars, overall_scores):
        ax2.text(val + 0.1, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                ha='left', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig5_overall_summary.png")
    plt.savefig(FIGURES_DIR / "fig5_overall_summary.pdf")
    plt.close()
    print("Generated Figure 5: Overall Summary")


def fig6_confidence_vs_accuracy(data):
    """Figure 6: Scatter plot of confidence calibration vs accuracy."""
    scores = data["scores"]

    fig, ax = plt.subplots(figsize=(8, 6))

    group_colors = {
        "E1": "#2196F3", "E2": "#4CAF50", "E3": "#FF9800",
        "E4": "#9C27B0", "E5": "#F44336", "E6": "#00BCD4", "E7": "#795548"
    }
    group_names = {
        "E1": "Direct Desc.", "E2": "UI Elements", "E3": "Interaction",
        "E4": "ASCII Art", "E5": "Comparison", "E6": "Features", "E7": "Meta-Aware"
    }

    plotted_groups = set()
    for exp_id, s in scores.items():
        group = s.get("experiment_group", exp_id.split('.')[0])
        color = group_colors.get(group, '#666')
        label = group_names.get(group, group) if group not in plotted_groups else '_nolegend_'
        plotted_groups.add(group)

        ax.scatter(s.get("confidence_calibration", 0), s.get("accuracy", 0),
                  c=color, s=80, alpha=0.7, edgecolors='white', linewidth=0.5,
                  label=label)
        ax.annotate(exp_id, (s.get("confidence_calibration", 0), s.get("accuracy", 0)),
                   textcoords="offset points", xytext=(5, 5), fontsize=7, alpha=0.7)

    # Add diagonal line (perfect calibration)
    ax.plot([0, 5], [0, 5], 'k--', alpha=0.3, label='Perfect calibration')

    ax.set_xlabel('Confidence Calibration Score')
    ax.set_ylabel('Accuracy Score')
    ax.set_title('Confidence Calibration vs. Actual Accuracy')
    ax.set_xlim(-0.2, 5.2)
    ax.set_ylim(-0.2, 5.2)
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig6_confidence_vs_accuracy.png")
    plt.savefig(FIGURES_DIR / "fig6_confidence_vs_accuracy.pdf")
    plt.close()
    print("Generated Figure 6: Confidence vs Accuracy")


def main():
    """Generate all figures."""
    print("Loading scores...")
    data = load_scores()
    print(f"Loaded scores for {len(data.get('scores', {}))} experiments")

    print("\nGenerating figures...")
    fig1_accuracy_by_category(data)
    fig2_hallucination_analysis(data)
    fig3_radar_chart(data)
    fig4_heatmap(data)
    fig5_overall_summary(data)
    fig6_confidence_vs_accuracy(data)

    print(f"\nAll figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    main()

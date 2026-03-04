"""
Generate publication-quality figures with KOREAN labels for the research report.
Uses empirical ground truth v2 scores.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from pathlib import Path

# Register Korean font
font_path = 'C:/Windows/Fonts/malgun.ttf'
font_prop = fm.FontProperties(fname=font_path)
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# Publication-quality defaults
plt.rcParams.update({
    'font.size': 11,
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
    # Try v2 first, fall back to v1
    v2_path = PROCESSED_DIR / "detailed_scores_v2.json"
    v1_path = PROCESSED_DIR / "detailed_scores.json"
    path = v2_path if v2_path.exists() else v1_path
    print(f"Loading scores from: {path.name}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def fig1_accuracy_by_category(data):
    """Figure 1: 실험 범주별 평균 점수."""
    scores = data["scores"]

    cat_scores = {}
    for exp_id, s in scores.items():
        group = s.get("experiment_group", exp_id.split('.')[0])
        if group not in cat_scores:
            cat_scores[group] = {"accuracy": [], "specificity": [], "completeness": [], "confidence_calibration": []}
        for dim in ["accuracy", "specificity", "completeness", "confidence_calibration"]:
            if dim in s:
                cat_scores[group][dim].append(s[dim])

    groups = sorted(cat_scores.keys())
    group_labels = {
        "E1": "직접\n서술",
        "E2": "UI 요소\n식별",
        "E3": "인터랙션\n패턴",
        "E4": "ASCII\n아트",
        "E5": "인터페이스\n비교",
        "E6": "특정\n기능",
        "E7": "메타\n인식",
    }

    dimensions = ["accuracy", "specificity", "completeness", "confidence_calibration"]
    dim_labels = ["정확도", "구체성", "완전성", "신뢰도 보정"]
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(groups))
    width = 0.18
    offsets = np.array([-1.5, -0.5, 0.5, 1.5]) * width

    for i, (dim, label, color) in enumerate(zip(dimensions, dim_labels, colors)):
        values = [np.mean(cat_scores[g][dim]) if cat_scores[g][dim] else 0 for g in groups]
        ax.bar(x + offsets[i], values, width, label=label, color=color, alpha=0.85, edgecolor='white', linewidth=0.5)

    ax.set_xlabel('실험 범주')
    ax.set_ylabel('점수 (0-5)')
    ax.set_title("Claude의 Claude Code 인터페이스 지식 (범주별)")
    ax.set_xticks(x)
    ax.set_xticklabels([group_labels.get(g, g) for g in groups])
    ax.set_ylim(0, 5.5)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig1_accuracy_by_category.png")
    plt.savefig(FIGURES_DIR / "fig1_accuracy_by_category.pdf")
    plt.close()
    print("  Figure 1 생성 완료")


def fig2_hallucination_analysis(data):
    """Figure 2: 환각 분석."""
    scores = data["scores"]

    groups = {}
    for exp_id, s in scores.items():
        group = s.get("experiment_group", exp_id.split('.')[0])
        if group not in groups:
            groups[group] = {"correct": 0, "hallucinated": 0}
        groups[group]["correct"] += s.get("correct_claims", 0)
        groups[group]["hallucinated"] += s.get("hallucinated_claims", 0)

    group_labels = {
        "E1": "직접 서술", "E2": "UI 요소", "E3": "인터랙션",
        "E4": "ASCII 아트", "E5": "비교", "E6": "특정 기능", "E7": "메타 인식",
    }

    sorted_groups = sorted(groups.keys())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    correct_vals = [groups[g]["correct"] for g in sorted_groups]
    halluc_vals = [groups[g]["hallucinated"] for g in sorted_groups]
    x = np.arange(len(sorted_groups))

    ax1.bar(x, correct_vals, label='정확한 주장', color='#4CAF50', alpha=0.85)
    ax1.bar(x, halluc_vals, bottom=correct_vals, label='환각된 주장', color='#F44336', alpha=0.85)
    ax1.set_xlabel('실험 범주')
    ax1.set_ylabel('주장 수')
    ax1.set_title('범주별 정확 vs 환각 주장')
    ax1.set_xticks(x)
    ax1.set_xticklabels([group_labels.get(g, g) for g in sorted_groups], rotation=30, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    rates = []
    for g in sorted_groups:
        total = groups[g]["correct"] + groups[g]["hallucinated"]
        rates.append((groups[g]["hallucinated"] / total * 100) if total > 0 else 0)

    ax2.bar(x, rates, color=['#4CAF50' if r < 20 else '#FF9800' if r < 40 else '#F44336' for r in rates], alpha=0.85)
    ax2.set_xlabel('실험 범주')
    ax2.set_ylabel('환각 비율 (%)')
    ax2.set_title('범주별 환각 비율')
    ax2.set_xticks(x)
    ax2.set_xticklabels([group_labels.get(g, g) for g in sorted_groups], rotation=30, ha='right')
    ax2.set_ylim(0, 100)
    ax2.axhline(y=20, color='green', linestyle='--', alpha=0.5, label='20% 기준선')
    ax2.axhline(y=40, color='orange', linestyle='--', alpha=0.5, label='40% 기준선')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig2_hallucination_analysis.png")
    plt.savefig(FIGURES_DIR / "fig2_hallucination_analysis.pdf")
    plt.close()
    print("  Figure 2 생성 완료")


def fig3_radar_chart(data):
    """Figure 3: 지식 차원 레이더 차트."""
    scores = data["scores"]

    cat_avgs = {}
    for exp_id, s in scores.items():
        group = s.get("experiment_group", exp_id.split('.')[0])
        if group not in cat_avgs:
            cat_avgs[group] = {d: [] for d in ["accuracy", "specificity", "completeness", "confidence_calibration"]}
        for d in ["accuracy", "specificity", "completeness", "confidence_calibration"]:
            if d in s:
                cat_avgs[group][d].append(s[d])

    dimensions = ["accuracy", "specificity", "completeness", "confidence_calibration"]
    dim_labels = ["정확도", "구체성", "완전성", "신뢰도\n보정"]
    overall = {d: np.mean([v for g in cat_avgs.values() for v in g[d]]) for d in dimensions}

    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    colors_map = {
        "E1": "#2196F3", "E2": "#4CAF50", "E3": "#FF9800",
        "E4": "#9C27B0", "E5": "#F44336", "E6": "#00BCD4", "E7": "#795548"
    }
    group_names = {
        "E1": "직접 서술", "E2": "UI 요소", "E3": "인터랙션",
        "E4": "ASCII 아트", "E5": "비교", "E6": "특정 기능", "E7": "메타 인식"
    }

    for group in sorted(cat_avgs.keys()):
        values = [np.mean(cat_avgs[group][d]) if cat_avgs[group][d] else 0 for d in dimensions]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=1.5, label=group_names.get(group, group),
                color=colors_map.get(group, '#666'), alpha=0.7, markersize=4)

    overall_values = [overall[d] for d in dimensions]
    overall_values += overall_values[:1]
    ax.plot(angles, overall_values, 's-', linewidth=3, label='전체 평균',
            color='black', alpha=0.9, markersize=6)
    ax.fill(angles, overall_values, alpha=0.1, color='black')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dim_labels)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_title("실험 범주별 지식 차원", pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), framealpha=0.9)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig3_radar_chart.png")
    plt.savefig(FIGURES_DIR / "fig3_radar_chart.pdf")
    plt.close()
    print("  Figure 3 생성 완료")


def fig4_heatmap(data):
    """Figure 4: 점수 히트맵."""
    scores = data["scores"]
    dimensions = ["accuracy", "specificity", "completeness", "confidence_calibration"]

    exp_ids = sorted(scores.keys(), key=lambda x: (x.split('.')[0], int(x.split('.')[1])))

    matrix = []
    labels = []
    for exp_id in exp_ids:
        s = scores[exp_id]
        matrix.append([s.get(d, 0) for d in dimensions])
        labels.append(exp_id)

    matrix = np.array(matrix)

    fig, ax = plt.subplots(figsize=(8, 12))
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=5)

    ax.set_xticks(range(len(dimensions)))
    ax.set_xticklabels(["정확도", "구체성", "완전성", "보정"], rotation=30, ha='right')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    for i in range(len(labels)):
        for j in range(len(dimensions)):
            ax.text(j, i, f"{matrix[i, j]:.1f}", ha="center", va="center", color="black", fontsize=9)

    ax.set_title("전체 실험 점수 히트맵")
    plt.colorbar(im, ax=ax, label='점수 (0-5)', shrink=0.6)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig4_heatmap.png")
    plt.savefig(FIGURES_DIR / "fig4_heatmap.pdf")
    plt.close()
    print("  Figure 4 생성 완료")


def fig5_overall_summary(data):
    """Figure 5: 전체 요약."""
    scores = data["scores"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    total_correct = sum(s.get("correct_claims", 0) for s in scores.values())
    total_halluc = sum(s.get("hallucinated_claims", 0) for s in scores.values())

    if total_correct + total_halluc > 0:
        sizes = [total_correct, total_halluc]
        labels_pie = [f'정확\n({total_correct}개)', f'환각\n({total_halluc}개)']
        colors_pie = ['#4CAF50', '#F44336']
        ax1.pie(sizes, explode=(0.02, 0.05), labels=labels_pie, colors=colors_pie,
                autopct='%1.1f%%', shadow=False, startangle=90, textprops={'fontsize': 11})
        ax1.set_title(f'전체 주장 정확도\n(N={total_correct + total_halluc}개 주장)')

    dimensions = ["accuracy", "specificity", "completeness", "confidence_calibration"]
    dim_labels = ["정확도", "구체성", "완전성", "신뢰도 보정"]
    overall_scores = [np.mean([s.get(d, 0) for s in scores.values()]) for d in dimensions]

    bars = ax2.barh(dim_labels, overall_scores, color=['#2196F3', '#4CAF50', '#FF9800', '#9C27B0'], alpha=0.85)
    ax2.set_xlim(0, 5)
    ax2.set_xlabel('평균 점수 (0-5)')
    ax2.set_title('차원별 전체 점수')
    ax2.grid(axis='x', alpha=0.3)

    for bar, val in zip(bars, overall_scores):
        ax2.text(val + 0.1, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                ha='left', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig5_overall_summary.png")
    plt.savefig(FIGURES_DIR / "fig5_overall_summary.pdf")
    plt.close()
    print("  Figure 5 생성 완료")


def fig6_confidence_vs_accuracy(data):
    """Figure 6: 신뢰도 보정 vs 정확도."""
    scores = data["scores"]

    fig, ax = plt.subplots(figsize=(8, 6))

    group_colors = {
        "E1": "#2196F3", "E2": "#4CAF50", "E3": "#FF9800",
        "E4": "#9C27B0", "E5": "#F44336", "E6": "#00BCD4", "E7": "#795548"
    }
    group_names = {
        "E1": "직접 서술", "E2": "UI 요소", "E3": "인터랙션",
        "E4": "ASCII 아트", "E5": "비교", "E6": "특정 기능", "E7": "메타 인식"
    }

    plotted_groups = set()
    for exp_id, s in scores.items():
        group = s.get("experiment_group", exp_id.split('.')[0])
        color = group_colors.get(group, '#666')
        label = group_names.get(group, group) if group not in plotted_groups else '_nolegend_'
        plotted_groups.add(group)
        ax.scatter(s.get("confidence_calibration", 0), s.get("accuracy", 0),
                  c=color, s=80, alpha=0.7, edgecolors='white', linewidth=0.5, label=label)
        ax.annotate(exp_id, (s.get("confidence_calibration", 0), s.get("accuracy", 0)),
                   textcoords="offset points", xytext=(5, 5), fontsize=7, alpha=0.7)

    ax.plot([0, 5], [0, 5], 'k--', alpha=0.3, label='완벽한 보정')
    ax.set_xlabel('신뢰도 보정 점수')
    ax.set_ylabel('정확도 점수')
    ax.set_title('신뢰도 보정 vs 실제 정확도')
    ax.set_xlim(-0.2, 5.2)
    ax.set_ylim(-0.2, 5.2)
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig6_confidence_vs_accuracy.png")
    plt.savefig(FIGURES_DIR / "fig6_confidence_vs_accuracy.pdf")
    plt.close()
    print("  Figure 6 생성 완료")


def main():
    print("점수 데이터 로딩...")
    data = load_scores()
    print(f"{len(data.get('scores', {}))}개 실험 점수 로드됨")

    print("\n그래프 생성 중 (한국어 라벨)...")
    fig1_accuracy_by_category(data)
    fig2_hallucination_analysis(data)
    fig3_radar_chart(data)
    fig4_heatmap(data)
    fig5_overall_summary(data)
    fig6_confidence_vs_accuracy(data)

    print(f"\n전체 그래프가 {FIGURES_DIR}/ 에 저장되었습니다")


if __name__ == "__main__":
    main()

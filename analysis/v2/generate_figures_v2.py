"""
Generate v2 experiment figures.
10 figures covering domain x type accuracy, calibration, and comparisons.
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from collections import defaultdict

# Korean font
font_path = 'C:/Windows/Fonts/malgun.ttf'
if Path(font_path).exists():
    font_prop = fm.FontProperties(fname=font_path)
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCORES_PATH = PROJECT_ROOT / "data" / "processed" / "v2" / "scores_v2.json"
SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "v2" / "summary_v2.json"
FIGURES_DIR = PROJECT_ROOT / "figures" / "v2"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Domain labels
DOMAIN_LABELS = {
    "D1": "시작 화면",
    "D2": "입력 영역",
    "D3": "출력 표시",
    "D4": "권한 대화상자",
    "D5": "상태 표시줄",
    "D6": "네비게이션",
    "D7": "테마/색상",
    "D8": "Diff/편집",
    "D9": "오류 상태",
    "D10": "부정 공간(통제)",
}

TYPE_LABELS = {
    "T1": "자유 회상",
    "T2": "객관식",
    "T3": "참/거짓",
    "T4": "공간 추론",
    "T5": "정확한 세부사항",
}


def load_data():
    with open(SCORES_PATH, 'r', encoding='utf-8') as f:
        scores = json.load(f)
    with open(SUMMARY_PATH, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    return scores, summary


def fig1_domain_accuracy(summary):
    """Figure 1: Objective accuracy by domain (bar chart)."""
    fig, ax = plt.subplots(figsize=(12, 6))

    domains = sorted(summary["by_domain"].keys())
    obj_acc = []
    colors = []
    for d in domains:
        s = summary["by_domain"][d]
        acc = s["objective_accuracy"] * 100 if s["objective_n"] > 0 else 0
        obj_acc.append(acc)
        if acc >= 80:
            colors.append('#2ecc71')
        elif acc >= 50:
            colors.append('#f39c12')
        else:
            colors.append('#e74c3c')

    x = np.arange(len(domains))
    bars = ax.bar(x, obj_acc, color=colors, edgecolor='white', linewidth=0.5)

    # Add value labels
    for bar, val in zip(bars, obj_acc):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{val:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels([DOMAIN_LABELS.get(d, d) for d in domains], rotation=45, ha='right')
    ax.set_ylabel('객관식 정확도 (%)')
    ax.set_title('도메인별 객관식 정확도 (강제 선택 + 참/거짓)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='찬스 수준 (T/F)')
    ax.axhline(y=25, color='gray', linestyle=':', alpha=0.3, label='찬스 수준 (4지선다)')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig1_domain_accuracy.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / 'fig1_domain_accuracy.pdf', bbox_inches='tight')
    plt.close()
    print("Fig 1: Domain accuracy saved")


def fig2_heatmap(scores):
    """Figure 2: Domain x Type accuracy heatmap."""
    domains = sorted(set(s["domain"] for s in scores.values()))
    types = sorted(set(s["cognitive_type"] for s in scores.values()))

    # Build matrix
    matrix = np.full((len(domains), len(types)), np.nan)
    counts = np.zeros((len(domains), len(types)), dtype=int)

    for pid, pdata in scores.items():
        di = domains.index(pdata["domain"])
        ti = types.index(pdata["cognitive_type"])
        for trial in pdata["trials"]:
            counts[di, ti] += 1
            pt = trial.get("prompt_type", "")
            if pt in ("forced_choice", "true_false"):
                val = 1.0 if trial.get("correct", False) else 0.0
            else:
                val = trial.get("accuracy", 0.0)

            if np.isnan(matrix[di, ti]):
                matrix[di, ti] = val
            else:
                matrix[di, ti] = (matrix[di, ti] + val) / 2

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix * 100, cmap='RdYlGn', vmin=0, vmax=100, aspect='auto')

    # Add text annotations
    for i in range(len(domains)):
        for j in range(len(types)):
            val = matrix[i, j]
            if not np.isnan(val):
                text = f'{val*100:.0f}%'
                color = 'white' if val < 0.4 or val > 0.8 else 'black'
                ax.text(j, i, text, ha='center', va='center', fontsize=10, color=color, fontweight='bold')
            else:
                ax.text(j, i, '-', ha='center', va='center', fontsize=10, color='gray')

    ax.set_xticks(np.arange(len(types)))
    ax.set_xticklabels([TYPE_LABELS.get(t, t) for t in types])
    ax.set_yticks(np.arange(len(domains)))
    ax.set_yticklabels([DOMAIN_LABELS.get(d, d) for d in domains])
    ax.set_title('도메인 × 인지 유형 정확도 히트맵', fontsize=14, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax, label='정확도 (%)')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig2_heatmap.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / 'fig2_heatmap.pdf', bbox_inches='tight')
    plt.close()
    print("Fig 2: Heatmap saved")


def fig3_confidence_calibration(scores):
    """Figure 3: Confidence vs accuracy calibration curve."""
    bins = np.arange(0, 1.1, 0.1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_correct = defaultdict(list)

    for pid, pdata in scores.items():
        for trial in pdata["trials"]:
            pt = trial.get("prompt_type", "")
            if pt in ("forced_choice", "true_false"):
                conf = trial.get("confidence", 0.5)
                correct = 1.0 if trial.get("correct", False) else 0.0
                bin_idx = min(int(conf * 10), 9)
                bin_correct[bin_idx].append(correct)

    fig, ax = plt.subplots(figsize=(8, 8))

    actual_acc = []
    for i in range(10):
        vals = bin_correct.get(i, [])
        if vals:
            actual_acc.append(np.mean(vals))
        else:
            actual_acc.append(np.nan)

    valid = ~np.isnan(actual_acc)
    centers_valid = bin_centers[valid]
    acc_valid = np.array(actual_acc)[valid]

    # Perfect calibration line
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='완벽한 보정')

    # Actual calibration
    ax.plot(centers_valid, acc_valid, 'o-', color='#3498db', markersize=8, linewidth=2, label='실제 보정')

    # Fill between
    ax.fill_between(centers_valid, centers_valid, acc_valid, alpha=0.15, color='#3498db')

    ax.set_xlabel('모델 신뢰도', fontsize=12)
    ax.set_ylabel('실제 정확도', fontsize=12)
    ax.set_title('신뢰도 보정 곡선 (객관식 문항)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig3_calibration.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / 'fig3_calibration.pdf', bbox_inches='tight')
    plt.close()
    print("Fig 3: Calibration curve saved")


def fig4_cognitive_type_comparison(summary):
    """Figure 4: Accuracy by cognitive type."""
    fig, ax = plt.subplots(figsize=(10, 6))

    types = sorted(summary["by_cognitive_type"].keys())
    obj_acc = []
    obj_n = []
    for t in types:
        s = summary["by_cognitive_type"][t]
        obj_acc.append(s["objective_accuracy"] * 100 if s["objective_n"] > 0 else None)
        obj_n.append(s["objective_n"])

    x = np.arange(len(types))
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

    for i, (acc, n) in enumerate(zip(obj_acc, obj_n)):
        if acc is not None:
            bar = ax.bar(x[i], acc, color=colors[i], edgecolor='white', width=0.6)
            ax.text(x[i], acc + 1, f'{acc:.0f}%\n(n={n})', ha='center', va='bottom', fontsize=10)
        else:
            ax.bar(x[i], 0, color='lightgray', edgecolor='white', width=0.6)
            ax.text(x[i], 2, f'해당 없음\n(주관식)', ha='center', va='bottom', fontsize=9, color='gray')

    ax.set_xticks(x)
    ax.set_xticklabels([TYPE_LABELS.get(t, t) for t in types])
    ax.set_ylabel('객관식 정확도 (%)')
    ax.set_title('인지 유형별 정확도', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='T/F 찬스 수준')
    ax.axhline(y=25, color='gray', linestyle=':', alpha=0.3, label='4지선다 찬스 수준')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig4_type_accuracy.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / 'fig4_type_accuracy.pdf', bbox_inches='tight')
    plt.close()
    print("Fig 4: Cognitive type accuracy saved")


def fig5_confidence_distribution(scores):
    """Figure 5: Confidence distribution for correct vs incorrect."""
    correct_conf = []
    incorrect_conf = []

    for pid, pdata in scores.items():
        for trial in pdata["trials"]:
            pt = trial.get("prompt_type", "")
            if pt in ("forced_choice", "true_false"):
                conf = trial.get("confidence", 0.5)
                if trial.get("correct", False):
                    correct_conf.append(conf)
                else:
                    incorrect_conf.append(conf)

    fig, ax = plt.subplots(figsize=(10, 6))
    bins = np.arange(0, 1.05, 0.1)

    ax.hist(correct_conf, bins=bins, alpha=0.7, color='#2ecc71', edgecolor='white',
            label=f'정답 (n={len(correct_conf)})')
    ax.hist(incorrect_conf, bins=bins, alpha=0.7, color='#e74c3c', edgecolor='white',
            label=f'오답 (n={len(incorrect_conf)})')

    if correct_conf:
        ax.axvline(np.mean(correct_conf), color='#27ae60', linestyle='--',
                    label=f'정답 평균={np.mean(correct_conf):.2f}')
    if incorrect_conf:
        ax.axvline(np.mean(incorrect_conf), color='#c0392b', linestyle='--',
                    label=f'오답 평균={np.mean(incorrect_conf):.2f}')

    ax.set_xlabel('모델 신뢰도')
    ax.set_ylabel('빈도')
    ax.set_title('정답 vs 오답의 신뢰도 분포', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig5_confidence_dist.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / 'fig5_confidence_dist.pdf', bbox_inches='tight')
    plt.close()
    print("Fig 5: Confidence distribution saved")


def fig6_overall_summary(summary):
    """Figure 6: Overall summary dashboard."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    o = summary["overall"]

    # Panel 1: Objective accuracy pie
    ax = axes[0]
    correct = int(o["objective_accuracy"] * o["objective_n"])
    wrong = o["objective_n"] - correct
    ax.pie([correct, wrong], labels=[f'정답\n{correct}', f'오답\n{wrong}'],
           colors=['#2ecc71', '#e74c3c'], autopct='%1.0f%%', startangle=90,
           textprops={'fontsize': 12})
    ax.set_title(f'객관식 정확도\n(n={o["objective_n"]})', fontsize=13, fontweight='bold')

    # Panel 2: Claims breakdown
    ax = axes[1]
    sizes = [o["claims_correct"], o["claims_incorrect"], o["claims_unverifiable"]]
    labels = [f'정확\n{sizes[0]}', f'부정확\n{sizes[1]}', f'미검증\n{sizes[2]}']
    colors_pie = ['#2ecc71', '#e74c3c', '#95a5a6']
    # Filter out zeros
    non_zero = [(s, l, c) for s, l, c in zip(sizes, labels, colors_pie) if s > 0]
    if non_zero:
        sz, lb, cl = zip(*non_zero)
        ax.pie(sz, labels=lb, colors=cl, autopct='%1.0f%%', startangle=90,
               textprops={'fontsize': 12})
    ax.set_title(f'주장 분류\n(n={o["claims_total"]})', fontsize=13, fontweight='bold')

    # Panel 3: Key metrics
    ax = axes[2]
    ax.axis('off')
    metrics = [
        ('객관식 정확도', f'{o["objective_accuracy"]*100:.1f}%'),
        ('평균 신뢰도', f'{o["avg_confidence"]:.3f}'),
        ('보정 오차', f'{o["avg_calibration_error"]:.3f}'),
        ('총 주장 수', f'{o["claims_total"]}'),
        ('검증 정확도', f'{o["claim_accuracy"]*100:.1f}%'),
    ]
    for i, (label, value) in enumerate(metrics):
        y = 0.85 - i * 0.17
        ax.text(0.1, y, label, fontsize=13, va='center', transform=ax.transAxes)
        ax.text(0.9, y, value, fontsize=15, va='center', ha='right',
                fontweight='bold', transform=ax.transAxes,
                color='#2ecc71' if 'accuracy' in label.lower() else '#333')

    ax.set_title('핵심 지표', fontsize=13, fontweight='bold')

    plt.suptitle('"Claude는 자신의 Harness가 어떻게 생겼는지 아는가?" — v2 결과 요약',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig6_overall_summary.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / 'fig6_overall_summary.pdf', bbox_inches='tight')
    plt.close()
    print("Fig 6: Overall summary saved")


def fig7_wrong_answers_detail(scores):
    """Figure 7: Detailed wrong answers analysis."""
    wrong_items = []
    for pid, pdata in scores.items():
        for trial in pdata["trials"]:
            pt = trial.get("prompt_type", "")
            if pt in ("forced_choice", "true_false") and not trial.get("correct", True):
                wrong_items.append({
                    "prompt_id": pid,
                    "domain": pdata["domain"],
                    "answer": trial.get("answer_given", "?"),
                    "expected": trial.get("correct_answer", "?"),
                    "confidence": trial.get("confidence", 0),
                })

    if not wrong_items:
        print("Fig 7: No wrong answers to plot")
        return

    fig, ax = plt.subplots(figsize=(10, max(4, len(wrong_items) * 0.8)))

    y_pos = np.arange(len(wrong_items))
    confs = [w["confidence"] for w in wrong_items]
    labels = [f'{w["prompt_id"]} ({DOMAIN_LABELS.get(w["domain"], w["domain"])})' for w in wrong_items]
    details = [f'답: {w["answer"][:15]} → 정답: {w["expected"][:15]}' for w in wrong_items]

    bars = ax.barh(y_pos, confs, color='#e74c3c', alpha=0.8, edgecolor='white')
    for i, (bar, detail) in enumerate(zip(bars, details)):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                detail, va='center', fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel('모델 신뢰도')
    ax.set_title('오답 분석: 신뢰도와 상세 내용', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1.2)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig7_wrong_answers.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / 'fig7_wrong_answers.pdf', bbox_inches='tight')
    plt.close()
    print("Fig 7: Wrong answers detail saved")


def fig8_radar_chart(summary):
    """Figure 8: Radar chart of domain performance."""
    domains = sorted(summary["by_domain"].keys())
    N = len(domains)

    # Get accuracy for each domain (combining objective + claim)
    values = []
    for d in domains:
        s = summary["by_domain"][d]
        if s["objective_n"] > 0:
            values.append(s["objective_accuracy"])
        elif s["claims_total"] > 0:
            values.append(s["claim_accuracy"])
        else:
            values.append(0)

    # Close the radar
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_closed = values + [values[0]]
    angles_closed = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles_closed, values_closed, alpha=0.25, color='#3498db')
    ax.plot(angles_closed, values_closed, 'o-', color='#3498db', linewidth=2, markersize=6)

    ax.set_xticks(angles)
    ax.set_xticklabels([DOMAIN_LABELS.get(d, d) for d in domains], fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=8)
    ax.set_title('도메인별 성능 레이더 차트', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig8_radar.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / 'fig8_radar.pdf', bbox_inches='tight')
    plt.close()
    print("Fig 8: Radar chart saved")


def main():
    print("=== Generating v2 Figures ===")
    scores, summary = load_data()

    fig1_domain_accuracy(summary)
    fig2_heatmap(scores)
    fig3_confidence_calibration(scores)
    fig4_cognitive_type_comparison(summary)
    fig5_confidence_distribution(scores)
    fig6_overall_summary(summary)
    fig7_wrong_answers_detail(scores)
    fig8_radar_chart(summary)

    print(f"\nAll figures saved to {FIGURES_DIR}")


if __name__ == "__main__":
    main()

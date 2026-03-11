"""Generate figures for H1 analysis: SP+ vs SP-."""
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

# Korean font
font_path = 'C:/Windows/Fonts/malgun.ttf'
if Path(font_path).exists():
    prop = fm.FontProperties(fname=font_path)
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
H1_PATH = PROJECT_ROOT / "data" / "processed" / "v2" / "h1_analysis.json"
FIG_DIR = PROJECT_ROOT / "figures" / "v2"
FIG_DIR.mkdir(parents=True, exist_ok=True)

with open(H1_PATH, 'r', encoding='utf-8') as f:
    h1 = json.load(f)

obj = h1["objective_results"]
details = h1["details"]


def fig_h1_main():
    """Main H1 figure: SP+ vs SP- accuracy and confidence side by side."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Accuracy
    labels = ['SP+\n(System Prompt)', 'SP-\n(External Knowledge)']
    accs = [obj["sp_plus"]["accuracy"] * 100, obj["sp_minus"]["accuracy"] * 100]
    ns = [obj["sp_plus"]["total"], obj["sp_minus"]["total"]]
    colors = ['#2ecc71', '#e74c3c']

    bars = ax1.bar(labels, accs, color=colors, edgecolor='white', width=0.5)
    for bar, acc, n in zip(bars, accs, ns):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                 f'{acc:.1f}%\n(n={n})', ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax1.axhline(50, color='gray', ls='--', alpha=0.5, label='T/F chance (50%)')
    ax1.axhline(25, color='gray', ls=':', alpha=0.3, label='MC chance (25%)')
    ax1.set_ylim(0, 115)
    ax1.set_ylabel('Objective Accuracy (%)', fontsize=12)
    ax1.set_title('(a) Accuracy by Information Source', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', alpha=0.2)

    # Panel 2: Confidence
    sp_plus_conf = [d["confidence"] for d in details if d["sp"] == "SP+" and d["confidence"] is not None]
    sp_minus_correct_conf = [d["confidence"] for d in details if d["sp"] == "SP-" and d["correct"] and d["confidence"] is not None]
    sp_minus_wrong_conf = [d["confidence"] for d in details if d["sp"] == "SP-" and not d["correct"] and d["confidence"] is not None]

    positions = [0, 1, 2]
    bp_data = [sp_plus_conf, sp_minus_correct_conf, sp_minus_wrong_conf]
    bp_labels = ['SP+ Correct', 'SP- Correct', 'SP- Wrong']
    bp_colors = ['#2ecc71', '#3498db', '#e74c3c']

    bp = ax2.boxplot(bp_data, positions=positions, widths=0.4, patch_artist=True,
                     showmeans=True, meanprops=dict(marker='D', markerfacecolor='white', markersize=6))
    for patch, color in zip(bp['boxes'], bp_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Scatter individual points
    for i, (data, color) in enumerate(zip(bp_data, bp_colors)):
        jitter = np.random.normal(0, 0.05, len(data))
        ax2.scatter([i] * len(data) + jitter, data, color=color, alpha=0.6, s=30, zorder=5)

    ax2.set_xticks(positions)
    ax2.set_xticklabels(bp_labels, fontsize=10)
    ax2.set_ylabel('Stated Confidence', fontsize=12)
    ax2.set_title('(b) Confidence Distribution\n(p=0.0013, Mann-Whitney U)', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 1.05)
    ax2.grid(axis='y', alpha=0.2)

    plt.suptitle('H1: System Prompt Knowledge vs External Knowledge',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig_h1_main.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig_h1_main.pdf', bbox_inches='tight')
    plt.close()
    print("fig_h1_main saved")


def fig_h1_domain_split():
    """Domain-level breakdown showing SP+ vs SP- items per domain."""
    fig, ax = plt.subplots(figsize=(12, 6))

    domains = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10']
    domain_names = ['Startup', 'Input', 'Output', 'Permission', 'Status',
                    'Navigation', 'Theming', 'Diff', 'Error', 'Negative']

    sp_plus_acc = []
    sp_minus_acc = []

    from collections import defaultdict
    dom_data = defaultdict(lambda: {"sp+_c": 0, "sp+_t": 0, "sp-_c": 0, "sp-_t": 0})
    for d in details:
        dom = d["domain"]
        if d["sp"] == "SP+":
            dom_data[dom]["sp+_c"] += int(d["correct"])
            dom_data[dom]["sp+_t"] += 1
        else:
            dom_data[dom]["sp-_c"] += int(d["correct"])
            dom_data[dom]["sp-_t"] += 1

    for dom in domains:
        s = dom_data[dom]
        sp_plus_acc.append(s["sp+_c"] / s["sp+_t"] * 100 if s["sp+_t"] > 0 else None)
        sp_minus_acc.append(s["sp-_c"] / s["sp-_t"] * 100 if s["sp-_t"] > 0 else None)

    x = np.arange(len(domains))
    w = 0.35

    # Plot SP+ bars
    sp_plus_vals = [v if v is not None else 0 for v in sp_plus_acc]
    sp_minus_vals = [v if v is not None else 0 for v in sp_minus_acc]
    sp_plus_mask = [v is not None for v in sp_plus_acc]
    sp_minus_mask = [v is not None for v in sp_minus_acc]

    bars1 = ax.bar(x[sp_plus_mask] - w/2, [sp_plus_vals[i] for i in range(len(domains)) if sp_plus_mask[i]],
                   w, color='#2ecc71', label='SP+ (System Prompt)', edgecolor='white')
    bars2 = ax.bar(x[sp_minus_mask] + w/2, [sp_minus_vals[i] for i in range(len(domains)) if sp_minus_mask[i]],
                   w, color='#e74c3c', label='SP- (External)', edgecolor='white', alpha=0.8)

    # Labels
    for i, (sp, sm) in enumerate(zip(sp_plus_acc, sp_minus_acc)):
        if sp is not None:
            ax.text(i - w/2, sp + 1.5, f'{sp:.0f}%', ha='center', fontsize=8, fontweight='bold', color='#27ae60')
        if sm is not None:
            ax.text(i + w/2, sm + 1.5, f'{sm:.0f}%', ha='center', fontsize=8, fontweight='bold', color='#c0392b')

    ax.set_xticks(x)
    ax.set_xticklabels([f'{d}\n{n}' for d, n in zip(domains, domain_names)], fontsize=9)
    ax.set_ylabel('Objective Accuracy (%)')
    ax.set_title('Domain-Level Accuracy: SP+ vs SP-', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 115)
    ax.axhline(50, color='gray', ls='--', alpha=0.4)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.2)

    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig_h1_domain.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig_h1_domain.pdf', bbox_inches='tight')
    plt.close()
    print("fig_h1_domain saved")


def fig_h1_wrong_detail():
    """Wrong answers analysis with SP label and confidence."""
    wrong = [d for d in details if not d["correct"]]
    if not wrong:
        print("No wrong answers")
        return

    fig, ax = plt.subplots(figsize=(10, 4))

    labels = []
    confs = []
    explanations = {
        "P06": "Personalized greeting\nexists (missed feature)",
        "P13": "All multiline methods\nwork (partial knowledge)",
        "P19": "3 output styles exist\n(missed feature, high conf!)",
        "P33": "Vim mode exists\n(missed feature)",
        "P36": "Ctrl+G not Ctrl+E\n(wrong shortcut)",
    }

    for d in wrong:
        pid = d["prompt_id"]
        labels.append(f'{pid}\n{explanations.get(pid, "")}')
        confs.append(d["confidence"])

    y_pos = np.arange(len(wrong))
    colors = ['#e74c3c' if c > 0.6 else '#f39c12' if c > 0.4 else '#95a5a6' for c in confs]
    bars = ax.barh(y_pos, confs, color=colors, edgecolor='white', height=0.6)

    for i, (bar, c) in enumerate(zip(bars, confs)):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f'{c:.2f}', va='center', fontsize=11, fontweight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Stated Confidence', fontsize=12)
    ax.set_title('All 5 Wrong Answers Are SP- (External Knowledge Required)',
                 fontsize=13, fontweight='bold')
    ax.set_xlim(0, 1.1)
    ax.axvline(0.5, color='gray', ls='--', alpha=0.4, label='Neutral confidence')
    ax.legend()
    ax.grid(axis='x', alpha=0.2)
    ax.invert_yaxis()

    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig_h1_wrong.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig_h1_wrong.pdf', bbox_inches='tight')
    plt.close()
    print("fig_h1_wrong saved")


def fig_h1_summary():
    """Summary infographic."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')

    # Title
    ax.text(0.5, 0.95, 'H1: System Prompt is the Primary Driver of Harness Knowledge',
            ha='center', va='top', fontsize=16, fontweight='bold', transform=ax.transAxes)

    # Two boxes
    # SP+ box
    ax.add_patch(plt.Rectangle((0.02, 0.3), 0.44, 0.55, fill=True,
                               facecolor='#eafaf1', edgecolor='#27ae60', linewidth=2,
                               transform=ax.transAxes))
    ax.text(0.24, 0.80, 'SP+ (In System Prompt)', ha='center', fontsize=13,
            fontweight='bold', color='#27ae60', transform=ax.transAxes)
    ax.text(0.24, 0.72, '100% accuracy (7/7)', ha='center', fontsize=18,
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.24, 0.62, 'Avg confidence: 0.876', ha='center', fontsize=11,
            transform=ax.transAxes)
    ax.text(0.24, 0.55, 'Calibration error: 0.124', ha='center', fontsize=11,
            transform=ax.transAxes)
    ax.text(0.24, 0.45, '• CLI identity → no GUI features\n'
            '• CommonMark spec\n• Auto-compression',
            ha='center', fontsize=9, transform=ax.transAxes, color='#555')

    # SP- box
    ax.add_patch(plt.Rectangle((0.54, 0.3), 0.44, 0.55, fill=True,
                               facecolor='#fdedec', edgecolor='#e74c3c', linewidth=2,
                               transform=ax.transAxes))
    ax.text(0.76, 0.80, 'SP- (External Knowledge)', ha='center', fontsize=13,
            fontweight='bold', color='#e74c3c', transform=ax.transAxes)
    ax.text(0.76, 0.72, '76.2% accuracy (16/21)', ha='center', fontsize=18,
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.76, 0.62, 'Avg confidence: 0.491', ha='center', fontsize=11,
            transform=ax.transAxes)
    ax.text(0.76, 0.55, 'Calibration error: 0.532', ha='center', fontsize=11,
            transform=ax.transAxes)
    ax.text(0.76, 0.45, '• Prompt char, layout, themes\n'
            '• Keyboard shortcuts\n• Recently-added features',
            ha='center', fontsize=9, transform=ax.transAxes, color='#555')

    # Bottom text
    ax.text(0.5, 0.18, 'Confidence gap: 0.876 vs 0.473 (p = 0.0013, Mann-Whitney U)',
            ha='center', fontsize=12, fontweight='bold', transform=ax.transAxes)
    ax.text(0.5, 0.10, 'All 5 wrong answers are SP- items. SP- MC accuracy (83%) still >> 25% chance.',
            ha='center', fontsize=10, transform=ax.transAxes, color='#555')
    ax.text(0.5, 0.03, '→ System prompt drives confidence; training data provides partial but real knowledge',
            ha='center', fontsize=11, fontweight='bold', color='#2c3e50', transform=ax.transAxes)

    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig_h1_summary.png', dpi=150, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig_h1_summary.pdf', bbox_inches='tight')
    plt.close()
    print("fig_h1_summary saved")


if __name__ == "__main__":
    fig_h1_main()
    fig_h1_domain_split()
    fig_h1_wrong_detail()
    fig_h1_summary()
    print(f"\nAll H1 figures saved to {FIG_DIR}")

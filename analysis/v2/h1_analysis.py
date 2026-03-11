"""
H1 Analysis: System Prompt vs Training Data as Source of Harness Knowledge

Classifies all 55 prompts as SP+ (answer derivable from system prompt) or
SP- (requires external knowledge), then analyzes accuracy differences.

Key information IN the system prompt:
- "You are Claude Code, Anthropic's official CLI for Claude"
- Tool names: Read, Edit, Write, Bash, Glob, Grep, Agent, etc.
- "Github-flavored markdown for formatting, rendered in a monospace font
   using the CommonMark specification"
- "The system will automatically compress prior messages"
- Permission modes exist ("user-selected permission mode")
- /help mentioned, /<skill-name> pattern mentioned
- /fast toggles fast mode, same model with faster output
- Platform: win32, Shell: bash, Model: Opus 4.6
- Auto memory at ~/.claude/projects/{hash}/memory/
- Skills: keybindings-help, simplify, claude-api, commit-commands, ralph-loop
- Deferred tools: Agent, AskUserQuestion, Bash, Edit, ..., Write (21 total)

Key information NOT in the system prompt:
- Startup screen layout (two-column, bordered box, logo, greeting)
- Prompt character (❯ vs >)
- Specific permission mode names (default, acceptEdits, plan, dontAsk, bypass)
- Shift+Tab for mode cycling
- Color themes (count, names, /theme command)
- Syntax highlighting (native build only)
- Diff view appearance and navigation
- Vim mode (/vim command)
- Output styles (Default, Explanatory, Learning)
- Error display formatting
- Status line appearance
- Most keyboard shortcuts (Ctrl+G, Ctrl+T, Ctrl+O, Esc+Esc, etc.)
- Checkpointing / rewind feature
- Personalized greeting
- Fast mode rate limit fallback behavior
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCORES_PATH = PROJECT_ROOT / "data" / "processed" / "v2" / "scores_v2.json"
SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "v2" / "summary_v2.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "v2"

# ─── SP Classification ───
# SP+ : Answer is directly stated in or logically inferrable from the system prompt
# SP- : Answer requires external knowledge (docs, screenshots, training data)
# SP+i: inferrable (subcategory of SP+)

SP_CLASSIFICATION = {
    # D1: Startup/Welcome Screen — ALL SP- (visual layout not in system prompt)
    "P01": {"sp": "SP-", "reason": "Startup visual layout not described in system prompt"},
    "P02": {"sp": "SP-", "reason": "Two-column layout is visual-only"},
    "P03": {"sp": "SP-", "reason": "Logo appearance is visual-only"},
    "P04": {"sp": "SP-", "reason": "Spatial layout not in system prompt"},
    "P05": {"sp": "SP-", "reason": "Logo characters are visual-only"},
    "P06": {"sp": "SP-", "reason": "Personalized greeting not mentioned"},
    "P07": {"sp": "SP-", "reason": "Border text format not described"},

    # D2: Input Area — ALL SP- (prompt char, multiline methods not in SP)
    "P08": {"sp": "SP-", "reason": "Prompt character and cursor not described"},
    "P09": {"sp": "SP-", "reason": "Prompt character (❯) not specified in SP"},
    "P10": {"sp": "SP-", "reason": "Prompt character not specified in SP"},
    "P11": {"sp": "SP-", "reason": "Below-input layout not described"},
    "P12": {"sp": "SP-", "reason": "Only / prefix mentioned; ! and @ not in SP"},
    "P13": {"sp": "SP-", "reason": "Multiline input methods not described"},

    # D3: Output & Response Display — MIXED
    "P14": {"sp": "SP-", "reason": "Tool execution display format not fully described"},
    "P15": {"sp": "SP-", "reason": "Verb tenses for tool display not specified"},
    "P16": {"sp": "SP+", "reason": "SP says 'markdown' and 'CommonMark', not HTML/CSS"},
    "P17": {"sp": "SP-", "reason": "Thinking indicator spatial arrangement not described"},
    "P18": {"sp": "SP+", "reason": "SP explicitly says 'CommonMark specification'"},
    "P19": {"sp": "SP-", "reason": "Output styles not mentioned in SP"},

    # D4: Permission Dialogs — MOSTLY SP-
    "P20": {"sp": "SP-", "reason": "Visual appearance of dialogs not described"},
    "P21": {"sp": "SP-", "reason": "Navigation method (Tab/arrows) not described"},
    "P22": {"sp": "SP-", "reason": "Inline vs popup not explicitly stated"},
    "P23": {"sp": "SP-", "reason": "Vertical layout of dialog not described"},
    "P24": {"sp": "SP-", "reason": "Specific mode names not listed in SP"},
    "P25": {"sp": "SP-", "reason": "Which tools need approval not explicitly stated"},

    # D5: Status Line — ALL SP-
    "P26": {"sp": "SP-", "reason": "Status line appearance not described"},
    "P27": {"sp": "SP-", "reason": "Context usage indicator not described"},
    "P28": {"sp": "SP-", "reason": "Startup status display not described"},
    "P29": {"sp": "SP-", "reason": "Exact startup status text not in SP"},
    "P30": {"sp": "SP-", "reason": "Spatial arrangement of status elements not described"},

    # D6: Navigation & Commands — MOSTLY SP-
    "P31": {"sp": "SP-", "reason": "Only /help and /<skill> pattern in SP; full list requires external knowledge"},
    "P32": {"sp": "SP-", "reason": "Ctrl+T shortcut not mentioned in SP"},
    "P33": {"sp": "SP-", "reason": "Vim mode not mentioned in SP"},
    "P34": {"sp": "SP-", "reason": "Escape behavior not described in SP"},
    "P35": {"sp": "SP-", "reason": "Shift+Tab not mentioned in SP"},
    "P36": {"sp": "SP-", "reason": "Ctrl+G not mentioned in SP"},

    # D7: Theming & Colors — ALL SP-
    "P37": {"sp": "SP-", "reason": "Themes not described in SP"},
    "P38": {"sp": "SP-", "reason": "Theme count not mentioned in SP"},
    "P39": {"sp": "SP-", "reason": "Syntax highlighting availability not mentioned"},
    "P40": {"sp": "SP-", "reason": "Theme picker not described in SP"},
    "P41": {"sp": "SP-", "reason": "/theme command not mentioned in SP"},

    # D8: Diff & File Editing — ALL SP-
    "P42": {"sp": "SP-", "reason": "Diff view not described in SP"},
    "P43": {"sp": "SP-", "reason": "Diff colors not described in SP"},
    "P44": {"sp": "SP-", "reason": "Checkpointing not described in SP"},
    "P45": {"sp": "SP-", "reason": "Diff navigation not described in SP"},
    "P46": {"sp": "SP-", "reason": "Rewind options not described in SP"},

    # D9: Error & Edge States — MOSTLY SP-
    "P47": {"sp": "SP-", "reason": "Error display not described in SP"},
    "P48": {"sp": "SP-", "reason": "Fast mode rate limit fallback not described"},
    "P49": {"sp": "SP+", "reason": "SP explicitly says 'automatically compress prior messages'"},
    "P50": {"sp": "SP-", "reason": "Retry visual indicator not described in SP"},

    # D10: Negative Space — ALL SP+ (inferrable from "CLI" identity)
    "P51": {"sp": "SP+", "reason": "SP says 'CLI'; no sidebar mentioned → inferrable"},
    "P52": {"sp": "SP+", "reason": "SP describes text interface; no avatars → inferrable"},
    "P53": {"sp": "SP+", "reason": "SP describes terminal tool; no image rendering → inferrable"},
    "P54": {"sp": "SP+", "reason": "SP describes CLI; no file tree panel → inferrable"},
    "P55": {"sp": "SP+", "reason": "SP describes keyboard-driven terminal → D is inferrable"},
}


def load_data():
    with open(SCORES_PATH, 'r', encoding='utf-8') as f:
        scores = json.load(f)
    with open(SUMMARY_PATH, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    return scores, summary


def classify_and_analyze():
    scores, summary = load_data()

    # Split prompts
    sp_plus = {pid: c for pid, c in SP_CLASSIFICATION.items() if c["sp"] == "SP+"}
    sp_minus = {pid: c for pid, c in SP_CLASSIFICATION.items() if c["sp"] == "SP-"}

    print(f"Total prompts: {len(SP_CLASSIFICATION)}")
    print(f"SP+ (system-prompt-derivable): {len(sp_plus)}")
    print(f"SP- (external knowledge needed): {len(sp_minus)}")

    # Analyze objective items (T2 + T3)
    sp_plus_obj = {"correct": 0, "total": 0, "confidences": [], "calib_errors": []}
    sp_minus_obj = {"correct": 0, "total": 0, "confidences": [], "calib_errors": []}

    # Analyze all items including free-recall
    sp_plus_all = {"correct_claims": 0, "total_claims": 0, "unverifiable": 0}
    sp_minus_all = {"correct_claims": 0, "total_claims": 0, "unverifiable": 0}

    details = []

    for pid, pdata in sorted(scores.items()):
        sp_label = SP_CLASSIFICATION[pid]["sp"]
        prompt_type = pdata.get("prompt_type", "unknown")
        domain = pdata.get("domain", "?")

        for trial in pdata["trials"]:
            pt = trial.get("prompt_type", "")
            conf = trial.get("confidence", None)

            if pt in ("forced_choice", "true_false"):
                correct = trial.get("correct", False)
                calib = trial.get("calibration_error", None)
                bucket = sp_plus_obj if sp_label == "SP+" else sp_minus_obj
                bucket["correct"] += int(correct)
                bucket["total"] += 1
                if conf is not None:
                    bucket["confidences"].append(conf)
                if calib is not None:
                    bucket["calib_errors"].append(calib)

                details.append({
                    "prompt_id": pid, "domain": domain, "type": pt,
                    "sp": sp_label, "correct": correct, "confidence": conf,
                    "answer_given": trial.get("answer_given"),
                    "correct_answer": trial.get("correct_answer"),
                })
            else:
                cc = trial.get("correct_count", 0)
                ic = trial.get("incorrect_count", 0)
                uc = trial.get("unverifiable_count", 0)
                tc = trial.get("total_claims", cc + ic + uc)
                bucket = sp_plus_all if sp_label == "SP+" else sp_minus_all
                bucket["correct_claims"] += cc
                bucket["total_claims"] += tc
                bucket["unverifiable"] += uc

    # Results
    print("\n" + "=" * 65)
    print("H1 ANALYSIS: SYSTEM PROMPT (SP+) vs EXTERNAL KNOWLEDGE (SP-)")
    print("=" * 65)

    print("\n── Objective Items (Forced Choice + True/False) ──")
    for label, data in [("SP+", sp_plus_obj), ("SP-", sp_minus_obj)]:
        acc = data["correct"] / data["total"] if data["total"] > 0 else 0
        avg_conf = np.mean(data["confidences"]) if data["confidences"] else 0
        avg_calib = np.mean(data["calib_errors"]) if data["calib_errors"] else 0
        print(f"  {label}: {data['correct']}/{data['total']} = {acc*100:.1f}%  "
              f"(avg_conf={avg_conf:.3f}, avg_calib_err={avg_calib:.3f})")

    print("\n── Free-Recall Claims ──")
    for label, data in [("SP+", sp_plus_all), ("SP-", sp_minus_all)]:
        total = data["total_claims"]
        cc = data["correct_claims"]
        print(f"  {label}: {cc}/{total} claims correct, {data['unverifiable']} unverifiable")

    # Statistical test (Fisher's exact test for objective items)
    print("\n── Statistical Test (Fisher's exact, objective items) ──")
    table = np.array([
        [sp_plus_obj["correct"], sp_plus_obj["total"] - sp_plus_obj["correct"]],
        [sp_minus_obj["correct"], sp_minus_obj["total"] - sp_minus_obj["correct"]],
    ])
    odds_ratio, p_value = stats.fisher_exact(table)
    print(f"  Contingency table:")
    print(f"    SP+: {table[0]} (correct, incorrect)")
    print(f"    SP-: {table[1]} (correct, incorrect)")
    print(f"  Fisher's exact test: OR={odds_ratio:.2f}, p={p_value:.4f}")
    if p_value < 0.05:
        print(f"  → Significant difference (p < 0.05)")
    else:
        print(f"  → Not significant at p < 0.05")

    # Chance baseline comparison
    print("\n── vs Chance Baselines (SP- only) ──")
    # T/F items in SP-
    sp_minus_tf = [d for d in details if d["sp"] == "SP-" and d["type"] == "true_false"]
    sp_minus_mc = [d for d in details if d["sp"] == "SP-" and d["type"] == "forced_choice"]
    tf_correct = sum(1 for d in sp_minus_tf if d["correct"])
    mc_correct = sum(1 for d in sp_minus_mc if d["correct"])

    if sp_minus_tf:
        tf_acc = tf_correct / len(sp_minus_tf)
        _, tf_p = stats.binomtest(tf_correct, len(sp_minus_tf), 0.5).statistic, stats.binomtest(tf_correct, len(sp_minus_tf), 0.5).pvalue
        print(f"  T/F (SP-): {tf_correct}/{len(sp_minus_tf)} = {tf_acc*100:.1f}%  "
              f"(vs 50% chance, binomial p={tf_p:.4f})")
    if sp_minus_mc:
        mc_acc = mc_correct / len(sp_minus_mc)
        _, mc_p = stats.binomtest(mc_correct, len(sp_minus_mc), 0.25).statistic, stats.binomtest(mc_correct, len(sp_minus_mc), 0.25).pvalue
        print(f"  MC (SP-): {mc_correct}/{len(sp_minus_mc)} = {mc_acc*100:.1f}%  "
              f"(vs 25% chance, binomial p={mc_p:.4f})")

    # Confidence analysis
    print("\n── Confidence Analysis ──")
    sp_plus_correct_conf = [d["confidence"] for d in details if d["sp"] == "SP+" and d["correct"] and d["confidence"] is not None]
    sp_minus_correct_conf = [d["confidence"] for d in details if d["sp"] == "SP-" and d["correct"] and d["confidence"] is not None]
    sp_minus_wrong_conf = [d["confidence"] for d in details if d["sp"] == "SP-" and not d["correct"] and d["confidence"] is not None]

    if sp_plus_correct_conf:
        print(f"  SP+ correct: avg_conf={np.mean(sp_plus_correct_conf):.3f} (n={len(sp_plus_correct_conf)})")
    if sp_minus_correct_conf:
        print(f"  SP- correct: avg_conf={np.mean(sp_minus_correct_conf):.3f} (n={len(sp_minus_correct_conf)})")
    if sp_minus_wrong_conf:
        print(f"  SP- wrong:   avg_conf={np.mean(sp_minus_wrong_conf):.3f} (n={len(sp_minus_wrong_conf)})")

    if sp_plus_correct_conf and sp_minus_correct_conf:
        t_stat, t_p = stats.mannwhitneyu(sp_plus_correct_conf, sp_minus_correct_conf, alternative='two-sided')
        print(f"  Mann-Whitney U (SP+ vs SP- correct conf): U={t_stat:.1f}, p={t_p:.4f}")

    # Domain breakdown
    print("\n── Domain Breakdown ──")
    domain_sp = defaultdict(lambda: {"sp+_correct": 0, "sp+_total": 0, "sp-_correct": 0, "sp-_total": 0})
    for d in details:
        dom = d["domain"]
        if d["sp"] == "SP+":
            domain_sp[dom]["sp+_correct"] += int(d["correct"])
            domain_sp[dom]["sp+_total"] += 1
        else:
            domain_sp[dom]["sp-_correct"] += int(d["correct"])
            domain_sp[dom]["sp-_total"] += 1

    domain_names = {
        "D1": "Startup", "D2": "Input", "D3": "Output", "D4": "Permission",
        "D5": "Status", "D6": "Navigation", "D7": "Theming", "D8": "Diff",
        "D9": "Error", "D10": "Negative(Ctrl)"
    }
    for dom in sorted(domain_sp.keys()):
        s = domain_sp[dom]
        name = domain_names.get(dom, dom)
        parts = []
        if s["sp+_total"] > 0:
            parts.append(f"SP+: {s['sp+_correct']}/{s['sp+_total']}")
        if s["sp-_total"] > 0:
            acc = s["sp-_correct"] / s["sp-_total"] * 100
            parts.append(f"SP-: {s['sp-_correct']}/{s['sp-_total']} ({acc:.0f}%)")
        print(f"  {dom} ({name}): {', '.join(parts)}")

    # Wrong answers detail
    print("\n── Wrong Answers (all SP-) ──")
    for d in details:
        if not d["correct"]:
            print(f"  {d['prompt_id']} ({d['domain']}, {d['type']}): "
                  f"answered={d['answer_given']}, expected={d['correct_answer']}, "
                  f"conf={d['confidence']:.2f}")

    # Save analysis results
    results = {
        "classification": SP_CLASSIFICATION,
        "objective_results": {
            "sp_plus": {
                "correct": sp_plus_obj["correct"],
                "total": sp_plus_obj["total"],
                "accuracy": sp_plus_obj["correct"] / sp_plus_obj["total"] if sp_plus_obj["total"] > 0 else 0,
                "avg_confidence": float(np.mean(sp_plus_obj["confidences"])) if sp_plus_obj["confidences"] else 0,
                "avg_calibration_error": float(np.mean(sp_plus_obj["calib_errors"])) if sp_plus_obj["calib_errors"] else 0,
            },
            "sp_minus": {
                "correct": sp_minus_obj["correct"],
                "total": sp_minus_obj["total"],
                "accuracy": sp_minus_obj["correct"] / sp_minus_obj["total"] if sp_minus_obj["total"] > 0 else 0,
                "avg_confidence": float(np.mean(sp_minus_obj["confidences"])) if sp_minus_obj["confidences"] else 0,
                "avg_calibration_error": float(np.mean(sp_minus_obj["calib_errors"])) if sp_minus_obj["calib_errors"] else 0,
            },
            "fisher_exact": {"odds_ratio": float(odds_ratio), "p_value": float(p_value)},
        },
        "confidence_analysis": {
            "sp_plus_correct_mean": float(np.mean(sp_plus_correct_conf)) if sp_plus_correct_conf else None,
            "sp_minus_correct_mean": float(np.mean(sp_minus_correct_conf)) if sp_minus_correct_conf else None,
            "sp_minus_wrong_mean": float(np.mean(sp_minus_wrong_conf)) if sp_minus_wrong_conf else None,
        },
        "details": details,
    }

    out_path = OUTPUT_DIR / "h1_analysis.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to {out_path}")

    return results


if __name__ == "__main__":
    classify_and_analyze()

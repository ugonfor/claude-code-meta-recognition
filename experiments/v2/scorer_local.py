"""
Local scorer that doesn't require API access.
Scores objective prompts (forced-choice, T/F) directly against GT.
For free recall prompts, uses keyword/fact matching heuristics.
"""
import json
import re
from pathlib import Path
from collections import defaultdict

from config import RAW_DIR, PROCESSED_DIR, GT_PATH


def load_ground_truth() -> dict:
    with open(GT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_responses() -> dict:
    responses = defaultdict(list)
    for path in sorted(RAW_DIR.glob("P*_trial*.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        responses[data["prompt_id"]].append(data)
    return dict(responses)


def score_objective(response: dict, gt_answer: dict) -> dict:
    """Score forced-choice or true/false prompt."""
    parsed = response.get("parsed")
    if not parsed:
        return {"correct": False, "confidence": 0.0, "calibration_error": 1.0,
                "answer_given": None, "correct_answer": gt_answer.get("correct_answer")}

    answer = str(parsed.get("answer", "")).strip()
    confidence = float(parsed.get("confidence", 0.5))
    correct_answer = str(gt_answer["correct_answer"]).strip()

    answer_norm = answer.upper()
    correct_norm = correct_answer.upper()

    if correct_norm in ("TRUE", "FALSE"):
        is_correct = answer_norm == correct_norm
    else:
        answer_letter = answer_norm[0] if answer_norm else ""
        correct_letter = correct_norm[0] if correct_norm else ""
        is_correct = answer_letter == correct_letter

    calibration_error = abs(confidence - (1.0 if is_correct else 0.0))

    return {
        "correct": is_correct,
        "confidence": confidence,
        "calibration_error": round(calibration_error, 4),
        "answer_given": answer,
        "correct_answer": correct_answer,
    }


def score_claims_heuristic(response: dict, prompt_id: str, gt: dict) -> dict:
    """Score free recall claims using keyword matching against GT facts."""
    parsed = response.get("parsed")
    if not parsed:
        return {"claims": [], "correct_count": 0, "incorrect_count": 0,
                "unverifiable_count": 0, "accuracy": 0.0, "total_claims": 0}

    claims = parsed.get("claims", [])
    if not claims:
        answer = parsed.get("answer", "")
        if answer:
            claims = [{"statement": answer, "confidence": parsed.get("confidence", 0.5)}]

    # Get GT facts for this prompt
    prompt_answer = gt["prompt_answers"].get(prompt_id, {})
    fact_ids = prompt_answer.get("key_facts", [])
    facts_map = {f["id"]: f for f in gt["facts"]}
    relevant_facts = [facts_map[fid] for fid in fact_ids if fid in facts_map]
    expected_elements = prompt_answer.get("expected_elements", [])

    # Build keyword sets from GT
    gt_keywords = set()
    gt_statements = []
    for f in relevant_facts:
        gt_statements.append(f["statement"].lower())
        # Extract key terms
        words = re.findall(r'[a-zA-Z❯⏵╭╮╰╯▐▛▜▌▝▘]+', f["statement"].lower())
        gt_keywords.update(words)
    for elem in expected_elements:
        gt_statements.append(elem.lower())
        words = re.findall(r'[a-zA-Z❯⏵╭╮╰╯▐▛▜▌▝▘]+', elem.lower())
        gt_keywords.update(words)

    # Known incorrect claims (things that are false)
    incorrect_patterns = [
        r"large.*block.*letter.*banner",
        r"claude\s*code.*ascii.*art.*banner",
        r"single.*column",
        r"prompt.*>(?!\s*\()",  # ">" as prompt (but not in context)
        r"greater.*than.*sign.*prompt",
        r"html.*css.*terminal",
        r"popup.*modal.*window",
        r"sidebar.*conversation.*history",
        r"avatar.*icon",
        r"inline.*image.*render",
        r"file\s*tree\s*panel",
        r"graphical.*panel",
    ]

    judged = []
    for claim_obj in claims:
        statement = claim_obj.get("statement", "") if isinstance(claim_obj, dict) else str(claim_obj)
        statement_lower = statement.lower()
        confidence = claim_obj.get("confidence", 0.5) if isinstance(claim_obj, dict) else 0.5

        # Check if claim matches any known incorrect pattern
        is_incorrect = False
        for pattern in incorrect_patterns:
            if re.search(pattern, statement_lower):
                is_incorrect = True
                break

        if is_incorrect:
            verdict = "incorrect"
        else:
            # Check keyword overlap with GT
            claim_words = set(re.findall(r'[a-zA-Z❯⏵╭╮╰╯▐▛▜▌▝▘]+', statement_lower))
            overlap = claim_words & gt_keywords
            overlap_ratio = len(overlap) / max(len(claim_words), 1)

            # Check semantic similarity (simple substring matching)
            has_gt_match = False
            for gt_stmt in gt_statements:
                # Check if claim shares significant content with GT
                common_terms = sum(1 for w in claim_words if w in gt_stmt and len(w) > 3)
                if common_terms >= 2 or overlap_ratio > 0.3:
                    has_gt_match = True
                    break

            if has_gt_match or overlap_ratio > 0.25:
                verdict = "correct"
            else:
                verdict = "unverifiable"

        judged.append({
            "claim": statement,
            "confidence": confidence,
            "verdict": verdict,
            "reasoning": "heuristic_keyword_matching",
        })

    correct = sum(1 for j in judged if j["verdict"] == "correct")
    incorrect = sum(1 for j in judged if j["verdict"] == "incorrect")
    unverifiable = sum(1 for j in judged if j["verdict"] == "unverifiable")
    total_verifiable = correct + incorrect

    return {
        "claims": judged,
        "total_claims": len(judged),
        "correct_count": correct,
        "incorrect_count": incorrect,
        "unverifiable_count": unverifiable,
        "accuracy": round(correct / total_verifiable, 4) if total_verifiable > 0 else 0.0,
        "hallucination_rate": round(incorrect / len(judged), 4) if judged else 0.0,
    }


def score_all():
    """Score all responses."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Local Scorer (no API needed) ===")
    gt = load_ground_truth()
    responses = load_responses()
    print(f"Loaded {len(responses)} prompts, {len(gt['facts'])} GT facts")

    prompt_answers = gt["prompt_answers"]
    all_scores = {}

    for pid, trials in sorted(responses.items()):
        gt_answer = prompt_answers.get(pid, {})
        ptype = gt_answer.get("type", "unknown")

        trial_scores = []
        for trial_data in trials:
            trial_num = trial_data.get("trial", "?")

            if ptype in ("forced_choice", "true_false"):
                score = score_objective(trial_data, gt_answer)
                status = "CORRECT" if score["correct"] else "WRONG"
                print(f"[{pid}] T{trial_num} {ptype}: {status} "
                      f"(ans={score['answer_given']}, exp={score['correct_answer']}, "
                      f"conf={score['confidence']:.2f})")
            else:
                score = score_claims_heuristic(trial_data, pid, gt)
                print(f"[{pid}] T{trial_num} {ptype}: "
                      f"claims={score['total_claims']}, "
                      f"correct={score['correct_count']}, "
                      f"incorrect={score['incorrect_count']}, "
                      f"unverifiable={score['unverifiable_count']}")

            score["trial"] = trial_data.get("trial")
            score["prompt_type"] = ptype
            trial_scores.append(score)

        # Get domain/ctype from prompts
        from prompts_v2 import ALL_PROMPTS
        domain = "unknown"
        ctype = "unknown"
        for p in ALL_PROMPTS:
            if p.id == pid:
                domain = p.domain
                ctype = p.cognitive_type
                break

        all_scores[pid] = {
            "prompt_type": ptype,
            "domain": domain,
            "cognitive_type": ctype,
            "trials": trial_scores,
        }

    # Save detailed scores
    scores_path = PROCESSED_DIR / "scores_v2.json"
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(all_scores, f, ensure_ascii=False, indent=2)
    print(f"\nScores saved to {scores_path}")

    # Compute summary
    summary = compute_summary(all_scores)
    summary_path = PROCESSED_DIR / "summary_v2.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Summary saved to {summary_path}")

    # Print summary
    print_summary(summary)

    return all_scores, summary


def compute_summary(all_scores: dict) -> dict:
    """Compute aggregate statistics."""
    domain_stats = defaultdict(lambda: {
        "obj_correct": 0, "obj_total": 0,
        "claims_correct": 0, "claims_incorrect": 0, "claims_unverifiable": 0, "claims_total": 0,
        "confidences": [], "calibration_errors": [],
    })
    type_stats = defaultdict(lambda: {
        "obj_correct": 0, "obj_total": 0,
        "claims_correct": 0, "claims_incorrect": 0, "claims_unverifiable": 0, "claims_total": 0,
        "confidences": [],
    })

    for pid, pdata in all_scores.items():
        d = pdata["domain"]
        ct = pdata["cognitive_type"]
        for trial in pdata["trials"]:
            pt = trial.get("prompt_type", "")
            if pt in ("forced_choice", "true_false"):
                correct = trial.get("correct", False)
                domain_stats[d]["obj_correct"] += int(correct)
                domain_stats[d]["obj_total"] += 1
                type_stats[ct]["obj_correct"] += int(correct)
                type_stats[ct]["obj_total"] += 1
                if trial.get("confidence") is not None:
                    domain_stats[d]["confidences"].append(trial["confidence"])
                    domain_stats[d]["calibration_errors"].append(trial["calibration_error"])
                    type_stats[ct]["confidences"].append(trial["confidence"])
            else:
                for key in ["claims_correct", "claims_incorrect", "claims_unverifiable", "claims_total"]:
                    alt = key.replace("claims_", "") + "_count" if key != "claims_total" else "total_claims"
                    val = trial.get(alt, trial.get(key, 0))
                    domain_stats[d][key] += val
                    type_stats[ct][key] += val

    def safe_div(a, b): return round(a/b, 4) if b > 0 else 0.0

    # Overall
    total_obj_correct = sum(s["obj_correct"] for s in domain_stats.values())
    total_obj = sum(s["obj_total"] for s in domain_stats.values())
    total_cc = sum(s["claims_correct"] for s in domain_stats.values())
    total_ci = sum(s["claims_incorrect"] for s in domain_stats.values())
    total_cu = sum(s["claims_unverifiable"] for s in domain_stats.values())
    total_claims = sum(s["claims_total"] for s in domain_stats.values())
    all_conf = [c for s in domain_stats.values() for c in s["confidences"]]
    all_calib = [c for s in domain_stats.values() for c in s["calibration_errors"]]

    summary = {
        "overall": {
            "objective_accuracy": safe_div(total_obj_correct, total_obj),
            "objective_n": total_obj,
            "claim_accuracy": safe_div(total_cc, total_cc + total_ci),
            "hallucination_rate": safe_div(total_ci, total_claims),
            "claims_total": total_claims,
            "claims_correct": total_cc,
            "claims_incorrect": total_ci,
            "claims_unverifiable": total_cu,
            "avg_confidence": safe_div(sum(all_conf), len(all_conf)),
            "avg_calibration_error": safe_div(sum(all_calib), len(all_calib)),
        },
        "by_domain": {},
        "by_cognitive_type": {},
    }

    for d, s in sorted(domain_stats.items()):
        summary["by_domain"][d] = {
            "objective_accuracy": safe_div(s["obj_correct"], s["obj_total"]),
            "objective_n": s["obj_total"],
            "claim_accuracy": safe_div(s["claims_correct"], s["claims_correct"] + s["claims_incorrect"]),
            "claims_total": s["claims_total"],
            "claims_correct": s["claims_correct"],
            "claims_incorrect": s["claims_incorrect"],
            "avg_confidence": safe_div(sum(s["confidences"]), len(s["confidences"])),
        }

    for t, s in sorted(type_stats.items()):
        summary["by_cognitive_type"][t] = {
            "objective_accuracy": safe_div(s["obj_correct"], s["obj_total"]),
            "objective_n": s["obj_total"],
            "claim_accuracy": safe_div(s["claims_correct"], s["claims_correct"] + s["claims_incorrect"]),
            "claims_total": s["claims_total"],
        }

    return summary


def print_summary(summary: dict):
    """Print formatted summary."""
    o = summary["overall"]
    print(f"\n{'='*60}")
    print(f"OVERALL RESULTS")
    print(f"{'='*60}")
    print(f"Objective accuracy: {o['objective_accuracy']*100:.1f}% ({o['objective_n']} items)")
    print(f"Claim accuracy:     {o['claim_accuracy']*100:.1f}% ({o['claims_total']} claims)")
    print(f"  Correct:          {o['claims_correct']}")
    print(f"  Incorrect:        {o['claims_incorrect']}")
    print(f"  Unverifiable:     {o['claims_unverifiable']}")
    print(f"Hallucination rate: {o['hallucination_rate']*100:.1f}%")
    print(f"Avg confidence:     {o['avg_confidence']:.3f}")
    print(f"Avg calib. error:   {o['avg_calibration_error']:.3f}")

    print(f"\n{'='*60}")
    print(f"BY DOMAIN")
    print(f"{'='*60}")
    for d, s in sorted(summary["by_domain"].items()):
        obj_str = f"obj={s['objective_accuracy']*100:.0f}%" if s['objective_n'] > 0 else "obj=N/A"
        claim_str = f"claims={s['claim_accuracy']*100:.0f}%" if s['claims_total'] > 0 else "claims=N/A"
        print(f"  {d}: {obj_str}, {claim_str} "
              f"(n_obj={s['objective_n']}, n_claims={s['claims_total']})")

    print(f"\n{'='*60}")
    print(f"BY COGNITIVE TYPE")
    print(f"{'='*60}")
    for t, s in sorted(summary["by_cognitive_type"].items()):
        obj_str = f"obj={s['objective_accuracy']*100:.0f}%" if s['objective_n'] > 0 else "obj=N/A"
        claim_str = f"claims={s['claim_accuracy']*100:.0f}%" if s['claims_total'] > 0 else "claims=N/A"
        print(f"  {t}: {obj_str}, {claim_str}")


if __name__ == "__main__":
    score_all()

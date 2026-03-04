"""
Experiment v2 Scorer: Automated scoring pipeline.

Scores responses against ground truth using:
- Binary correct/incorrect for objective prompts (forced choice, T/F)
- LLM judge for free recall claims
"""
import json
import random
import sys
from pathlib import Path
from collections import defaultdict

import anthropic

from config import (
    RAW_DIR, PROCESSED_DIR, GT_PATH,
    N_TRIALS, SPOTCHECK_RATIO,
)
from judge import load_ground_truth, judge_claims_batch


def load_responses() -> dict:
    """Load all response files, grouped by prompt_id."""
    responses = defaultdict(list)
    for path in sorted(RAW_DIR.glob("P*_trial*.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        responses[data["prompt_id"]].append(data)
    return dict(responses)


def score_objective(response: dict, gt_answer: dict) -> dict:
    """Score a forced-choice or true/false response."""
    parsed = response.get("parsed")
    if not parsed:
        return {
            "correct": False,
            "confidence": 0.0,
            "calibration_error": 1.0,
            "answer_given": None,
            "correct_answer": gt_answer.get("correct_answer"),
            "error": "Response not parsed",
        }

    answer = str(parsed.get("answer", "")).strip()
    confidence = float(parsed.get("confidence", 0.5))
    correct_answer = str(gt_answer["correct_answer"]).strip()

    # Normalize for comparison
    answer_norm = answer.upper()
    correct_norm = correct_answer.upper()

    # Handle True/False
    if correct_norm in ("TRUE", "FALSE"):
        is_correct = answer_norm == correct_norm
    else:
        # Forced choice: extract just the letter
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


def score_free_recall(response: dict, prompt_id: str, gt: dict,
                      client: anthropic.Anthropic) -> dict:
    """Score a free recall response using LLM judge."""
    parsed = response.get("parsed")
    if not parsed:
        return {
            "claims": [],
            "correct_count": 0,
            "incorrect_count": 0,
            "unverifiable_count": 0,
            "accuracy": 0.0,
            "error": "Response not parsed",
        }

    claims = parsed.get("claims", [])
    if not claims:
        # If no claims extracted, try to score the answer as a single claim
        answer = parsed.get("answer", "")
        if answer:
            claims = [{"statement": answer, "confidence": parsed.get("confidence", 0.5)}]

    # Judge each claim
    judged = judge_claims_batch(client, claims, prompt_id, gt)

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


def score_all(responses: dict, gt: dict) -> dict:
    """Score all responses."""
    client = anthropic.Anthropic()
    prompt_answers = gt["prompt_answers"]
    all_scores = {}

    for prompt_id, trials in sorted(responses.items()):
        gt_answer = prompt_answers.get(prompt_id, {})
        prompt_type = gt_answer.get("type", "unknown")

        print(f"\n[{prompt_id}] type={prompt_type}, {len(trials)} trial(s)")

        trial_scores = []
        for trial_data in trials:
            trial_num = trial_data.get("trial", "?")
            print(f"  Trial {trial_num}:", end=" ", flush=True)

            if prompt_type in ("forced_choice", "true_false"):
                score = score_objective(trial_data, gt_answer)
                print(f"{'CORRECT' if score['correct'] else 'WRONG'} "
                      f"(answer={score['answer_given']}, expected={score['correct_answer']}, "
                      f"conf={score['confidence']:.2f})")
            elif prompt_type in ("free_recall", "spatial", "exact_detail"):
                score = score_free_recall(trial_data, prompt_id, gt, client)
                print(f"claims={score['total_claims']}, "
                      f"correct={score['correct_count']}, "
                      f"incorrect={score['incorrect_count']}, "
                      f"acc={score['accuracy']:.2f}")
            else:
                score = {"error": f"Unknown prompt type: {prompt_type}"}
                print(f"UNKNOWN TYPE: {prompt_type}")

            score["trial"] = trial_data.get("trial")
            score["prompt_type"] = prompt_type
            trial_scores.append(score)

        all_scores[prompt_id] = {
            "prompt_type": prompt_type,
            "domain": prompt_id_to_domain(prompt_id),
            "cognitive_type": prompt_id_to_ctype(prompt_id),
            "trials": trial_scores,
        }

    return all_scores


def prompt_id_to_domain(prompt_id: str) -> str:
    """Map prompt ID to domain."""
    from prompts_v2 import ALL_PROMPTS
    for p in ALL_PROMPTS:
        if p.id == prompt_id:
            return p.domain
    return "unknown"


def prompt_id_to_ctype(prompt_id: str) -> str:
    """Map prompt ID to cognitive type."""
    from prompts_v2 import ALL_PROMPTS
    for p in ALL_PROMPTS:
        if p.id == prompt_id:
            return p.cognitive_type
    return "unknown"


def aggregate_scores(all_scores: dict) -> dict:
    """Compute aggregate statistics."""
    # Per-domain
    domain_stats = defaultdict(lambda: {"correct": 0, "total": 0, "claims_correct": 0,
                                         "claims_incorrect": 0, "claims_total": 0})
    # Per-cognitive-type
    type_stats = defaultdict(lambda: {"correct": 0, "total": 0, "claims_correct": 0,
                                       "claims_incorrect": 0, "claims_total": 0})
    # Overall
    overall = {"objective_correct": 0, "objective_total": 0,
               "claims_correct": 0, "claims_incorrect": 0, "claims_unverifiable": 0,
               "claims_total": 0, "confidences": [], "calibration_errors": []}

    for pid, pdata in all_scores.items():
        domain = pdata["domain"]
        ctype = pdata["cognitive_type"]

        for trial in pdata["trials"]:
            ptype = trial.get("prompt_type", "")

            if ptype in ("forced_choice", "true_false"):
                is_correct = trial.get("correct", False)
                domain_stats[domain]["correct"] += int(is_correct)
                domain_stats[domain]["total"] += 1
                type_stats[ctype]["correct"] += int(is_correct)
                type_stats[ctype]["total"] += 1
                overall["objective_correct"] += int(is_correct)
                overall["objective_total"] += 1
                if trial.get("confidence") is not None:
                    overall["confidences"].append(trial["confidence"])
                    overall["calibration_errors"].append(trial["calibration_error"])

            elif ptype in ("free_recall", "spatial", "exact_detail"):
                cc = trial.get("correct_count", 0)
                ic = trial.get("incorrect_count", 0)
                uc = trial.get("unverifiable_count", 0)
                tc = trial.get("total_claims", 0)

                domain_stats[domain]["claims_correct"] += cc
                domain_stats[domain]["claims_incorrect"] += ic
                domain_stats[domain]["claims_total"] += tc
                type_stats[ctype]["claims_correct"] += cc
                type_stats[ctype]["claims_incorrect"] += ic
                type_stats[ctype]["claims_total"] += tc
                overall["claims_correct"] += cc
                overall["claims_incorrect"] += ic
                overall["claims_unverifiable"] += uc
                overall["claims_total"] += tc

                # Per-claim confidences
                for claim in trial.get("claims", []):
                    if claim.get("confidence") is not None:
                        overall["confidences"].append(claim["confidence"])

    # Compute rates
    def safe_div(a, b):
        return round(a / b, 4) if b > 0 else 0.0

    summary = {
        "overall": {
            "objective_accuracy": safe_div(overall["objective_correct"], overall["objective_total"]),
            "objective_n": overall["objective_total"],
            "claim_accuracy": safe_div(overall["claims_correct"],
                                       overall["claims_correct"] + overall["claims_incorrect"]),
            "hallucination_rate": safe_div(overall["claims_incorrect"], overall["claims_total"]),
            "claims_total": overall["claims_total"],
            "claims_correct": overall["claims_correct"],
            "claims_incorrect": overall["claims_incorrect"],
            "claims_unverifiable": overall["claims_unverifiable"],
            "avg_confidence": safe_div(sum(overall["confidences"]), len(overall["confidences"])),
            "avg_calibration_error": safe_div(sum(overall["calibration_errors"]),
                                              len(overall["calibration_errors"])),
        },
        "by_domain": {},
        "by_cognitive_type": {},
    }

    for d, s in domain_stats.items():
        summary["by_domain"][d] = {
            "objective_accuracy": safe_div(s["correct"], s["total"]),
            "objective_n": s["total"],
            "claim_accuracy": safe_div(s["claims_correct"],
                                       s["claims_correct"] + s["claims_incorrect"]),
            "claims_total": s["claims_total"],
        }

    for t, s in type_stats.items():
        summary["by_cognitive_type"][t] = {
            "objective_accuracy": safe_div(s["correct"], s["total"]),
            "objective_n": s["total"],
            "claim_accuracy": safe_div(s["claims_correct"],
                                       s["claims_correct"] + s["claims_incorrect"]),
            "claims_total": s["claims_total"],
        }

    return summary


def generate_spotcheck_sample(all_scores: dict) -> list:
    """Generate stratified sample for human spot-check."""
    all_claims = []
    for pid, pdata in all_scores.items():
        for trial in pdata["trials"]:
            for claim in trial.get("claims", []):
                all_claims.append({
                    "prompt_id": pid,
                    "domain": pdata["domain"],
                    "trial": trial.get("trial"),
                    **claim,
                })

    if not all_claims:
        return []

    # Stratified sampling
    n_sample = max(1, int(len(all_claims) * SPOTCHECK_RATIO))

    # Ensure representation of each verdict type
    by_verdict = defaultdict(list)
    for c in all_claims:
        by_verdict[c.get("verdict", "unknown")].append(c)

    sample = []
    # Include all unverifiable claims
    sample.extend(by_verdict.get("unverifiable", []))

    # Add at least 5 correct and 5 incorrect
    for verdict in ["correct", "incorrect"]:
        pool = by_verdict.get(verdict, [])
        n_needed = min(5, len(pool))
        sample.extend(random.sample(pool, n_needed))

    # Fill remaining quota from all claims
    remaining = n_sample - len(sample)
    if remaining > 0:
        sampled_ids = {id(c) for c in sample}
        available = [c for c in all_claims if id(c) not in sampled_ids]
        if available:
            sample.extend(random.sample(available, min(remaining, len(available))))

    return sample


def run_scoring():
    """Main scoring pipeline."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Experiment v2 Scorer ===")
    print(f"Loading ground truth from {GT_PATH}")
    gt = load_ground_truth()

    print(f"Loading responses from {RAW_DIR}")
    responses = load_responses()
    print(f"Found {len(responses)} prompts with responses")

    print("\n--- Scoring ---")
    all_scores = score_all(responses, gt)

    # Save detailed scores
    scores_path = PROCESSED_DIR / "scores_v2.json"
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(all_scores, f, ensure_ascii=False, indent=2)
    print(f"\nDetailed scores saved to {scores_path}")

    # Compute aggregates
    print("\n--- Aggregating ---")
    summary = aggregate_scores(all_scores)
    summary_path = PROCESSED_DIR / "summary_v2.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Summary saved to {summary_path}")

    # Print summary
    o = summary["overall"]
    print(f"\n=== Results ===")
    print(f"Objective accuracy: {o['objective_accuracy']*100:.1f}% ({o['objective_n']} items)")
    print(f"Claim accuracy: {o['claim_accuracy']*100:.1f}% ({o['claims_total']} claims)")
    print(f"Hallucination rate: {o['hallucination_rate']*100:.1f}%")
    print(f"Avg confidence: {o['avg_confidence']:.3f}")
    print(f"Avg calibration error: {o['avg_calibration_error']:.3f}")

    # Generate spot-check sample
    print("\n--- Spot-check Sample ---")
    sample = generate_spotcheck_sample(all_scores)
    spotcheck_path = PROCESSED_DIR / "human_spotcheck.json"
    with open(spotcheck_path, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)
    print(f"Spot-check sample: {len(sample)} claims saved to {spotcheck_path}")


if __name__ == "__main__":
    run_scoring()

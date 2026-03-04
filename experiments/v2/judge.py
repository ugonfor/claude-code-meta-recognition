"""
LLM Judge for claim verification.

Uses a separate model instance to evaluate individual claims against ground truth.
"""
import json
import anthropic

from config import JUDGE_MODEL, MAX_TOKENS_JUDGE, TEMPERATURE_JUDGE, GT_PATH


def load_ground_truth() -> dict:
    with open(GT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_relevant_facts(prompt_id: str, gt: dict) -> str:
    """Get GT facts relevant to a prompt, formatted for the judge."""
    prompt_answer = gt["prompt_answers"].get(prompt_id, {})
    fact_ids = prompt_answer.get("key_facts", [])

    # Collect facts by ID
    facts_map = {f["id"]: f for f in gt["facts"]}
    relevant_facts = [facts_map[fid] for fid in fact_ids if fid in facts_map]

    # Also include expected elements
    expected = prompt_answer.get("expected_elements", [])

    lines = []
    if relevant_facts:
        lines.append("=== Verified Facts ===")
        for f in relevant_facts:
            conf = f["confidence"]
            lines.append(f"[{f['id']}] ({conf}) {f['statement']}")

    if expected:
        lines.append("\n=== Expected Elements ===")
        for elem in expected:
            lines.append(f"- {elem}")

    # For objective prompts, include the correct answer
    correct = prompt_answer.get("correct_answer")
    explanation = prompt_answer.get("explanation", "")
    if correct is not None:
        lines.append(f"\n=== Correct Answer ===")
        lines.append(f"Answer: {correct}")
        if explanation:
            lines.append(f"Explanation: {explanation}")

    return "\n".join(lines)


JUDGE_SYSTEM_PROMPT = """You are a strict, objective fact-checker for claims about the Claude Code CLI interface.
You will be given ground truth facts (verified from screenshots and official documentation) and a claim to evaluate.

You MUST respond with valid JSON only, no other text. Format:
{
  "verdict": "correct" | "incorrect" | "unverifiable",
  "reasoning": "<brief explanation>",
  "matched_facts": ["GT_ID1", ...]
}

Rules:
- "correct": The claim is clearly supported by the ground truth facts
- "incorrect": The claim clearly contradicts the ground truth facts
- "unverifiable": The ground truth does not contain enough information to verify or refute this claim
- Be strict: if a claim includes any incorrect detail mixed with correct ones, mark it "incorrect"
- For partially correct claims, still mark as "incorrect" but note what's right in reasoning
"""


def judge_claim(client: anthropic.Anthropic, claim: str, gt_context: str) -> dict:
    """Judge a single claim against ground truth."""
    user_msg = f"""Ground truth (verified from screenshots and documentation):
{gt_context}

Claim to evaluate: "{claim}"

Classify this claim and respond with JSON only."""

    try:
        response = client.messages.create(
            model=JUDGE_MODEL,
            max_tokens=MAX_TOKENS_JUDGE,
            temperature=TEMPERATURE_JUDGE,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text

        # Parse JSON
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                result = json.loads(match.group())
            else:
                result = {"verdict": "unverifiable", "reasoning": f"Judge response not parseable: {raw[:200]}", "matched_facts": []}

        return result

    except Exception as e:
        return {"verdict": "unverifiable", "reasoning": f"Judge error: {str(e)}", "matched_facts": []}


def judge_claims_batch(client: anthropic.Anthropic, claims: list, prompt_id: str,
                       gt: dict) -> list:
    """Judge a batch of claims for a single prompt."""
    gt_context = get_relevant_facts(prompt_id, gt)
    results = []
    for claim_obj in claims:
        statement = claim_obj if isinstance(claim_obj, str) else claim_obj.get("statement", str(claim_obj))
        verdict = judge_claim(client, statement, gt_context)
        results.append({
            "claim": statement,
            "confidence": claim_obj.get("confidence", None) if isinstance(claim_obj, dict) else None,
            **verdict,
        })
    return results

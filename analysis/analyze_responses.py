"""
Analysis script for Claude Code meta-recognition experiment.
Compares Claude's responses against ground truth and generates scores.
"""

import json
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures"


def load_response_file(filepath):
    """Load a markdown response file and parse into sections."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by experiment ID headers (E1.1, E2.3, etc.)
    sections = {}
    current_id = None
    current_content = []

    for line in content.split('\n'):
        # Match patterns like "## E1.1" or "**E1.1**" or "# E1.1"
        match = re.match(r'^[#*\s]*\*?\*?(E\d+\.\d+)\*?\*?', line)
        if match:
            if current_id:
                sections[current_id] = '\n'.join(current_content).strip()
            current_id = match.group(1)
            current_content = []
        else:
            current_content.append(line)

    if current_id:
        sections[current_id] = '\n'.join(current_content).strip()

    return sections


def load_all_responses():
    """Load all experiment response files."""
    all_responses = {}
    for i in range(1, 8):
        filepath = RAW_DIR / f"E{i}_responses.md"
        if filepath.exists():
            sections = load_response_file(filepath)
            all_responses.update(sections)
        else:
            print(f"Warning: {filepath} not found")
    return all_responses


def load_ground_truth():
    """Load ground truth document."""
    gt_path = DATA_DIR / "ground_truth" / "claude_code_ui_ground_truth.md"
    if gt_path.exists():
        with open(gt_path, 'r', encoding='utf-8') as f:
            return f.read()
    print("Warning: Ground truth file not found")
    return ""


def extract_claims(response_text):
    """Extract individual factual claims from a response."""
    # Split into sentences and filter for factual claims
    sentences = re.split(r'[.!?]\s+', response_text)
    claims = []
    for s in sentences:
        s = s.strip()
        if len(s) > 20:  # Filter out very short fragments
            claims.append(s)
    return claims


def compute_word_overlap(text1, text2):
    """Compute word-level overlap between two texts."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    return len(intersection) / max(len(words1), len(words2))


def analyze_uncertainty_markers(text):
    """Count uncertainty markers in text."""
    uncertainty_phrases = [
        "i'm not sure", "i think", "i believe", "possibly", "probably",
        "may ", "might ", "could be", "i'm uncertain", "not certain",
        "i don't know", "i'm not confident", "approximately", "roughly",
        "if i recall", "from what i remember", "i may be wrong",
        "uncertain", "unsure", "speculate", "guess"
    ]
    text_lower = text.lower()
    count = sum(1 for phrase in uncertainty_phrases if phrase in text_lower)
    return count


def analyze_confidence_markers(text):
    """Count confidence markers in text."""
    confidence_phrases = [
        "definitely", "certainly", "clearly", "obviously",
        "without a doubt", "for sure", "absolutely",
        "it is", "it has", "it shows", "it displays",
        "you will see", "you can see", "it features"
    ]
    text_lower = text.lower()
    count = sum(1 for phrase in confidence_phrases if phrase in text_lower)
    return count


def generate_summary_stats(all_responses):
    """Generate summary statistics across all responses."""
    stats = {
        "total_responses": len(all_responses),
        "avg_response_length": 0,
        "total_claims": 0,
        "avg_uncertainty_markers": 0,
        "avg_confidence_markers": 0,
        "responses_by_category": {},
    }

    total_len = 0
    total_uncertainty = 0
    total_confidence = 0

    for exp_id, text in all_responses.items():
        total_len += len(text.split())
        claims = extract_claims(text)
        stats["total_claims"] += len(claims)
        total_uncertainty += analyze_uncertainty_markers(text)
        total_confidence += analyze_confidence_markers(text)

        # Categorize by experiment
        category = exp_id.split('.')[0]  # E1, E2, etc.
        if category not in stats["responses_by_category"]:
            stats["responses_by_category"][category] = []
        stats["responses_by_category"][category].append({
            "id": exp_id,
            "word_count": len(text.split()),
            "claim_count": len(claims),
            "uncertainty_markers": analyze_uncertainty_markers(text),
            "confidence_markers": analyze_confidence_markers(text),
        })

    n = max(len(all_responses), 1)
    stats["avg_response_length"] = total_len / n
    stats["avg_uncertainty_markers"] = total_uncertainty / n
    stats["avg_confidence_markers"] = total_confidence / n

    return stats


if __name__ == "__main__":
    print("Loading responses...")
    responses = load_all_responses()
    print(f"Loaded {len(responses)} responses")

    print("\nLoading ground truth...")
    gt = load_ground_truth()
    print(f"Ground truth: {len(gt)} chars")

    print("\nGenerating summary statistics...")
    stats = generate_summary_stats(responses)
    print(json.dumps(stats, indent=2, default=str))

    # Save stats
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(PROCESSED_DIR / "summary_stats.json", 'w') as f:
        json.dump(stats, f, indent=2, default=str)

    print(f"\nSaved stats to {PROCESSED_DIR / 'summary_stats.json'}")

"""Helper script to save batched agent responses to individual JSON files."""
import json
import sys
from datetime import datetime
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "v2" / "responses"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def save_batch(responses: list, trial: int = 1, model: str = "claude-sonnet-4-20250514"):
    """Save a batch of responses to individual files."""
    for item in responses:
        pid = item["prompt_id"]
        result = {
            "prompt_id": pid,
            "trial": trial,
            "backend": "subagent",
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "raw_text": json.dumps(item, ensure_ascii=False),
            "parsed": item,
            "parse_success": True,
        }
        path = RAW_DIR / f"{pid}_trial{trial}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Saved {path.name}")


def save_from_file(json_file: str, trial: int = 1):
    """Load batch from JSON file and save."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    save_batch(data, trial)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        save_from_file(sys.argv[1], trial=int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    else:
        print("Usage: python save_batch.py <json_file> [trial_number]")

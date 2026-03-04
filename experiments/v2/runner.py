"""
Experiment v2 Runner: Executes prompts and collects structured JSON responses.

Two backends:
1. API mode (--backend api): Uses Anthropic API directly for clean responses
   without Claude Code system prompt context. Requires ANTHROPIC_API_KEY.
2. CLI mode (--backend cli): Uses `claude -p` with --system-prompt override.
   No separate API key needed; uses existing Claude Code auth.
"""
import json
import os
import re
import subprocess
import time
import sys
import tempfile
from pathlib import Path
from datetime import datetime

from config import (
    RAW_DIR, N_TRIALS, SUBJECT_MODEL,
    MAX_TOKENS_RESPONSE, TEMPERATURE_SUBJECT,
)
from prompts_v2 import ALL_PROMPTS, SYSTEM_PROMPT


def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def parse_json_response(raw_text: str) -> dict | None:
    """Try to parse JSON from raw response text."""
    if not raw_text:
        return None
    # Direct parse
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass
    # Extract from markdown code block
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    # Try to find the first { ... } block
    brace_match = re.search(r'\{[\s\S]*\}', raw_text)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass
    return None


# =============================================================================
# Backend: Anthropic API
# =============================================================================

def run_via_api(prompt_text: str, prompt_id: str, trial: int) -> dict:
    """Run a single prompt via Anthropic API."""
    import anthropic
    client = anthropic.Anthropic()

    print(f"  [API] {prompt_id} trial {trial}...", end=" ", flush=True)
    t0 = time.time()

    try:
        response = client.messages.create(
            model=SUBJECT_MODEL,
            max_tokens=MAX_TOKENS_RESPONSE,
            temperature=TEMPERATURE_SUBJECT,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt_text}],
        )

        raw_text = response.content[0].text
        elapsed = time.time() - t0
        parsed = parse_json_response(raw_text)

        result = {
            "prompt_id": prompt_id,
            "trial": trial,
            "backend": "api",
            "model": SUBJECT_MODEL,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "raw_text": raw_text,
            "parsed": parsed,
            "parse_success": parsed is not None,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }
        status = "OK" if parsed else "PARSE_FAIL"
        print(f"{status} ({elapsed:.1f}s, {response.usage.output_tokens} tok)")
        return result

    except Exception as e:
        elapsed = time.time() - t0
        print(f"ERROR: {e} ({elapsed:.1f}s)")
        return {
            "prompt_id": prompt_id,
            "trial": trial,
            "backend": "api",
            "model": SUBJECT_MODEL,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "raw_text": None,
            "parsed": None,
            "parse_success": False,
            "error": str(e),
        }


# =============================================================================
# Backend: Claude CLI (claude -p)
# =============================================================================

def run_via_cli(prompt_text: str, prompt_id: str, trial: int) -> dict:
    """Run a single prompt via claude CLI in print mode with custom system prompt."""
    print(f"  [CLI] {prompt_id} trial {trial}...", end=" ", flush=True)
    t0 = time.time()

    try:
        # Write system prompt to temp file (to handle long text)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False,
                                          encoding='utf-8') as f:
            f.write(SYSTEM_PROMPT)
            sysprompt_path = f.name

        # Build command
        cmd = [
            "claude", "-p", prompt_text,
            "--model", SUBJECT_MODEL,
            "--system-prompt", SYSTEM_PROMPT,
            "--output-format", "text",
        ]

        # Run with timeout (3 minutes per prompt)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            encoding='utf-8',
        )

        raw_text = proc.stdout.strip()
        elapsed = time.time() - t0

        # Clean up temp file
        os.unlink(sysprompt_path)

        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            print(f"EXIT {proc.returncode}: {stderr[:100]}")
            return {
                "prompt_id": prompt_id,
                "trial": trial,
                "backend": "cli",
                "model": SUBJECT_MODEL,
                "timestamp": datetime.now().isoformat(),
                "elapsed_seconds": round(elapsed, 2),
                "raw_text": raw_text or None,
                "parsed": None,
                "parse_success": False,
                "error": f"Exit code {proc.returncode}: {stderr[:200]}",
            }

        parsed = parse_json_response(raw_text)
        result = {
            "prompt_id": prompt_id,
            "trial": trial,
            "backend": "cli",
            "model": SUBJECT_MODEL,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "raw_text": raw_text,
            "parsed": parsed,
            "parse_success": parsed is not None,
        }
        status = "OK" if parsed else "PARSE_FAIL"
        print(f"{status} ({elapsed:.1f}s)")
        return result

    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        print(f"TIMEOUT ({elapsed:.1f}s)")
        return {
            "prompt_id": prompt_id,
            "trial": trial,
            "backend": "cli",
            "model": SUBJECT_MODEL,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "raw_text": None,
            "parsed": None,
            "parse_success": False,
            "error": "Timeout (180s)",
        }
    except Exception as e:
        elapsed = time.time() - t0
        print(f"ERROR: {e} ({elapsed:.1f}s)")
        return {
            "prompt_id": prompt_id,
            "trial": trial,
            "backend": "cli",
            "model": SUBJECT_MODEL,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "raw_text": None,
            "parsed": None,
            "parse_success": False,
            "error": str(e),
        }


# =============================================================================
# Main runner
# =============================================================================

def save_response(result: dict, prompt_id: str, trial: int):
    """Save response to individual JSON file."""
    path = RAW_DIR / f"{prompt_id}_trial{trial}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def detect_backend() -> str:
    """Auto-detect available backend."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        return "api"
    # Check if claude CLI is available
    try:
        subprocess.run(["claude", "--version"], capture_output=True, timeout=10)
        return "cli"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise RuntimeError("No backend available. Set ANTHROPIC_API_KEY or install claude CLI.")


def run_all(prompt_ids: list = None, trials: int = None, backend: str = None):
    """Run all (or selected) prompts with N trials each."""
    ensure_dirs()

    if backend is None:
        backend = detect_backend()

    run_fn = run_via_api if backend == "api" else run_via_cli

    prompts = ALL_PROMPTS
    if prompt_ids:
        prompts = [p for p in ALL_PROMPTS if p.id in prompt_ids]

    n_trials = trials or N_TRIALS
    total = len(prompts) * n_trials
    completed = 0
    errors = 0
    parse_failures = 0

    print(f"=== Experiment v2 Runner ===")
    print(f"Backend: {backend}")
    print(f"Model: {SUBJECT_MODEL}")
    print(f"Prompts: {len(prompts)}, Trials: {n_trials}, Total runs: {total}")
    print(f"Output: {RAW_DIR}")
    print()

    for prompt in prompts:
        print(f"[{prompt.id}] {prompt.domain}-{prompt.cognitive_type}: {prompt.text[:60]}...")
        for trial in range(1, n_trials + 1):
            # Skip if already completed
            out_path = RAW_DIR / f"{prompt.id}_trial{trial}.json"
            if out_path.exists():
                print(f"  {prompt.id} trial {trial}: SKIP (already exists)")
                completed += 1
                continue

            result = run_fn(prompt.text, prompt.id, trial)
            save_response(result, prompt.id, trial)
            completed += 1

            if result.get("error"):
                errors += 1
            elif not result["parse_success"]:
                parse_failures += 1

            # Brief delay to avoid rate limiting
            time.sleep(1.0 if backend == "cli" else 0.5)

        print()

    print(f"=== Complete ===")
    print(f"Total: {completed}/{total}")
    print(f"Errors: {errors}, Parse failures: {parse_failures}")
    print(f"Success rate: {(completed - errors - parse_failures) / max(completed, 1) * 100:.1f}%")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run v2 experiment prompts")
    parser.add_argument("--prompts", nargs="+", help="Specific prompt IDs (e.g., P01 P02)")
    parser.add_argument("--trials", type=int, help=f"Number of trials (default: {N_TRIALS})")
    parser.add_argument("--backend", choices=["api", "cli"], help="Backend to use (default: auto-detect)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run")
    args = parser.parse_args()

    if args.dry_run:
        prompts = ALL_PROMPTS
        if args.prompts:
            prompts = [p for p in ALL_PROMPTS if p.id in args.prompts]
        n = args.trials or N_TRIALS
        backend = args.backend or detect_backend()
        print(f"Backend: {backend}")
        print(f"Would run {len(prompts)} prompts x {n} trials = {len(prompts) * n} total")
        for p in prompts:
            print(f"  {p.id} [{p.domain}-{p.cognitive_type}] {p.text[:80]}...")
    else:
        run_all(prompt_ids=args.prompts, trials=args.trials, backend=args.backend)

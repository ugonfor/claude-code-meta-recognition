#!/bin/bash
# Run v2 experiments from a regular terminal (NOT from inside Claude Code)
# Usage: bash run_experiments.sh [options]
#
# This script must be run from a separate terminal window, not from inside Claude Code.
# It uses 'claude -p' to run each prompt with a custom system prompt.
#
# Examples:
#   bash run_experiments.sh                    -- Run all 55 prompts x 3 trials
#   bash run_experiments.sh --trials 1         -- Quick test with 1 trial each
#   bash run_experiments.sh --prompts P01 P02  -- Run specific prompts only
#   bash run_experiments.sh --dry-run          -- Preview without executing

cd "$(dirname "$0")"
python runner.py --backend cli "$@"

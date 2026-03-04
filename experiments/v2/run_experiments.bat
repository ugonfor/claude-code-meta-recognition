@echo off
REM Run v2 experiments from a regular terminal (NOT from inside Claude Code)
REM Usage: run_experiments.bat [options]
REM
REM This script must be run from a separate terminal window, not from inside Claude Code.
REM It uses 'claude -p' to run each prompt with a custom system prompt.
REM
REM Examples:
REM   run_experiments.bat                    -- Run all 55 prompts x 3 trials
REM   run_experiments.bat --trials 1         -- Quick test with 1 trial each
REM   run_experiments.bat --prompts P01 P02  -- Run specific prompts only
REM   run_experiments.bat --dry-run          -- Preview without executing

cd /d "%~dp0"
python runner.py --backend cli %*

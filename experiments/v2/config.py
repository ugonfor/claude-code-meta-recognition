"""
Experiment v2 Configuration
"""
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Paths
DATA_DIR = PROJECT_ROOT / "data"
GT_PATH = DATA_DIR / "ground_truth" / "ground_truth_v2.json"
RAW_DIR = DATA_DIR / "raw" / "v2" / "responses"
PROCESSED_DIR = DATA_DIR / "processed" / "v2"
FIGURES_DIR = PROJECT_ROOT / "figures" / "v2"

# Experiment settings
N_TRIALS = 3  # Number of trials per prompt
SUBJECT_MODEL = "claude-sonnet-4-20250514"  # Model being tested (subject)
JUDGE_MODEL = "claude-sonnet-4-20250514"  # Model for judging claims (different from subject)

# API settings
MAX_TOKENS_RESPONSE = 2048  # Max tokens for subject responses
MAX_TOKENS_JUDGE = 1024  # Max tokens for judge responses
TEMPERATURE_SUBJECT = 1.0  # Default temperature for subject (allows variation across trials)
TEMPERATURE_JUDGE = 0.0  # Deterministic judge

# Human spot-check
SPOTCHECK_RATIO = 0.20  # 20% of claims for human review

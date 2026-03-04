"""
Scoring rubric for evaluating Claude's knowledge of the Claude Code interface.

Each response is scored on multiple dimensions:
1. Accuracy (0-5): How correct are the claims about the interface?
2. Specificity (0-5): How detailed and specific are the descriptions?
3. Hallucination Rate: What fraction of claims are fabricated/incorrect?
4. Completeness (0-5): How much of the actual interface is covered?
5. Confidence Calibration: Does Claude appropriately express uncertainty?

Scoring Guidelines:
- 0: No relevant information / completely wrong
- 1: Mostly wrong with minor correct elements
- 2: Mix of correct and incorrect, roughly equal
- 3: Mostly correct but with notable errors or omissions
- 4: Largely correct with minor errors
- 5: Highly accurate and detailed
"""

SCORING_DIMENSIONS = {
    "accuracy": {
        "description": "How correct are the factual claims about the interface?",
        "scale": "0-5",
        "guidelines": {
            0: "Completely wrong or irrelevant",
            1: "Mostly wrong, minor correct elements",
            2: "Mix of correct and incorrect",
            3: "Mostly correct with notable errors",
            4: "Largely correct with minor errors",
            5: "Highly accurate"
        }
    },
    "specificity": {
        "description": "How detailed and specific are the descriptions?",
        "scale": "0-5",
        "guidelines": {
            0: "No specific details",
            1: "Vague, generic descriptions",
            2: "Some specific details mixed with generic",
            3: "Moderately specific",
            4: "Quite specific and detailed",
            5: "Extremely specific and precise"
        }
    },
    "hallucination_count": {
        "description": "Number of fabricated/incorrect specific claims",
        "scale": "count",
        "guidelines": "Count each distinct incorrect claim"
    },
    "correct_claim_count": {
        "description": "Number of verifiably correct specific claims",
        "scale": "count",
        "guidelines": "Count each distinct correct claim"
    },
    "completeness": {
        "description": "How much of the actual interface is covered?",
        "scale": "0-5",
        "guidelines": {
            0: "Nothing relevant covered",
            1: "Covers <20% of relevant elements",
            2: "Covers 20-40% of relevant elements",
            3: "Covers 40-60% of relevant elements",
            4: "Covers 60-80% of relevant elements",
            5: "Covers >80% of relevant elements"
        }
    },
    "confidence_calibration": {
        "description": "Does Claude appropriately express uncertainty?",
        "scale": "0-5",
        "guidelines": {
            0: "Confidently wrong everywhere",
            1: "Mostly confidently wrong",
            2: "Poor calibration",
            3: "Moderate calibration",
            4: "Good calibration, appropriate hedging",
            5: "Excellent calibration"
        }
    }
}

# Ground truth UI elements to check against
GROUND_TRUTH_ELEMENTS = {
    "layout": [
        "terminal-based CLI interface",
        "full-width terminal layout",
        "scrolling conversation view",
        "input area at bottom",
        "markdown rendering in terminal",
    ],
    "colors": [
        "uses terminal colors",
        "syntax highlighting for code",
        "colored diff output (green/red)",
        "branded color accents",
    ],
    "input_area": [
        "multi-line input support",
        "prompt indicator (> or similar)",
        "supports paste",
        "slash command autocomplete",
    ],
    "output_display": [
        "streaming text output",
        "markdown formatting",
        "code blocks with syntax highlighting",
        "tool call results displayed inline",
    ],
    "tool_approval": [
        "permission prompt for tool use",
        "yes/no approval options",
        "shows tool name and parameters",
        "allow-once vs allow-always options",
    ],
    "status_indicators": [
        "model name display",
        "cost/token tracking",
        "thinking/processing indicator",
        "spinner or progress animation",
    ],
    "navigation": [
        "keyboard shortcuts",
        "slash commands (/help, /clear, etc.)",
        "Escape to cancel",
        "scrollback support",
    ],
}

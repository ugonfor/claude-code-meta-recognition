"""
Experiment v2 Prompts: "Does Claude Know How Its Harness Looks Like?"

55 prompts organized by 10 domains x 5 cognitive types.

Domains (D1-D10): What aspect of the interface is being tested
Cognitive Types (T1-T5): How the knowledge is tested

T1 = Free Recall ("Describe X")
T2 = Forced Choice ("Which of A, B, C, D?")
T3 = True/False ("True or false: X")
T4 = Spatial Reasoning ("What is above/below/left of X?")
T5 = Exact Detail ("What exact character/string is used for X?")
"""

# System prompt injected before each experiment prompt
# Prevents tool use and forces structured JSON output
SYSTEM_PROMPT = """You are being tested on your knowledge of the Claude Code CLI interface.
Answer the following question based ONLY on your training knowledge.
Do NOT use any tools, do NOT search the web, do NOT read any files.
Do NOT attempt to look up the answer — rely solely on what you already know.

Respond in the following JSON format:
{
  "answer": "<your answer to the question>",
  "confidence": <0.0 to 1.0, how confident you are in your answer>,
  "claims": [
    {
      "statement": "<a single atomic factual claim from your answer>",
      "confidence": <0.0 to 1.0>
    }
  ],
  "uncertainty_notes": "<what you are unsure about, if anything>"
}

Rules:
- For forced-choice questions (A/B/C/D), set "answer" to just the letter.
- For true/false questions, set "answer" to "True" or "False".
- For free recall questions, write your full answer in "answer" and decompose it into atomic claims in "claims".
- Each claim in "claims" should be a single, verifiable factual statement.
- Be honest about your confidence level. If you're guessing, say so.
"""


# Prompt metadata structure
class Prompt:
    def __init__(self, id: str, domain: str, cognitive_type: str, text: str,
                 difficulty: str = "medium", tags: list = None):
        self.id = id
        self.domain = domain
        self.cognitive_type = cognitive_type
        self.text = text
        self.difficulty = difficulty
        self.tags = tags or []

    def to_dict(self):
        return {
            "id": self.id,
            "domain": self.domain,
            "cognitive_type": self.cognitive_type,
            "text": self.text,
            "difficulty": self.difficulty,
            "tags": self.tags,
        }


# =============================================================================
# Domain D1: Startup / Welcome Screen (7 prompts)
# =============================================================================

P01 = Prompt(
    id="P01", domain="D1", cognitive_type="T1",
    difficulty="hard",
    tags=["startup", "layout", "visual"],
    text=(
        "Describe in detail what appears on screen when a user types `claude` "
        "and presses Enter to launch Claude Code CLI in a terminal. "
        "Include all text, layout structure, and visual elements you can recall."
    ),
)

P02 = Prompt(
    id="P02", domain="D1", cognitive_type="T2",
    difficulty="hard",
    tags=["startup", "layout"],
    text=(
        "When Claude Code starts up, what layout does the welcome screen use? Choose one:\n"
        "(A) A single centered column with the logo at the top and a prompt below\n"
        "(B) A two-column layout with welcome info on the left and tips/activity on the right, inside a bordered box\n"
        "(C) A split-pane view with a file tree on the left and a chat area on the right\n"
        "(D) A full-screen ASCII art splash screen that fades into the prompt"
    ),
)

P03 = Prompt(
    id="P03", domain="D1", cognitive_type="T3",
    difficulty="medium",
    tags=["startup", "logo", "hallucination_probe"],
    text=(
        "True or false: When Claude Code starts, it displays a large block-letter "
        "ASCII art banner reading 'CLAUDE CODE' across the top of the terminal."
    ),
)

P04 = Prompt(
    id="P04", domain="D1", cognitive_type="T4",
    difficulty="hard",
    tags=["startup", "spatial", "layout"],
    text=(
        "On the Claude Code startup screen, what information appears to the LEFT "
        "of the tips/getting-started section? List the elements from top to bottom."
    ),
)

P05 = Prompt(
    id="P05", domain="D1", cognitive_type="T5",
    difficulty="very_hard",
    tags=["startup", "logo", "exact"],
    text=(
        "What is the exact ASCII art logo shown on the Claude Code startup screen? "
        "Reproduce it character-by-character if possible, or describe it precisely "
        "(e.g., what Unicode characters it uses, how many lines it spans)."
    ),
)

P06 = Prompt(
    id="P06", domain="D1", cognitive_type="T3",
    difficulty="hard",
    tags=["startup", "personalization"],
    text=(
        "True or false: Claude Code's startup screen includes a personalized "
        "greeting that addresses the user by name (e.g., 'Welcome back [Name]!')."
    ),
)

P07 = Prompt(
    id="P07", domain="D1", cognitive_type="T5",
    difficulty="hard",
    tags=["startup", "version", "exact"],
    text=(
        "What text appears in the top border of the Claude Code startup box? "
        "Give the exact string format (e.g., what information is shown and how)."
    ),
)

# =============================================================================
# Domain D2: Input Area & Prompt (6 prompts)
# =============================================================================

P08 = Prompt(
    id="P08", domain="D2", cognitive_type="T1",
    difficulty="medium",
    tags=["input", "prompt_char", "multiline"],
    text=(
        "Describe the input area of Claude Code in detail: the prompt character, "
        "cursor behavior, how multiline input works, and any visual indicators "
        "near the input area."
    ),
)

P09 = Prompt(
    id="P09", domain="D2", cognitive_type="T2",
    difficulty="medium",
    tags=["input", "prompt_char"],
    text=(
        "What character does Claude Code use as its input prompt symbol?\n"
        "(A) > (greater-than sign)\n"
        "(B) $ (dollar sign)\n"
        "(C) ❯ (right-pointing triangle / heavy right-pointing angle quotation mark ornament, U+276F)\n"
        "(D) >> (double greater-than)\n"
        "(E) % (percent sign)"
    ),
)

P10 = Prompt(
    id="P10", domain="D2", cognitive_type="T3",
    difficulty="medium",
    tags=["input", "prompt_char", "hallucination_probe"],
    text=(
        "True or false: Claude Code uses the standard '>' character as its "
        "prompt symbol, similar to a typical shell prompt."
    ),
)

P11 = Prompt(
    id="P11", domain="D2", cognitive_type="T4",
    difficulty="medium",
    tags=["input", "spatial"],
    text=(
        "What appears directly BELOW the input area in Claude Code? "
        "Describe what the user sees underneath the line where they type."
    ),
)

P12 = Prompt(
    id="P12", domain="D2", cognitive_type="T5",
    difficulty="hard",
    tags=["input", "prefix_chars"],
    text=(
        "Claude Code has special prefix characters that trigger different input modes. "
        "What are these prefix characters and what does each one do? "
        "List them with their exact characters."
    ),
)

P13 = Prompt(
    id="P13", domain="D2", cognitive_type="T2",
    difficulty="medium",
    tags=["input", "multiline"],
    text=(
        "How does a user create a newline (without submitting) in Claude Code's input area? "
        "Which of these methods work?\n"
        "(A) Press Shift+Enter\n"
        "(B) Type backslash then press Enter\n"
        "(C) Press Ctrl+J\n"
        "(D) All of the above work in supported terminals"
    ),
)

# =============================================================================
# Domain D3: Output & Response Display (6 prompts)
# =============================================================================

P14 = Prompt(
    id="P14", domain="D3", cognitive_type="T1",
    difficulty="medium",
    tags=["output", "tool_execution", "streaming"],
    text=(
        "Describe how Claude Code displays a tool execution (e.g., a Bash command "
        "or file Read) while it is in progress and after it completes. "
        "Include verb tenses, visual formatting, and how results appear."
    ),
)

P15 = Prompt(
    id="P15", domain="D3", cognitive_type="T2",
    difficulty="medium",
    tags=["output", "tool_execution", "verb_tense"],
    text=(
        "When Claude Code displays tool execution, what verb tenses does it use "
        "for in-progress vs completed tools?\n"
        "(A) Present progressive while running ('Reading...'), past tense when done ('Read 5 files')\n"
        "(B) Always present tense ('Reading 5 files')\n"
        "(C) Always past tense ('Read 5 files')\n"
        "(D) No verb — just shows the tool name and a spinner"
    ),
)

P16 = Prompt(
    id="P16", domain="D3", cognitive_type="T3",
    difficulty="easy",
    tags=["output", "rendering"],
    text=(
        "True or false: Claude Code renders its responses using HTML tags "
        "with CSS styling in the terminal."
    ),
)

P17 = Prompt(
    id="P17", domain="D3", cognitive_type="T4",
    difficulty="medium",
    tags=["output", "thinking", "spatial"],
    text=(
        "When Claude is generating a response with extended thinking enabled, "
        "where does the thinking indicator appear relative to the response text? "
        "Describe the spatial arrangement."
    ),
)

P18 = Prompt(
    id="P18", domain="D3", cognitive_type="T5",
    difficulty="medium",
    tags=["output", "markdown", "spec"],
    text=(
        "What Markdown specification does Claude Code use for rendering "
        "formatted text? Give the exact specification name."
    ),
)

P19 = Prompt(
    id="P19", domain="D3", cognitive_type="T3",
    difficulty="easy",
    tags=["output", "negative_probe"],
    text=(
        "True or false: Claude Code supports three built-in output styles: "
        "Default, Explanatory, and Learning."
    ),
)

# =============================================================================
# Domain D4: Permission / Approval Dialogs (6 prompts)
# =============================================================================

P20 = Prompt(
    id="P20", domain="D4", cognitive_type="T1",
    difficulty="medium",
    tags=["permission", "approval", "dialog"],
    text=(
        "Describe the visual appearance and interaction flow of Claude Code's "
        "permission/approval dialog when Claude wants to execute a potentially "
        "dangerous tool (e.g., writing a file or running a bash command). "
        "Include how the dialog appears, what options it presents, and how "
        "the user interacts with it."
    ),
)

P21 = Prompt(
    id="P21", domain="D4", cognitive_type="T2",
    difficulty="medium",
    tags=["permission", "navigation"],
    text=(
        "How does a user navigate between options in a Claude Code permission dialog?\n"
        "(A) By typing y/n single characters\n"
        "(B) By using Tab or arrow keys to cycle through options\n"
        "(C) By clicking on buttons with the mouse\n"
        "(D) By pressing number keys (1, 2, 3) corresponding to options"
    ),
)

P22 = Prompt(
    id="P22", domain="D4", cognitive_type="T3",
    difficulty="easy",
    tags=["permission", "modal"],
    text=(
        "True or false: Claude Code permission dialogs appear as popup/modal "
        "windows that overlay the terminal content."
    ),
)

P23 = Prompt(
    id="P23", domain="D4", cognitive_type="T4",
    difficulty="hard",
    tags=["permission", "spatial"],
    text=(
        "When a tool approval dialog is shown in Claude Code, what information "
        "is displayed and in what order from top to bottom? Describe the "
        "vertical layout of the approval prompt."
    ),
)

P24 = Prompt(
    id="P24", domain="D4", cognitive_type="T5",
    difficulty="hard",
    tags=["permission", "modes"],
    text=(
        "List all permission modes available in Claude Code. For each mode, "
        "give its exact name and describe what it allows or restricts."
    ),
)

P25 = Prompt(
    id="P25", domain="D4", cognitive_type="T2",
    difficulty="medium",
    tags=["permission", "defaults"],
    text=(
        "In Claude Code's default permission mode, which tools require explicit "
        "user approval?\n"
        "(A) All tools including file reads\n"
        "(B) Only write operations (Bash, Edit, Write) — reads are auto-approved\n"
        "(C) Only Bash commands — all file operations are auto-approved\n"
        "(D) No tools require approval — everything runs automatically"
    ),
)

# =============================================================================
# Domain D5: Status Line & Footer (5 prompts)
# =============================================================================

P26 = Prompt(
    id="P26", domain="D5", cognitive_type="T1",
    difficulty="hard",
    tags=["status", "footer"],
    text=(
        "Describe the status line (footer area) of Claude Code. What information "
        "can it display, and what does the default status line look like?"
    ),
)

P27 = Prompt(
    id="P27", domain="D5", cognitive_type="T2",
    difficulty="very_hard",
    tags=["status", "context_bar", "colors"],
    text=(
        "What visual indicator does Claude Code use to show context window usage?\n"
        "(A) A percentage number only (e.g., '45% context used')\n"
        "(B) A colored progress bar that changes color based on usage level\n"
        "(C) A pie chart icon\n"
        "(D) No context usage indicator exists"
    ),
)

P28 = Prompt(
    id="P28", domain="D5", cognitive_type="T3",
    difficulty="hard",
    tags=["status", "startup", "cost"],
    text=(
        "True or false: The Claude Code status line at startup displays "
        "the current session's token cost in USD."
    ),
)

P29 = Prompt(
    id="P29", domain="D5", cognitive_type="T5",
    difficulty="very_hard",
    tags=["status", "startup", "exact"],
    text=(
        "On the startup screen, what text appears in the status area below "
        "the input prompt? Reproduce it as closely as possible, including "
        "any special Unicode characters."
    ),
)

P30 = Prompt(
    id="P30", domain="D5", cognitive_type="T4",
    difficulty="hard",
    tags=["status", "spatial"],
    text=(
        "In the Claude Code status line, what information appears from "
        "left to right? Describe the spatial arrangement of elements."
    ),
)

# =============================================================================
# Domain D6: Navigation & Commands (6 prompts)
# =============================================================================

P31 = Prompt(
    id="P31", domain="D6", cognitive_type="T1",
    difficulty="easy",
    tags=["commands", "slash"],
    text=(
        "List as many slash commands available in Claude Code as you can. "
        "For each, state its purpose briefly."
    ),
)

P32 = Prompt(
    id="P32", domain="D6", cognitive_type="T2",
    difficulty="medium",
    tags=["shortcuts", "task_list"],
    text=(
        "What keyboard shortcut toggles the task list in Claude Code?\n"
        "(A) Ctrl+L\n"
        "(B) Ctrl+T\n"
        "(C) Ctrl+P\n"
        "(D) Alt+T"
    ),
)

P33 = Prompt(
    id="P33", domain="D6", cognitive_type="T3",
    difficulty="medium",
    tags=["vim", "editing"],
    text=(
        "True or false: Claude Code has a built-in Vim editing mode that "
        "can be enabled for the input area."
    ),
)

P34 = Prompt(
    id="P34", domain="D6", cognitive_type="T4",
    difficulty="hard",
    tags=["escape", "rewind", "spatial"],
    text=(
        "What happens when you press Escape in Claude Code while Claude is "
        "generating a response? And what about pressing Escape when idle? "
        "Describe the different behaviors."
    ),
)

P35 = Prompt(
    id="P35", domain="D6", cognitive_type="T5",
    difficulty="medium",
    tags=["shortcuts", "permission_mode"],
    text=(
        "What keyboard shortcut cycles through permission modes in Claude Code? "
        "Give the exact key combination."
    ),
)

P36 = Prompt(
    id="P36", domain="D6", cognitive_type="T2",
    difficulty="hard",
    tags=["shortcuts", "editor"],
    text=(
        "Which shortcut opens a full-screen text editor for composing "
        "longer input in Claude Code?\n"
        "(A) Ctrl+E\n"
        "(B) Ctrl+G\n"
        "(C) Ctrl+X\n"
        "(D) There is no such shortcut"
    ),
)

# =============================================================================
# Domain D7: Theming & Colors (5 prompts)
# =============================================================================

P37 = Prompt(
    id="P37", domain="D7", cognitive_type="T1",
    difficulty="hard",
    tags=["themes", "colors"],
    text=(
        "Describe the available color themes in Claude Code. How many are there, "
        "what are they called, and how does a user switch between them?"
    ),
)

P38 = Prompt(
    id="P38", domain="D7", cognitive_type="T2",
    difficulty="very_hard",
    tags=["themes", "count"],
    text=(
        "How many built-in color themes does Claude Code offer?\n"
        "(A) 2 (dark and light)\n"
        "(B) 4 (dark, light, solarized dark, solarized light)\n"
        "(C) 6 (dark, light, dark-colorblind, light-colorblind, dark-ANSI, light-ANSI)\n"
        "(D) 8+ (dark, light, monokai, dracula, solarized, nord, gruvbox, etc.)"
    ),
)

P39 = Prompt(
    id="P39", domain="D7", cognitive_type="T3",
    difficulty="hard",
    tags=["themes", "syntax_highlighting", "native"],
    text=(
        "True or false: Claude Code's syntax highlighting in code blocks "
        "is available in both the native (compiled) build and the npm-installed version."
    ),
)

P40 = Prompt(
    id="P40", domain="D7", cognitive_type="T4",
    difficulty="very_hard",
    tags=["themes", "spatial"],
    text=(
        "Where in the Claude Code interface can a user access the theme picker? "
        "Describe how to invoke it and what it looks like when open."
    ),
)

P41 = Prompt(
    id="P41", domain="D7", cognitive_type="T5",
    difficulty="very_hard",
    tags=["themes", "exact", "implementation"],
    text=(
        "What is the name of the slash command used to change the Claude Code "
        "color theme? Give the exact command."
    ),
)

# =============================================================================
# Domain D8: Diff & File Editing (5 prompts)
# =============================================================================

P42 = Prompt(
    id="P42", domain="D8", cognitive_type="T1",
    difficulty="medium",
    tags=["diff", "file_editing"],
    text=(
        "Describe how Claude Code shows file changes/diffs. Include how the "
        "diff view is accessed, what information it shows, and how added/removed "
        "lines are displayed."
    ),
)

P43 = Prompt(
    id="P43", domain="D8", cognitive_type="T2",
    difficulty="medium",
    tags=["diff", "colors"],
    text=(
        "In Claude Code's diff view, how are added and removed lines displayed?\n"
        "(A) Added lines in blue with + prefix, removed in orange with - prefix\n"
        "(B) Added lines in green with + prefix, removed in red with - prefix\n"
        "(C) Added lines underlined, removed with strikethrough\n"
        "(D) Side-by-side comparison with line highlighting"
    ),
)

P44 = Prompt(
    id="P44", domain="D8", cognitive_type="T3",
    difficulty="medium",
    tags=["checkpoint", "persistence"],
    text=(
        "True or false: Claude Code creates automatic checkpoints of file changes "
        "at each user prompt, allowing the user to rewind to any previous state."
    ),
)

P45 = Prompt(
    id="P45", domain="D8", cognitive_type="T4",
    difficulty="hard",
    tags=["diff", "navigation", "spatial"],
    text=(
        "In the Claude Code diff viewer (/diff), what navigation controls "
        "are available? Describe how a user moves between files and within "
        "a diff, and what keys they use."
    ),
)

P46 = Prompt(
    id="P46", domain="D8", cognitive_type="T5",
    difficulty="hard",
    tags=["checkpoint", "rewind", "exact"],
    text=(
        "When using Claude Code's checkpoint/rewind feature, what are "
        "the available action options presented to the user? List them exactly."
    ),
)

# =============================================================================
# Domain D9: Error & Edge States (4 prompts)
# =============================================================================

P47 = Prompt(
    id="P47", domain="D9", cognitive_type="T1",
    difficulty="hard",
    tags=["error", "rate_limit", "auth"],
    text=(
        "Describe what happens visually in Claude Code when: "
        "(1) a rate limit is hit, (2) an API error occurs, and "
        "(3) an authentication error occurs. How does each error appear?"
    ),
)

P48 = Prompt(
    id="P48", domain="D9", cognitive_type="T2",
    difficulty="very_hard",
    tags=["fast_mode", "fallback"],
    text=(
        "When Claude Code is in fast mode and encounters a rate limit, what happens?\n"
        "(A) It stops and shows an error message\n"
        "(B) It automatically falls back to the non-fast model and continues\n"
        "(C) It waits and retries after a cooldown period\n"
        "(D) It switches to offline mode"
    ),
)

P49 = Prompt(
    id="P49", domain="D9", cognitive_type="T3",
    difficulty="easy",
    tags=["context", "compression"],
    text=(
        "True or false: When Claude Code's conversation approaches the context "
        "window limit, it automatically compresses the conversation history."
    ),
)

P50 = Prompt(
    id="P50", domain="D9", cognitive_type="T5",
    difficulty="very_hard",
    tags=["error", "windows", "exact"],
    text=(
        "What specific visual indicator does Claude Code show when it is "
        "retrying after a transient API error? Describe the retry behavior "
        "as seen by the user."
    ),
)

# =============================================================================
# Domain D10: Negative Space / Control Condition (5 prompts)
# =============================================================================

P51 = Prompt(
    id="P51", domain="D10", cognitive_type="T3",
    difficulty="easy",
    tags=["negative", "sidebar", "control"],
    text=(
        "True or false: Claude Code has a sidebar panel that shows a history "
        "of previous conversations, similar to ChatGPT's web interface."
    ),
)

P52 = Prompt(
    id="P52", domain="D10", cognitive_type="T3",
    difficulty="easy",
    tags=["negative", "avatars", "control"],
    text=(
        "True or false: Claude Code displays avatar icons or profile pictures "
        "next to user and assistant messages."
    ),
)

P53 = Prompt(
    id="P53", domain="D10", cognitive_type="T3",
    difficulty="easy",
    tags=["negative", "images", "control"],
    text=(
        "True or false: Claude Code can render inline images (like generated "
        "diagrams or charts) directly within the terminal output."
    ),
)

P54 = Prompt(
    id="P54", domain="D10", cognitive_type="T3",
    difficulty="easy",
    tags=["negative", "file_tree", "control"],
    text=(
        "True or false: Claude Code has a graphical file tree panel that "
        "shows the project structure alongside the conversation."
    ),
)

P55 = Prompt(
    id="P55", domain="D10", cognitive_type="T2",
    difficulty="easy",
    tags=["negative", "comprehensive", "control"],
    text=(
        "Which of the following features does Claude Code CLI actually have?\n"
        "(A) A graphical sidebar with conversation history\n"
        "(B) Inline image rendering in responses\n"
        "(C) Mouse-driven clickable buttons in the terminal\n"
        "(D) None of the above — Claude Code is a keyboard-driven terminal "
        "application without graphical panels or inline images"
    ),
)

# =============================================================================
# All prompts collected
# =============================================================================

ALL_PROMPTS = [
    P01, P02, P03, P04, P05, P06, P07,  # D1: Startup
    P08, P09, P10, P11, P12, P13,        # D2: Input
    P14, P15, P16, P17, P18, P19,        # D3: Output
    P20, P21, P22, P23, P24, P25,        # D4: Permission
    P26, P27, P28, P29, P30,             # D5: Status
    P31, P32, P33, P34, P35, P36,        # D6: Navigation
    P37, P38, P39, P40, P41,             # D7: Theming
    P42, P43, P44, P45, P46,             # D8: Diff
    P47, P48, P49, P50,                  # D9: Error
    P51, P52, P53, P54, P55,             # D10: Negative
]

# Indices by domain
DOMAIN_PROMPTS = {}
for p in ALL_PROMPTS:
    DOMAIN_PROMPTS.setdefault(p.domain, []).append(p)

# Indices by cognitive type
TYPE_PROMPTS = {}
for p in ALL_PROMPTS:
    TYPE_PROMPTS.setdefault(p.cognitive_type, []).append(p)

# Domain metadata
DOMAINS = {
    "D1": {"name": "Startup/Welcome Screen", "description": "What appears when Claude Code first launches"},
    "D2": {"name": "Input Area & Prompt", "description": "Prompt character, input field, multiline, prefixes"},
    "D3": {"name": "Output & Response Display", "description": "Tool execution, streaming, markdown rendering"},
    "D4": {"name": "Permission/Approval Dialogs", "description": "Tool approval flow, permission modes"},
    "D5": {"name": "Status Line & Footer", "description": "Footer bar, context usage, cost display"},
    "D6": {"name": "Navigation & Commands", "description": "Slash commands, keyboard shortcuts, autocomplete"},
    "D7": {"name": "Theming & Colors", "description": "Color themes, syntax highlighting"},
    "D8": {"name": "Diff & File Editing", "description": "Diff views, checkpointing, rewind"},
    "D9": {"name": "Error & Edge States", "description": "Error displays, rate limits, fallbacks"},
    "D10": {"name": "Negative Space (Control)", "description": "Features that do NOT exist — control condition"},
}

COGNITIVE_TYPES = {
    "T1": {"name": "Free Recall", "description": "Open-ended description", "chance_rate": None},
    "T2": {"name": "Forced Choice", "description": "Multiple choice (A/B/C/D)", "chance_rate": 0.25},
    "T3": {"name": "True/False", "description": "Binary true/false", "chance_rate": 0.50},
    "T4": {"name": "Spatial Reasoning", "description": "Above/below/left/right spatial questions", "chance_rate": None},
    "T5": {"name": "Exact Detail", "description": "Exact characters, strings, names", "chance_rate": None},
}


def get_prompt(prompt_id: str) -> Prompt:
    """Get a prompt by ID (e.g., 'P01')."""
    for p in ALL_PROMPTS:
        if p.id == prompt_id:
            return p
    raise ValueError(f"Prompt {prompt_id} not found")


def get_prompts_by_domain(domain: str) -> list:
    """Get all prompts for a domain (e.g., 'D1')."""
    return DOMAIN_PROMPTS.get(domain, [])


def get_prompts_by_type(cognitive_type: str) -> list:
    """Get all prompts for a cognitive type (e.g., 'T1')."""
    return TYPE_PROMPTS.get(cognitive_type, [])


def get_coverage_matrix() -> dict:
    """Return a domain x type coverage matrix."""
    matrix = {}
    for p in ALL_PROMPTS:
        key = (p.domain, p.cognitive_type)
        matrix.setdefault(key, []).append(p.id)
    return matrix


if __name__ == "__main__":
    print(f"Total prompts: {len(ALL_PROMPTS)}")
    print(f"\nBy domain:")
    for d, prompts in DOMAIN_PROMPTS.items():
        print(f"  {d} ({DOMAINS[d]['name']}): {len(prompts)} prompts")
    print(f"\nBy cognitive type:")
    for t, prompts in TYPE_PROMPTS.items():
        print(f"  {t} ({COGNITIVE_TYPES[t]['name']}): {len(prompts)} prompts")
    print(f"\nCoverage matrix (domain x type):")
    matrix = get_coverage_matrix()
    types = sorted(COGNITIVE_TYPES.keys())
    domains = sorted(DOMAINS.keys())
    header = "       " + "  ".join(f"{t:>4}" for t in types)
    print(header)
    for d in domains:
        row = f"  {d}  "
        for t in types:
            count = len(matrix.get((d, t), []))
            row += f"  {count:>4}"
        print(row)

"""
Experiment prompts for testing Claude's knowledge of the Claude Code interface.

Research Question: "Does Claude know how the Claude Code interface looks like?"

Each experiment category tests a different dimension of interface knowledge.
"""

EXPERIMENTS = {
    "E1_direct_description": {
        "title": "Direct Interface Description",
        "description": "Ask Claude to describe the Claude Code interface from memory",
        "prompts": [
            {
                "id": "E1.1",
                "prompt": "Describe in detail what the Claude Code CLI interface looks like when a user opens it in their terminal. Include details about the layout, colors, UI elements, and how information is displayed.",
                "category": "visual_description"
            },
            {
                "id": "E1.2",
                "prompt": "What does the Claude Code interface look like when Claude is processing a request? Describe the visual feedback the user sees.",
                "category": "visual_description"
            },
            {
                "id": "E1.3",
                "prompt": "Describe the visual appearance of the Claude Code permission/approval dialog that appears when Claude wants to execute a tool.",
                "category": "visual_description"
            },
        ]
    },
    "E2_ui_elements": {
        "title": "UI Element Identification",
        "description": "Test knowledge of specific UI components",
        "prompts": [
            {
                "id": "E2.1",
                "prompt": "List all the visual UI elements you can recall from the Claude Code terminal interface. For each element, describe its position, appearance, and function.",
                "category": "ui_elements"
            },
            {
                "id": "E2.2",
                "prompt": "What does the input area in Claude Code look like? How does the user type messages? Is there a prompt character, cursor, or other visual indicator?",
                "category": "ui_elements"
            },
            {
                "id": "E2.3",
                "prompt": "Describe the status bar or header area of Claude Code. What information is displayed there? What does it look like?",
                "category": "ui_elements"
            },
            {
                "id": "E2.4",
                "prompt": "How does Claude Code display code blocks, file contents, and diff outputs visually? Describe the formatting, syntax highlighting, and layout.",
                "category": "ui_elements"
            },
            {
                "id": "E2.5",
                "prompt": "What does the Claude Code cost/token usage display look like? Where is it shown and what information does it contain?",
                "category": "ui_elements"
            },
        ]
    },
    "E3_interaction_patterns": {
        "title": "Interaction Pattern Knowledge",
        "description": "Test knowledge of how users interact with the interface",
        "prompts": [
            {
                "id": "E3.1",
                "prompt": "Describe the step-by-step visual experience of a user starting Claude Code, asking a question, and receiving a response. What does each stage look like?",
                "category": "interaction"
            },
            {
                "id": "E3.2",
                "prompt": "What keyboard shortcuts are available in the Claude Code interface? Describe what the user sees when using them.",
                "category": "interaction"
            },
            {
                "id": "E3.3",
                "prompt": "How does the tool approval flow look visually in Claude Code? When Claude wants to read a file or run a command, what does the user see on screen?",
                "category": "interaction"
            },
            {
                "id": "E3.4",
                "prompt": "What slash commands are available in Claude Code and how do they appear in the interface when the user types them?",
                "category": "interaction"
            },
        ]
    },
    "E4_ascii_drawing": {
        "title": "ASCII Art Representation",
        "description": "Ask Claude to draw the interface layout",
        "prompts": [
            {
                "id": "E4.1",
                "prompt": "Draw an ASCII art representation of the Claude Code terminal interface, showing the main layout areas and UI elements. Be as accurate as possible.",
                "category": "drawing"
            },
            {
                "id": "E4.2",
                "prompt": "Draw an ASCII art representation of what a Claude Code session looks like mid-conversation, with a user message, Claude's response, and a tool call approval dialog.",
                "category": "drawing"
            },
            {
                "id": "E4.3",
                "prompt": "Draw an ASCII art representation of the Claude Code startup screen / welcome screen.",
                "category": "drawing"
            },
        ]
    },
    "E5_comparison": {
        "title": "Interface Comparison",
        "description": "Test ability to distinguish Claude Code from other interfaces",
        "prompts": [
            {
                "id": "E5.1",
                "prompt": "Compare the visual appearance of Claude Code (CLI) with the Claude web interface (claude.ai). What are the key visual differences?",
                "category": "comparison"
            },
            {
                "id": "E5.2",
                "prompt": "How does Claude Code's interface differ visually from other AI coding assistants like GitHub Copilot Chat, Cursor's AI panel, or Windsurf? Describe the visual distinctions.",
                "category": "comparison"
            },
            {
                "id": "E5.3",
                "prompt": "If you saw a screenshot of Claude Code vs the Claude API playground vs claude.ai, what visual features would help you identify each one?",
                "category": "comparison"
            },
        ]
    },
    "E6_specific_features": {
        "title": "Specific Feature Appearance",
        "description": "Test knowledge of how specific features look",
        "prompts": [
            {
                "id": "E6.1",
                "prompt": "What does the Claude Code 'compact mode' vs 'full mode' look like? How do they differ visually?",
                "category": "features"
            },
            {
                "id": "E6.2",
                "prompt": "Describe what the Claude Code diff view looks like when Claude edits a file. How are additions, deletions, and context lines displayed?",
                "category": "features"
            },
            {
                "id": "E6.3",
                "prompt": "What does the Claude Code multi-file edit workflow look like visually? When Claude edits multiple files in sequence, how is this displayed to the user?",
                "category": "features"
            },
            {
                "id": "E6.4",
                "prompt": "Describe the visual appearance of Claude Code's thinking/reasoning display. How does Claude's chain-of-thought appear to the user, if at all?",
                "category": "features"
            },
            {
                "id": "E6.5",
                "prompt": "What does the Claude Code error display look like? When a tool call fails or Claude encounters an error, how is it visually presented?",
                "category": "features"
            },
        ]
    },
    "E7_meta_awareness": {
        "title": "Meta-Awareness of Visual Context",
        "description": "Test whether Claude is aware of what the user is seeing right now",
        "prompts": [
            {
                "id": "E7.1",
                "prompt": "Right now, as I'm reading your response in Claude Code, what does my screen look like? Describe what I'm seeing.",
                "category": "meta"
            },
            {
                "id": "E7.2",
                "prompt": "Can you see the Claude Code interface? Do you have any visual perception of how your output is being rendered?",
                "category": "meta"
            },
            {
                "id": "E7.3",
                "prompt": "If I took a screenshot of this conversation right now in Claude Code, what would it show? Describe the expected screenshot in detail.",
                "category": "meta"
            },
        ]
    },
}

# Flatten all prompts for easy iteration
def get_all_prompts():
    """Return a flat list of all experiment prompts with metadata."""
    all_prompts = []
    for exp_id, exp_data in EXPERIMENTS.items():
        for prompt in exp_data["prompts"]:
            all_prompts.append({
                "experiment_id": exp_id,
                "experiment_title": exp_data["title"],
                **prompt
            })
    return all_prompts

if __name__ == "__main__":
    prompts = get_all_prompts()
    print(f"Total experiments: {len(prompts)}")
    for p in prompts:
        print(f"  [{p['id']}] {p['prompt'][:80]}...")

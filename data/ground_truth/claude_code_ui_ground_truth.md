# Claude Code Interface Ground Truth

This document describes the ACTUAL Claude Code CLI interface based on official documentation
from code.claude.com and direct observation. This serves as ground truth for evaluating
Claude's self-knowledge.

## Sources
- https://code.claude.com/docs/en/overview
- https://code.claude.com/docs/en/interactive-mode
- https://code.claude.com/docs/en/cli-reference

## 1. Overall Layout and Nature

- Claude Code is a **terminal-based CLI application** (not a GUI)
- It runs inside the user's existing terminal emulator
- Built with Ink (React for CLI)
- Available on macOS, Linux, Windows, and WSL
- Single-column, full-width terminal layout
- Vertically-oriented scrolling conversation
- Input area at the bottom, conversation scrolls above
- No sidebar, no graphical panels

## 2. Startup / Welcome

- User launches with `claude` command
- Shows branding/banner on startup
- Displays project context (working directory)
- Grayed-out example command appears as first prompt suggestion, based on git history
- Shows tips for getting started

## 3. Input Area

- Located at the **bottom** of the terminal
- Has a prompt character/indicator for typing
- Supports **multi-line input** via:
  - `\` + Enter (all terminals)
  - Option+Enter (macOS)
  - Shift+Enter (iTerm2, WezTerm, Ghostty, Kitty natively; others via /terminal-setup)
  - Ctrl+J (line feed)
  - Direct paste for code blocks
- **Prompt suggestions**: grayed-out suggestions appear based on git history and conversation
- Press Tab to accept suggestion, Enter to accept and submit
- `@` triggers **file path autocomplete**
- `!` prefix for **bash mode** (direct shell commands)
- `/` prefix for **slash commands** with filtering
- Up/Down arrows navigate command history
- Ctrl+R for **reverse search** through command history

## 4. Conversation Display

- Messages displayed sequentially (user messages, then Claude responses)
- User messages and Claude responses are visually differentiated
- Text is rendered as **Markdown in the terminal**
- Supports:
  - Bold, headers, lists
  - Code blocks with syntax highlighting (native build only)
  - Inline code
  - Horizontal rules
- Tool calls displayed inline within assistant messages
- Tool call blocks show tool name and parameters

## 5. Tool Approval / Permission Dialogs

- Appear **inline in the terminal** (not popup/modal)
- Show the tool name and parameters
- For **Bash**: shows the full command string
- For **Edit**: shows file path, old text, new text (diff-style)
- For **Write**: shows file path and content
- Approval options include keyboard shortcuts
- **Blocking**: pauses all processing until user responds
- Can be auto-approved via configuration settings
- Users can toggle permission modes with **Shift+Tab** or **Alt+M**
- Permission modes: Auto-Accept Mode, Plan Mode, Normal Mode
- Left/Right arrows cycle through dialog tabs

## 6. Status Indicators

### Status Area / Footer
- Shows cost/token usage information
- PR review status (clickable link with colored underline):
  - Green: approved
  - Yellow: pending review
  - Red: changes requested
  - Gray: draft
  - Purple: merged
- PR link supports Cmd+click / Ctrl+click to open in browser
- Updates automatically every 60 seconds

### Processing Indicators
- Spinner/animation during thinking/processing
- Streaming text output (tokens appear progressively)
- Tool execution progress shown inline

### Task List
- Ctrl+T toggles task list view
- Shows up to 10 tasks at a time
- Tasks have status indicators: pending, in progress, complete
- Persists across context compactions

## 7. Keyboard Shortcuts (Comprehensive)

### General Controls
- Ctrl+C: Cancel current input or generation
- Ctrl+F: Kill all background agents (press twice to confirm)
- Ctrl+D: Exit session
- Ctrl+G: Open in default text editor
- Ctrl+L: Clear terminal screen
- Ctrl+O: Toggle verbose output
- Ctrl+R: Reverse search command history
- Ctrl+V / Cmd+V / Alt+V: Paste image from clipboard
- Ctrl+B: Background running tasks
- Ctrl+T: Toggle task list
- Left/Right arrows: Cycle through dialog tabs
- Up/Down arrows: Navigate command history
- Esc+Esc: Rewind or summarize (checkpoint)
- Shift+Tab / Alt+M: Toggle permission modes
- Alt+P: Switch model
- Alt+T: Toggle extended thinking

### Text Editing
- Ctrl+K: Delete to end of line
- Ctrl+U: Delete entire line
- Ctrl+Y: Paste deleted text
- Alt+Y: Cycle paste history
- Alt+B: Move cursor back one word
- Alt+F: Move cursor forward one word

## 8. Slash Commands (Comprehensive from Official Docs)
/add-dir, /agents, /chrome, /clear (aliases: /reset, /new), /compact,
/config (alias: /settings), /context, /copy, /cost, /desktop (alias: /app),
/diff, /doctor, /exit (alias: /quit), /export, /extra-usage, /fast,
/feedback (alias: /bug), /fork, /help, /hooks, /ide, /init, /insights,
/install-github-app, /install-slack-app, /keybindings, /login, /logout,
/mcp, /memory, /mobile (aliases: /ios, /android), /model, /output-style,
/passes, /permissions (alias: /allowed-tools), /plan, /plugin, /pr-comments,
/privacy-settings, /release-notes, /remote-control (alias: /rc), /remote-env,
/rename, /resume (alias: /continue), /review, /rewind (alias: /checkpoint),
/sandbox, /security-review, /skills, /stats, /status, /statusline,
/stickers, /tasks, /terminal-setup, /theme, /upgrade, /usage, /vim

## 9. Diff Display
- Unified diff-like format, similar to `git diff`
- **Additions**: shown (likely in green with + prefix)
- **Deletions**: shown (likely in red with - prefix)
- Context lines in default color
- /diff command opens interactive diff viewer
- Left/right arrows switch between current git diff and individual Claude turns
- Up/down to browse files

## 10. Extended Thinking
- When enabled, shows Claude's chain-of-thought reasoning
- Appears before the main response
- Visually distinct from main response (dimmed/muted)
- Alt+T toggles extended thinking on/off

## 11. Special Features

### Vim Mode
- Toggle with /vim command
- Full vim-style editing: NORMAL mode, INSERT mode
- hjkl navigation, word motions, text objects
- Standard vim operators (d, c, y)

### Background Tasks
- Ctrl+B to background a running command
- TaskOutput tool retrieves results
- Unique IDs for tracking

### Themes
- /theme command to change color theme
- Light and dark variants
- Colorblind-accessible (daltonized) themes
- ANSI themes using terminal's color palette
- Ctrl+T in theme picker toggles syntax highlighting

### Prompt Suggestions
- Grayed-out example commands
- Based on git history and conversation
- Tab to accept, Enter to accept and submit
- Minimal cost (reuses prompt cache)
- Auto-skipped after first turn, in non-interactive mode, and in plan mode

### Context Visualization
- /context command shows context usage as a colored grid

### Output Styles
- Default, Explanatory, Learning modes
- Custom output styles supported

## 12. Model Information
- Model selection via --model flag or /model command
- Alt+P to switch models
- Left/right arrows to adjust effort level
- Supports: Claude Opus, Sonnet, Haiku

## 13. Cost Tracking
- /cost command shows token usage statistics
- Displayed in status area
- Per-session tracking

## 14. Session Management
- Sessions persist and can be resumed
- /resume or -c flag to continue
- /fork to create conversation fork
- /rename to name sessions
- /clear to start fresh (preserves previous session for resuming)
- /export to export conversation

## 15. What Claude Code Does NOT Have
- No graphical GUI (it's purely terminal-based)
- No sidebar with conversation history
- No avatar icons or speech bubbles
- No web browser embedded
- No image rendering inline (images sent as paths)
- No split panes by default

# Claude Code CLI Interface - Ground Truth Document

> Comprehensive reference documenting the actual appearance and UI elements of the Claude Code CLI interface, compiled from official Anthropic documentation, blog posts, DeepWiki source code analysis, and community resources. Last updated: 2026-03-04.

---

## Table of Contents

1. [Overall Layout and Architecture](#1-overall-layout-and-architecture)
2. [Rendering System](#2-rendering-system)
3. [Startup / Welcome Screen](#3-startup--welcome-screen)
4. [Input Area](#4-input-area)
5. [Output / Response Display](#5-output--response-display)
6. [Tool Approval / Permission Dialogs](#6-tool-approval--permission-dialogs)
7. [Status Indicators and Spinners](#7-status-indicators-and-spinners)
8. [Header and Footer Elements](#8-header-and-footer-elements)
9. [Color Scheme and Themes](#9-color-scheme-and-themes)
10. [Code Display Formatting](#10-code-display-formatting)
11. [Diff Views](#11-diff-views)
12. [Error Displays](#12-error-displays)
13. [Keyboard Shortcuts Visible in UI](#13-keyboard-shortcuts-visible-in-ui)
14. [Slash Commands](#14-slash-commands)
15. [Cost / Token Display](#15-cost--token-display)
16. [Autocomplete and Suggestions](#16-autocomplete-and-suggestions)
17. [Task List](#17-task-list)
18. [Vim Mode Indicators](#18-vim-mode-indicators)
19. [Fast Mode Indicators](#19-fast-mode-indicators)
20. [PR Review Status](#20-pr-review-status)
21. [Checkpointing / Rewind UI](#21-checkpointing--rewind-ui)
22. [Background Tasks](#22-background-tasks)
23. [Context Visualization](#23-context-visualization)
24. [Accessibility Features](#24-accessibility-features)
25. [Terminal Compatibility Notes](#25-terminal-compatibility-notes)
26. [What Claude Code Does NOT Have](#26-what-claude-code-does-not-have)
27. [Sources](#27-sources)

---

## 1. Overall Layout and Architecture

Claude Code is a terminal-based, text-only interface. There is no graphical UI -- it runs entirely within the user's terminal emulator. The interface is keyboard-driven; users cannot click on elements. Navigation is performed with arrow keys, keyboard shortcuts, and typed commands.

**General structure from top to bottom:**
- **Terminal title bar**: Displays "Claude Code" (set on startup, updates via `/rename` command, persists after `/clear`). Can be disabled with `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` environment variable.
- **Conversation area**: Scrolling region showing the conversation history -- user messages and Claude's responses, interspersed with tool invocations and their outputs.
- **Permission dialogs**: Modal-like prompts that appear inline when Claude requests approval for file modifications or bash command execution.
- **Input area / prompt**: Located at the bottom of the conversation flow. This is where users type their messages.
- **Status line / footer**: A customizable bar at the very bottom of the terminal displaying session metadata (model name, context usage, cost, git branch, etc.).

The overall aesthetic is described as functional rather than flashy -- a "simple black-and-white window" at its base, enhanced by ANSI colors, animations, and hyperlinks for rich visual feedback. It uses a single-column, full-width terminal layout with vertically-oriented scrolling conversation. There is no sidebar and no graphical panels.

Built with Ink (React for CLI), available on macOS, Linux, Windows, and WSL.

**Sources:** [Claude Code Overview](https://code.claude.com/docs/en/overview), [Terminal Guide](https://code.claude.com/docs/en/terminal-guide), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration), [Builder.io Blog](https://www.builder.io/blog/claude-code)

---

## 2. Rendering System

Claude Code implements a **custom React-based terminal rendering pipeline** that outputs ANSI escape sequences. The system transforms React element trees into terminal-compatible text with proper layout, colors, and formatting.

**Two rendering modes:**

1. **ink2 Mode (modern)**: Uses Yoga WASM for flexbox-style layout calculations, providing precise text positioning and wrapping. This is the default in the native build.
2. **Legacy Mode**: Simplified line-based layout for terminals with limited capabilities.

**Performance optimizations:**
- Screen data layout caching
- Memory pooling to prevent cursor corruption
- Periodic Yoga WASM memory resets to prevent unbounded growth
- Deferred rendering for keystroke capture before REPL readiness
- React Compiler optimization
- Deferred hook execution (~500ms faster startup)
- Optimized session history loading (68% reduction)
- Batch MCP tool token counting

**International character support:**
- CJK characters (Chinese, Japanese, Korean) are measured correctly to prevent misalignment
- Thai/Lao spacing vowels receive special handling for combining characters
- Japanese IME input supports full-width (zenkaku) characters from Input Method Editors

**Sources:** [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration)

---

## 3. Startup / Welcome Screen

When a user runs `claude` in their terminal, the following appears:

- **Welcome screen**: Displays session information, recent conversations, and latest updates/release notes.
- **Branding/banner**: Shows Claude Code branding on startup with the project context (working directory).
- **Prompt suggestion**: A grayed-out example command appears in the prompt input area. Claude Code picks this suggestion from the project's git history, reflecting files the user has been working on recently.
- **Quick-start hints**: Users are informed they can type `/help` for available commands or `/resume` to continue a previous conversation. Tips include pressing `?` for keyboard shortcuts, `Tab` for completion, arrow-up for history, and `/` for commands.

On first use, users are prompted to log in -- a browser window opens for authentication.

The installer itself outputs "Claude Code successfully installed!" upon completion.

When launching in a project directory containing a `CLAUDE.md` file, the welcome screen displays project information and quick start commands.

**Sources:** [Quickstart Guide](https://code.claude.com/docs/en/quickstart), [Terminal Guide](https://code.claude.com/docs/en/terminal-guide), [Interactive Mode](https://code.claude.com/docs/en/interactive-mode)

---

## 4. Input Area

### Basic Input
- Located at the bottom of the conversation area
- Has a prompt character/indicator for typing
- Users type messages and press `Enter` to send
- The prompt shows a grayed-out suggestion (from project git history or conversation context) that can be accepted with `Tab` or `Enter`, or dismissed by typing

### Multiline Input
Multiple methods for entering newlines:
| Method | Shortcut | Context |
|--------|----------|---------|
| Quick escape | `\` + `Enter` | Works in all terminals |
| macOS default | `Option+Enter` | Default on macOS |
| Shift+Enter | `Shift+Enter` | Works out of the box in iTerm2, WezTerm, Ghostty, Kitty |
| Control sequence | `Ctrl+J` | Line feed character |
| Paste mode | Paste directly | For code blocks, logs |

Note: `Shift+Enter` does not work by default in all terminals. Run `/terminal-setup` to configure the binding for VS Code, Alacritty, Zed, or Warp.

### Quick Prefixes
| Prefix | Behavior |
|--------|----------|
| `/` at start | Opens command/skill list with filtering |
| `!` at start | Bash mode -- runs command directly without Claude approval, adds output to context |
| `@` anywhere | File path mention -- triggers file path autocomplete with type icons and folder navigation |

### Image Pasting
- `Ctrl+V` or `Cmd+V` (iTerm2) or `Alt+V` (Windows) to paste an image from clipboard
- Drag-and-drop files (hold Shift while dragging to reference them properly in Claude)
- BMP format support for WSL2 Windows clipboard
- TIFF format support on macOS

### Text Editing Shortcuts
| Shortcut | Description |
|----------|-------------|
| `Ctrl+K` | Delete to end of line (stores for pasting) |
| `Ctrl+U` | Delete entire line (stores for pasting) |
| `Ctrl+Y` | Paste deleted text |
| `Alt+Y` (after `Ctrl+Y`) | Cycle paste history |
| `Alt+B` | Move cursor back one word |
| `Alt+F` | Move cursor forward one word |

### External Editor
- `Ctrl+G` opens the system text editor (`EDITOR` or `VISUAL` environment variable) for composing complex input
- Also works in dialog "Other" options
- VS Code question dialogs support multiline input with `Shift+Enter`

### Command History
- `Up`/`Down` arrows navigate through previous inputs
- Input history is stored per working directory
- History resets on `/clear` (previous session preserved for resuming)
- `Ctrl+R` activates reverse search through command history with highlighted matching terms
- `!` prefix triggers bash history autocomplete with `Tab`
- History expansion (`!`) is disabled by default

### Paste Behavior
- Pasted text is treated as single-token deletion (backspace removes entire paste)
- Image paste supported including BMP for WSL2
- Content preservation during history navigation

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [Builder.io Blog](https://www.builder.io/blog/claude-code), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration)

---

## 5. Output / Response Display

### Text Formatting
Claude Code's responses use rich terminal formatting:
- **ANSI color codes** for terminal output
- **Bold** and **italic** text formatting
- **Syntax highlighting** for code blocks (only available in the native build)
- **Markdown rendering** within the terminal (headers, bold, italic, lists, code blocks, inline code, horizontal rules, tables with alignment)
- **Hyperlinks** via OSC 8 escape sequences (clickable with Cmd+click on macOS, Ctrl+click on Windows/Linux in supported terminals)
- File paths in tool output become clickable OSC 8 hyperlinks

### Tool Execution Display
When Claude uses tools, the output shows contextual progress:
- **In Progress**: Present tense verbs (e.g., "Reading", "Searching") with current items displayed
- **Completed**: Past tense verbs (e.g., "Read", "Searched") with final counts
- **Collapsed**: Summary lines with item counts; hovering shows truncated patterns
- ToolSearch results appear as brief notifications rather than inline displays
- Agent progress shows tool use counts
- Task results include token counts, tool uses, and duration

### Thinking / Extended Thinking
When extended thinking is enabled:
- A **shimmer animation** indicates active thinking
- Verbose mode (`Ctrl+O`) toggles display of thinking content in real-time
- Thinking blocks remain interactive during processing (can be interrupted with `Esc`)
- Thinking blocks preserve across context compaction
- Extended thinking has a default budget of 31,999 tokens

### Output Styles
Three built-in output styles:
1. **Default**: Standard system prompt for software engineering tasks, designed for concise output
2. **Explanatory**: Provides educational "Insights" between coding tasks, explaining implementation choices and codebase patterns
3. **Learning**: Collaborative learn-by-doing mode with `TODO(human)` markers for user implementation

Custom output styles can be created as Markdown files with frontmatter. Switch styles with `/output-style`.

### Turn Duration
After each response, a turn duration message appears (e.g., how long the response took). This can be toggled off with `showTurnDuration: false` in settings.

### Streaming
- Tokens appear progressively as they are generated (streaming text output)
- Tool calls are displayed inline within assistant messages showing tool name and parameters

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [Output Styles](https://code.claude.com/docs/en/output-styles), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration)

---

## 6. Tool Approval / Permission Dialogs

Claude Code uses a tiered permission system with inline dialog prompts that appear within the terminal.

### Permission Tiers
| Tool Type | Example | Approval Required | "Yes, don't ask again" Behavior |
|-----------|---------|-------------------|---------------------------------|
| Read-only | File reads, Grep | No | N/A |
| Bash commands | Shell execution | Yes | Permanently per project directory and command |
| File modification | Edit/write files | Yes | Until session end |

### Dialog Appearance
- Permission prompts appear **inline in the terminal** conversation flow (not popup/modal windows)
- They contain **tabs** that can be navigated with `Left/Right` arrow keys
- The dialog shows the tool name, what action is being requested, and the specific command or file involved
- For **Bash**: shows the full command string
- For **Edit**: shows file path, old text, new text (diff-style)
- For **Write**: shows file path and content
- **Blocking**: pauses all processing until user responds

### Dialog Actions
Users can respond by:
- **Allow**: Permit the specific action once
- **Allow always** / **"Yes, don't ask again"**: Persist the permission (scope depends on tool type)
- **Deny**: Block the action
- Navigating tabs using Left/Right arrows
- Approval options include keyboard shortcuts

### Permission Modes (cycled with Shift+Tab or Alt+M)
| Mode | Behavior |
|------|----------|
| `default` (Normal) | Prompts for permission on first use of each tool |
| `acceptEdits` | Automatically accepts file edit permissions for the session |
| `plan` (Plan Mode) | Claude can analyze but not modify files or execute commands |
| `dontAsk` | Auto-denies tools unless pre-approved via settings |
| `bypassPermissions` | Skips all permission prompts (requires safe/isolated environment) |

The status line temporarily hides during permission prompts to avoid visual clutter.

### Managing Permissions
- `/permissions` (alias `/allowed-tools`) lists all permission rules and their source settings files
- Allow, Ask, and Deny rules can be configured in `settings.json` files
- Rules evaluated in order: **deny -> ask -> allow** (first match wins, deny always takes precedence)
- Permission rules follow format `Tool` or `Tool(specifier)` with glob pattern support

**Sources:** [Configure Permissions](https://code.claude.com/docs/en/permissions), [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration)

---

## 7. Status Indicators and Spinners

### Spinner System
The activity indicator provides real-time feedback during agent processing:
- Uses **fixed-width braille characters** to prevent animation jitter
- **Shimmer effects** indicate active thinking (extended thinking mode)
- Spinners hide for instant local commands like `/model` or `/theme`
- Token counters suppress "0 tokens" display until actual tokens arrive

### Spinner Customization (via settings.json)
| Setting | Description | Default |
|---------|-------------|---------|
| `spinnerVerbs` | Custom action verbs shown during processing. Supports `mode: "append"` or `mode: "replace"` with custom verbs (e.g., "Pondering", "Crafting") | Built-in verbs |
| `spinnerTipsEnabled` | Show tips in the spinner while Claude is working | `true` |
| `spinnerTipsOverride` | Override default tips with custom strings. Can set `excludeDefault: true` | None |
| `showTurnDuration` | Show turn duration messages after responses | `true` |

### Product Page Status Animation
The Claude Code product page (claude.com/product/claude-code) displays cycling Unicode symbols paired with action messages like "Debugging...", "Analyzing...", "Thinking...", "Processing..." -- reflecting the feel of the CLI's spinner system.

### Terminal Progress Bar
- `terminalProgressBarEnabled` (default: `true`) enables native terminal progress bar support
- Integrates with iTerm2, Windows Terminal, and tmux native progress bar mechanisms

**Sources:** [Settings](https://code.claude.com/docs/en/settings), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration), [Claude Code Product Page](https://claude.com/product/claude-code)

---

## 8. Header and Footer Elements

### Terminal Title (Header)
- Shows "Claude Code" on startup
- Updates automatically based on conversation context (can be disabled with `CLAUDE_CODE_DISABLE_TERMINAL_TITLE`)
- Updates via `/rename` command
- Persists after `/clear`

### Status Line (Footer)
The status line is a **customizable bar at the bottom of Claude Code** that runs any shell script configured by the user. It receives JSON session data on stdin and displays whatever the script prints.

**Default/built-in status bar elements:**
- Session name (custom or auto-generated)
- PR status with colored dots (see section 20)
- Background task count
- Added directories from `/add-dir`
- Context usage with token percentage
- Git branch (when in VS Code)

**Customizable via `/statusline` command or manual script configuration. Available JSON data fields:**
- `model.id`, `model.display_name` -- Model identifier and display name (e.g., "Opus", "Sonnet")
- `cwd`, `workspace.current_dir` -- Current working directory
- `workspace.project_dir` -- Directory where Claude Code was launched
- `cost.total_cost_usd` -- Total session cost in USD
- `cost.total_duration_ms` -- Wall-clock time since session start
- `cost.total_api_duration_ms` -- Time waiting for API responses
- `cost.total_lines_added`, `cost.total_lines_removed` -- Lines of code changed
- `context_window.total_input_tokens`, `context_window.total_output_tokens` -- Cumulative token counts
- `context_window.context_window_size` -- Max context (200,000 or 1,000,000 tokens)
- `context_window.used_percentage` -- Pre-calculated context usage percentage
- `context_window.remaining_percentage` -- Remaining capacity
- `exceeds_200k_tokens` -- Boolean for exceeding 200K threshold
- `session_id` -- Unique session identifier
- `transcript_path` -- Path to conversation transcript
- `version` -- Claude Code version
- `output_style.name` -- Current output style
- `vim.mode` -- Vim mode (NORMAL/INSERT) when enabled
- `agent.name` -- Agent name when running with `--agent` flag

**Example status line appearance (multi-line):**
```
[Opus] my-project | main
[green progress bar] 25% | $0.55 | 6m 19s
```

**Color coding for context usage progress bar:**
- Green: under 70% usage
- Yellow: 70-89% usage
- Red: 90%+ usage

**Status line behavior:**
- Updates after each new assistant message, permission mode change, or vim mode toggle
- Updates debounced at 300ms
- If a new update triggers while script is running, the in-flight execution is cancelled
- Temporarily hides during autocomplete suggestions, help menu, and permission prompts
- Notifications (MCP server errors, auto-updates, token warnings) display on the right side of the same row
- Verbose mode adds a token counter to this area
- Does not consume API tokens
- `padding` setting adds horizontal spacing (in characters)
- Supports ANSI color codes, multi-line output, and OSC 8 clickable links

**Sources:** [Customize Your Status Line](https://code.claude.com/docs/en/statusline), [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration)

---

## 9. Color Scheme and Themes

### Theme Options
Claude Code offers **6 pre-defined themes** accessible via `/theme` or `/config`:

1. **Dark mode** -- Standard dark background with truecolor syntax highlighting
2. **Light mode** -- Standard light background with truecolor syntax highlighting
3. **Dark mode (colorblind-friendly / daltonized)** -- Accessible color palette for dark backgrounds
4. **Light mode (colorblind-friendly / daltonized)** -- Accessible color palette for light backgrounds
5. **Dark mode (ANSI colors only)** -- Uses the terminal's own 16-color palette
6. **Light mode (ANSI colors only)** -- Uses the terminal's own 16-color palette

### Color Capabilities
- Claude Code adjusts rendering based on the terminal's reported color capabilities
- Most modern terminals support 24-bit truecolor
- Remote shells may not properly advertise truecolor support; set `COLORTERM=truecolor` to force full RGB palette
- ANSI-only themes use the terminal's configured color palette for maximum compatibility
- Standard 256-color or 16-color terminals may render differently from truecolor

### Syntax Highlighting
- Available only in the native build of Claude Code
- Controlled via `Ctrl+T` toggle inside the `/theme` picker menu
- Uses colors to differentiate code syntax within Claude's responses
- Controls whether code in Claude's responses uses syntax coloring

### Theme Switching
- `/theme` command opens a picker menu with all available themes
- `/config` also provides access to theme settings
- Changes take effect immediately
- Adjusts syntax highlighting, status indicators, and UI elements to fit terminal's light or dark background

### Design Aesthetic
Claude's design language uses a warm aesthetic. Third-party Claude-inspired VS Code themes use Claude's signature rust-orange (#C15F3C) color. The CLI itself adapts to the terminal's color scheme when using ANSI-only themes.

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [GitHub Issue #1302](https://github.com/anthropics/claude-code/issues/1302), [GitHub Issue #1185](https://github.com/anthropics/claude-code/issues/1185), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration)

---

## 10. Code Display Formatting

### Code Blocks
- Claude's responses contain code blocks with **syntax highlighting** (in native builds)
- Code blocks use a dark background styling (referenced CSS: `background: #1e2129`)
- `/copy` command presents an interactive picker when code blocks are present, allowing selection of individual blocks or the full response

### File Edit Display
When Claude proposes file edits:
- Shows the proposed changes visually (exact format depends on the edit operation)
- Displays added lines and removed lines with color coding
- For **Edit** tool: shows file path, old text, new text in diff-style format
- For **Write** tool: shows file path and full content
- Users must approve changes before they are applied

### Markdown Rendering
- Claude Code renders markdown within the terminal using ANSI formatting
- Headers, bold, italic, lists, and code blocks are formatted appropriately for terminal display
- Tables are rendered with alignment
- Inline code is formatted distinctly
- Horizontal rules are displayed

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration), [Builder.io Blog](https://www.builder.io/blog/claude-code)

---

## 11. Diff Views

### `/diff` Command
The `/diff` command opens an **interactive diff viewer** showing uncommitted changes and per-turn diffs:
- **Navigation**: Use `Left/Right` arrows to switch between the current git diff and individual Claude turns
- **File browsing**: Use `Up/Down` arrows to browse files
- Shows a file list and changes for each file
- Diff stats indicator shows number of lines added and removed

### Diff Format
- Unified diff-like format, similar to `git diff`
- **Additions**: shown in green with + prefix
- **Deletions**: shown in red with - prefix
- Context lines in default color

### Per-Turn Tracking
- Each user prompt creates a new checkpoint
- Checkpoints persist across sessions
- Can view diffs from individual Claude turns to see what changed at each step
- Each terminal/session accumulates changes separately

### Desktop/VS Code Diff Viewing
When using `/desktop` to hand off to the desktop app or VS Code extension:
- Diffs displayed visually with a file list on the left and changes on the right
- Inline diff highlighting
- A button in the terminal bar shows a change counter
- A modal specific to that session shows the accumulated changes

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [Checkpointing](https://code.claude.com/docs/en/checkpointing), [eesel.ai Blog](https://www.eesel.ai/blog/ide-diff-viewer-claude-code)

---

## 12. Error Displays

### Terminal Error Formatting
- Error messages include an **error type** and **human-readable message**
- Color-coded using ANSI escape sequences (typically red for errors)
- Additional context about the failure is sometimes included
- Errors display when editor operations fail (e.g., `Ctrl+G` external editor)

### Known Rendering Issues (historical, mostly fixed)
- In very long conversations with many tool calls, typed text in the input prompt can become invisible (text still submits correctly via Enter)
- Bold/colored text misalignment has been fixed in recent versions
- Multi-line response styling alignment issues have been addressed
- Windows-specific: `\r\n` line ending issues causing incorrect line counts (fixed)
- `NO_COLOR=1` environment variable handling has had issues in some versions

### Authentication Errors
- "App unavailable in region" message if Claude Code is not available in the user's country
- "command not found: claude" if PATH is not configured correctly
- "Claude Code on Windows requires git-bash" if Git for Windows is not installed
- SSL/TLS errors on older Windows 10 systems

### Rate Limit / Overload Messages
- When rate-limited, fast mode automatically falls back to standard mode
- The fast mode lightning bolt icon turns gray to indicate cooldown
- Token warnings display on the right side of the status line row
- System notifications (MCP server errors, auto-updates) display in the status line area

**Sources:** [Troubleshooting](https://code.claude.com/docs/en/troubleshooting), [Terminal Guide](https://code.claude.com/docs/en/terminal-guide), [GitHub Issue #29706](https://github.com/anthropics/claude-code/issues/29706)

---

## 13. Keyboard Shortcuts Visible in UI

### Discoverability
- Press `?` to see all available keyboard shortcuts for the current environment
- Type `/help` to see available commands
- Type `/` to see all slash commands and skills with filtering

### General Controls
| Shortcut | Description |
|----------|-------------|
| `Ctrl+C` | Cancel current input or generation |
| `Ctrl+D` | Exit Claude Code session (EOF signal) |
| `Ctrl+F` | Kill all background agents (press twice within 3 seconds to confirm) |
| `Ctrl+G` | Open in default text editor |
| `Ctrl+L` | Clear terminal screen (keeps conversation history) |
| `Ctrl+O` | Toggle verbose output (shows detailed tool usage) |
| `Ctrl+R` | Reverse search command history |
| `Ctrl+V` / `Cmd+V` (iTerm2) / `Alt+V` (Windows) | Paste image from clipboard |
| `Ctrl+B` | Background running tasks (tmux users press twice) |
| `Ctrl+T` | Toggle task list |
| `Left/Right arrows` | Cycle through dialog tabs |
| `Up/Down arrows` | Navigate command history |
| `Esc` + `Esc` | Rewind or summarize (checkpoint) |
| `Shift+Tab` or `Alt+M` | Toggle permission modes (Auto-Accept, Plan, Normal) |
| `Option+P` (macOS) / `Alt+P` | Switch model |
| `Option+T` (macOS) / `Alt+T` | Toggle extended thinking |

### Text Editing Shortcuts
| Shortcut | Description |
|----------|-------------|
| `Ctrl+K` | Delete to end of line |
| `Ctrl+U` | Delete entire line |
| `Ctrl+Y` | Paste deleted text |
| `Alt+Y` (after `Ctrl+Y`) | Cycle paste history |
| `Alt+B` | Move cursor back one word |
| `Alt+F` | Move cursor forward one word |

### Theme and Display
| Shortcut | Description |
|----------|-------------|
| `Ctrl+T` | Toggle syntax highlighting (only inside `/theme` picker) |

### macOS Note
Option/Alt key shortcuts require configuring Option as Meta in the terminal:
- **iTerm2**: Settings > Profiles > Keys > set Left/Right Option key to "Esc+"
- **Terminal.app**: Settings > Profiles > Keyboard > check "Use Option as Meta Key"
- **VS Code**: Settings > Profiles > Keys > set Left/Right Option key to "Esc+"

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [Terminal Guide](https://code.claude.com/docs/en/terminal-guide)

---

## 14. Slash Commands

Comprehensive list of built-in slash commands (accessed by typing `/` at the start of input). Not all commands are visible to every user -- some depend on platform, plan, or environment.

### Session Management
| Command | Purpose |
|---------|---------|
| `/clear` (aliases: `/reset`, `/new`) | Clear conversation history and free context |
| `/compact [instructions]` | Compact conversation with optional focus instructions |
| `/context` | Visualize current context as a colored grid |
| `/exit` (alias: `/quit`) | Exit the CLI |
| `/export [filename]` | Export conversation as plain text (to clipboard or file) |
| `/fork [name]` | Create a fork of current conversation at this point |
| `/rename [name]` | Rename session (or auto-generate from history) |
| `/resume [session]` (alias: `/continue`) | Resume conversation by ID/name, or show picker |
| `/rewind` (alias: `/checkpoint`) | Rewind to previous point or summarize |

### Configuration
| Command | Purpose |
|---------|---------|
| `/config` (alias: `/settings`) | Open Settings interface (Config tab) |
| `/fast [on\|off]` | Toggle fast mode on or off |
| `/keybindings` | Open or create keybindings configuration file |
| `/model [model]` | Select/change AI model; left/right arrows adjust effort level |
| `/output-style [style]` | Switch output styles (Default, Explanatory, Learning, custom) |
| `/permissions` (alias: `/allowed-tools`) | View/update permissions |
| `/theme` | Change color theme (6 built-in options) |
| `/vim` | Toggle Vim/Normal editing modes |
| `/terminal-setup` | Configure terminal keybindings for Shift+Enter etc. |

### Development Workflow
| Command | Purpose |
|---------|---------|
| `/add-dir <path>` | Add working directory to current session |
| `/chrome` | Configure Chrome integration settings |
| `/diff` | Interactive diff viewer (uncommitted + per-turn diffs) |
| `/init` | Initialize project with CLAUDE.md guide |
| `/pr-comments [PR]` | Fetch GitHub PR comments (auto-detects or pass PR URL/number) |
| `/review` | Review a pull request for quality, security, tests |
| `/security-review` | Analyze changes for security vulnerabilities |

### Tools and Integrations
| Command | Purpose |
|---------|---------|
| `/agents` | Manage agent configurations |
| `/hooks` | Manage hook configurations for tool events |
| `/ide` | Manage IDE integrations and show status |
| `/mcp` | Manage MCP server connections and OAuth |
| `/memory` | Edit CLAUDE.md memory files, toggle auto-memory |
| `/plugin` | Manage Claude Code plugins |
| `/skills` | List available skills |

### Information and Help
| Command | Purpose |
|---------|---------|
| `/cost` | Show token usage statistics (for API users) |
| `/doctor` | Diagnose installation and settings |
| `/feedback` (alias: `/bug`) | Submit feedback |
| `/help` | Show help and available commands |
| `/insights` | Generate session analysis report (areas, patterns, friction) |
| `/release-notes` | View full changelog |
| `/stats` | Visualize daily usage, streaks, model preferences |
| `/status` | Settings interface (Status tab): version, model, account, connectivity |
| `/usage` | Show plan usage limits and rate limit status |

### Account and Platform
| Command | Purpose |
|---------|---------|
| `/copy` | Copy last response (with code block picker) |
| `/desktop` (alias: `/app`) | Continue session in desktop app (macOS/Windows) |
| `/extra-usage` | Configure extra usage for rate limits |
| `/install-github-app` | Set up GitHub Actions integration |
| `/install-slack-app` | Install Claude Slack app |
| `/login` | Sign in to Anthropic account |
| `/logout` | Sign out |
| `/mobile` (aliases: `/ios`, `/android`) | Show QR code for mobile app |
| `/passes` | Share free Claude Code passes (if eligible) |
| `/plan` | Enter plan mode directly from prompt |
| `/privacy-settings` | View/update privacy settings (Pro/Max only) |
| `/remote-control` (alias: `/rc`) | Enable remote control from claude.ai |
| `/remote-env` | Configure remote environment for teleport |
| `/sandbox` | Toggle sandbox mode |
| `/statusline` | Configure status line with natural language |
| `/stickers` | Order Claude Code stickers |
| `/tasks` | List and manage background tasks |
| `/upgrade` | Open upgrade page |

### Bundled Skills (appear alongside commands)
- `/simplify` -- Simplification workflows
- `/batch` -- Batch operations
- `/debug` -- Debugging workflows

### MCP Prompts
MCP servers can expose prompts as commands with format `/mcp__<server>__<prompt>`, dynamically discovered from connected servers.

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [CLI Reference](https://code.claude.com/docs/en/cli-reference)

---

## 15. Cost / Token Display

### `/cost` Command Output
Displays detailed token usage statistics for the current session:
```
Total cost:            $0.55
Total duration (API):  6m 19.7s
Total duration (wall): 6h 33m 10.2s
Total code changes:    0 lines added, 0 lines removed
```

Note: The `/cost` command shows API token usage and is intended for API/Console users. Claude Max and Pro subscribers have usage included in their subscription, so `/cost` data is not relevant for billing. Subscribers use `/stats` to view usage patterns.

### `/stats` Command
Visualizes daily usage, session history, streaks, and model preferences.

### `/usage` Command
Shows plan usage limits and rate limit status.

### `/context` Command
Visualizes current context usage as a **colored grid**, showing what consumes space (conversation history, MCP tool definitions, etc.).

### Status Line Cost Display
When configured via `/statusline`, the status line can continuously display:
- Total session cost in USD (e.g., `$0.55`)
- Wall-clock time since session start (formatted as minutes and seconds)
- API response time
- Lines of code added/removed
- Context window usage percentage with visual progress bar

### Verbose Mode Token Counter
When verbose output is toggled on (`Ctrl+O`), a token counter appears in the status line area, showing detailed tool usage and execution information. The token counter suppresses "0 tokens" display until actual tokens arrive.

### Background Token Usage
Claude Code uses tokens for background functionality even when idle:
- Conversation summarization (for `claude --resume`)
- Command processing (e.g., `/cost` status checks)
- Typically under $0.04 per session

### Cost Context
- Average cost: $6 per developer per day
- 90% of users: daily costs below $12
- API users: ~$100-200/developer per month with Sonnet 4.6
- Fast mode pricing: $30/150 MTok (input/output) under 200K, $60/225 MTok over 200K

**Sources:** [Manage Costs Effectively](https://code.claude.com/docs/en/costs), [Customize Your Status Line](https://code.claude.com/docs/en/statusline), [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [Fast Mode](https://code.claude.com/docs/en/fast-mode)

---

## 16. Autocomplete and Suggestions

### Context-Aware Autocomplete
Suggestions trigger for multiple contexts:

- **Slash commands**: Type `/` (works anywhere in input, not just at start) to see available commands; type additional characters to filter. Built-in commands prioritized over user skills.
- **File mentions**: `@` prefix shows a file picker with type icons and folder navigation
  - Folder click navigates into directories rather than selecting them
  - Anchor fragment support (e.g., `@README.md#installation`)
  - Large PDF handling: lightweight references for PDFs exceeding 10 pages, with page range parameters
  - Respects `.gitignore` (configurable via `respectGitignore` setting)
  - Pre-warmed on startup with session-based caching and background refresh
  - Displayed as removable attachments with correct relative paths from subdirectories
- **Bash history**: `!` prefix enables history completion with Tab
- **Command history**: Tab shows session history suggestions

### Display Characteristics
- Type icons differentiate suggestion categories
- Single-line formatting for compact display
- Truncated descriptions (max 2 lines)
- Built-in commands prioritized over user skills

### Prompt Suggestions
- Grayed-out example appears on session start (picked from project git history)
- After Claude responds, follow-up suggestions appear based on conversation context (e.g., next step from multi-part request)
- Press `Tab` to accept, `Enter` to accept and submit, or start typing to dismiss
- Runs as background request reusing parent conversation's prompt cache (minimal additional cost)
- Skipped when cache is cold, after first turn, in non-interactive mode, and in plan mode
- Configurable: `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=false` to disable

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration)

---

## 17. Task List

When working on complex, multi-step work, Claude creates a **task list** to track progress.

### Appearance
- Tasks appear in the **status area** of the terminal
- Indicators show what is **pending**, **in progress**, or **complete**
- Display shows up to 10 tasks at a time

### Controls
- Press `Ctrl+T` to toggle the task list view
- Ask Claude directly: "show me all tasks" or "clear all tasks"
- Tasks persist across context compactions, helping Claude stay organized on larger projects
- Share task list across sessions with `CLAUDE_CODE_TASK_LIST_ID=my-project` (uses named directory in `~/.claude/tasks/`)
- Revert to previous TODO list behavior with `CLAUDE_CODE_ENABLE_TASKS=false`

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode)

---

## 18. Vim Mode Indicators

When vim mode is enabled (via `/vim` command or `/config`):

- The current mode is displayed: **NORMAL** or **INSERT**
- Mode is available via status line JSON data as `vim.mode`
- Status line updates when vim mode toggles
- Comprehensive vim keybindings are active:
  - Mode switching: `Esc` (to NORMAL), `i`/`I`/`a`/`A`/`o`/`O` (to INSERT)
  - Navigation: `h`/`j`/`k`/`l`, `w`/`e`/`b`, `0`/`$`/`^`, `gg`/`G`, `f`/`F`/`t`/`T`
  - Editing: `x`, `dd`, `D`, `dw`/`de`/`db`, `cc`/`C`, `cw`/`ce`/`cb`, `yy`/`Y`, `p`/`P`, `>>`/`<<`, `J`, `.`
  - Text objects: `iw`/`aw`, `iW`/`aW`, `i"`/`a"`, `i'`/`a'`, `i(`/`a(`, `i[`/`a[`, `i{`/`a{`
- In normal mode, if cursor is at beginning/end of input and cannot move further, arrow keys navigate command history instead

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [Customize Your Status Line](https://code.claude.com/docs/en/statusline)

---

## 19. Fast Mode Indicators

When fast mode is enabled:
- A small **`...` (lightning bolt) icon** appears next to the prompt while fast mode is active
- Confirmation message displayed: **"Fast mode ON"**
- When fast mode falls back due to rate limiting, the lightning bolt icon **turns gray** to indicate cooldown
- Fast mode automatically re-enables when cooldown expires
- When disabled, the icon disappears
- Run `/fast` to check current fast mode state (on or off)

Fast mode uses the same Opus 4.6 model with a different API configuration prioritizing speed (2.5x faster, higher cost per token). It is not a different model -- identical quality and capabilities, just faster responses.

**Sources:** [Fast Mode](https://code.claude.com/docs/en/fast-mode)

---

## 20. PR Review Status

When working on a branch with an open pull request:

### Display
- A **clickable PR link** appears in the **footer** (e.g., "PR #446")
- The link has a **colored underline** indicating the review state

### Color Coding
| Color | State |
|-------|-------|
| Green | Approved |
| Yellow | Pending review |
| Red | Changes requested |
| Gray | Draft |
| Purple | Merged |

### Interaction
- `Cmd+click` (Mac) or `Ctrl+click` (Windows/Linux) opens the PR in the browser
- Status updates automatically every 60 seconds
- Requires `gh` CLI to be installed and authenticated (`gh auth login`)

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode)

---

## 21. Checkpointing / Rewind UI

### Automatic Checkpointing
- Every user prompt creates a new checkpoint
- Tracks all file changes made by Claude's editing tools (Edit, Write)
- Persists across sessions (accessible in resumed conversations)
- Automatically cleaned up along with sessions after 30 days (configurable)

### Rewind Interface (`Esc+Esc` or `/rewind`)
1. Opens a **scrollable list** of user prompts from the session
2. User selects the point to act on
3. Chooses an action:
   - **Restore code and conversation** -- reverts both to that point
   - **Restore conversation** -- rewinds messages, keeps current code
   - **Restore code** -- reverts files, keeps conversation
   - **Summarize from here** -- compresses conversation from selected point forward into AI-generated summary (original messages preserved in transcript)
   - **Never mind** -- returns to message list without changes
4. After restoring or summarizing, the original prompt from the selected message is restored into input field for re-sending or editing
5. Optional instructions can guide what the summary focuses on

### Limitations
- Does **not** track files modified by bash commands (e.g., `rm`, `mv`, `cp`)
- Does **not** track external/manual file changes outside Claude Code
- Not a replacement for version control (designed for quick session-level recovery)

**Sources:** [Checkpointing](https://code.claude.com/docs/en/checkpointing)

---

## 22. Background Tasks

### Backgrounding Commands
- Press `Ctrl+B` to move a running bash command to the background (tmux users press twice due to prefix key)
- Can also prompt Claude to run commands in the background
- Background tasks have **unique IDs** for tracking and output retrieval
- Output is buffered and retrievable via TaskOutput tool
- Background tasks automatically cleaned up when Claude Code exits

### Visual Indicators
- Background task count displayed in status bar
- Common backgrounded commands: build tools (webpack, vite), test runners (jest, pytest), dev servers, package managers

### `/tasks` Command
Lists and manages background tasks.

### Disabling
Set `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` to disable all background task functionality.

### Bash Mode (`!` prefix)
- Run bash commands directly without Claude's interpretation/approval
- Adds command and output to conversation context
- Shows real-time progress and output
- Supports `Ctrl+B` backgrounding
- Supports history-based autocomplete (Tab completes from previous `!` commands)

**Sources:** [Interactive Mode](https://code.claude.com/docs/en/interactive-mode)

---

## 23. Context Visualization

### `/context` Command
Visualizes current context usage as a **colored grid**. Helps identify what is consuming context space (conversation history, MCP tool definitions, file contents, etc.). Useful for deciding when to run `/compact` or `/clear`.

### Status Line Context Display
Available data fields for status line scripts:
- `context_window.total_input_tokens` -- Cumulative input tokens across session
- `context_window.total_output_tokens` -- Cumulative output tokens
- `context_window.context_window_size` -- Max context (200,000 default or 1,000,000 for extended context models)
- `context_window.used_percentage` -- Pre-calculated usage percentage (input tokens only)
- `context_window.remaining_percentage` -- Remaining capacity
- `context_window.current_usage` -- Token counts from most recent API call (input, output, cache creation, cache read)
- `exceeds_200k_tokens` -- Boolean flag for exceeding 200K threshold (fixed threshold regardless of actual window size)

### Auto-Compaction
Claude Code automatically summarizes conversation history when approaching context limits, reducing token usage while preserving essential information. Custom compaction instructions can be added via `/compact` command or CLAUDE.md.

**Sources:** [Customize Your Status Line](https://code.claude.com/docs/en/statusline), [Interactive Mode](https://code.claude.com/docs/en/interactive-mode), [Manage Costs Effectively](https://code.claude.com/docs/en/costs)

---

## 24. Accessibility Features

### Reduced Motion
- `prefersReducedMotion: true` in settings reduces or disables UI animations (spinners, shimmer, flash effects)
- Respects system motion preferences

### Colorblind-Friendly Themes
- Two daltonized themes available (dark and light)
- Designed for users with color vision deficiencies
- Accessible via `/theme` command

### ANSI-Only Themes
- Two ANSI-only themes (dark and light)
- Use the terminal's own 16-color palette, which users may have customized for accessibility
- Most compatible option across terminals

### Screen Reader Compatibility
- Text-based interface is inherently compatible with screen readers
- All interactions are keyboard-driven
- No mouse-only interactions

### Language Support
- `language` setting configures Claude's preferred response language (e.g., "japanese")
- Independent of UI language

**Sources:** [Settings](https://code.claude.com/docs/en/settings), [Interactive Mode](https://code.claude.com/docs/en/interactive-mode)

---

## 25. Terminal Compatibility Notes

### Terminal-Specific Features
| Terminal | Special Features |
|----------|-----------------|
| **iTerm2** | Shift+Enter native, Cmd+V image paste, progress bar, OSC 8 links, CSIu support |
| **Kitty** | Keyboard protocol, Ctrl+Z suspend, native multi-key sequences |
| **WezTerm** | CSIu protocol, Shift+Enter, Option+Return for newlines |
| **Ghostty** | Kitty protocol, Shift+Enter |
| **Warp** | Native Shift+Enter without prompting (detection skips unnecessary prompts) |
| **Windows Terminal** | Git Bash for hooks, MSYS2/Cygwin compatibility |
| **VS Code** | Scroll behavior fixes, dimming during dialogs, native Python venv |
| **Terminal.app** | Does NOT support clickable OSC 8 links |

### Platform-Specific Handling
- **Windows**: Console window flash prevention, temp directory path escaping, CWD tracking cleanup, drive letter casing normalization, right Alt key escape sequence cleanup
- **macOS**: FSEvents watcher loop prevention for git commands, Option-as-Meta hints with terminal-specific instructions, orphaned process cleanup on disconnect, sandbox temp directory fixes
- **Linux/WSL**: BMP format image paste support for WSL2 clipboard, SSH image paste guidance

### Keyboard Protocol Support
- CSIu (Enhanced Keyboard) for modern terminals (iTerm2, WezTerm, Ghostty, Kitty)
- Kitty Keyboard Protocol with modifier key support
- Native Shift+Enter support in modern terminals
- Legacy escape sequences for older terminals

### Privacy for Recordings/Streaming
- `CLAUDE_CODE_HIDE_ACCOUNT_INFO` environment variable hides email and organization name from UI
- `IS_DEMO` environment variable also hides personal information for screen recordings
- `DISABLE_NON_ESSENTIAL_MODEL_CALLS` disables model calls for non-critical paths like flavor text

**Sources:** [DeepWiki UI/UX Analysis](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration), [Settings](https://code.claude.com/docs/en/settings), [Terminal Guide](https://code.claude.com/docs/en/terminal-guide)

---

## 26. What Claude Code Does NOT Have

Based on the official documentation and source analysis, Claude Code's terminal interface does NOT include:
- No graphical GUI (it is purely terminal-based text)
- No sidebar with conversation history
- No avatar icons or speech bubbles
- No web browser embedded in the interface
- No image rendering inline in the terminal (images are sent as file paths/references)
- No split panes by default
- No mouse-driven interactions (keyboard only)
- No graphical panels or windows
- No separate chat and code panels (single unified terminal view)

Note: The VS Code extension, JetBrains plugin, desktop app, and web interface have additional graphical elements not present in the CLI.

---

## 27. Sources

### Official Anthropic Documentation
- [Claude Code Overview](https://code.claude.com/docs/en/overview) -- Product overview, installation, capabilities
- [Terminal Guide for New Users](https://code.claude.com/docs/en/terminal-guide) -- Step-by-step terminal installation guide
- [CLI Reference](https://code.claude.com/docs/en/cli-reference) -- Complete CLI commands and flags reference
- [Interactive Mode](https://code.claude.com/docs/en/interactive-mode) -- Keyboard shortcuts, slash commands, input modes
- [Configure Permissions](https://code.claude.com/docs/en/permissions) -- Permission system, modes, rules
- [Settings](https://code.claude.com/docs/en/settings) -- Configuration options, themes, display preferences
- [Manage Costs Effectively](https://code.claude.com/docs/en/costs) -- Cost tracking, /cost command, token usage
- [Customize Your Status Line](https://code.claude.com/docs/en/statusline) -- Status bar configuration, JSON data, examples
- [Output Styles](https://code.claude.com/docs/en/output-styles) -- Default, Explanatory, Learning styles
- [Checkpointing](https://code.claude.com/docs/en/checkpointing) -- Rewind, restore, summarize
- [Speed Up Responses with Fast Mode](https://code.claude.com/docs/en/fast-mode) -- Fast mode toggle, indicators, pricing
- [Quickstart Guide](https://code.claude.com/docs/en/quickstart) -- Getting started, first session

### Official Product Page
- [Claude Code Product Page](https://claude.com/product/claude-code) -- Product marketing, animations, platform availability

### Source Code Analysis
- [DeepWiki - UI/UX and Terminal Integration](https://deepwiki.com/anthropics/claude-code/3.9-uiux-and-terminal-integration) -- Detailed rendering system, keyboard handling, visual feedback, terminal compatibility
- [GitHub - anthropics/claude-code](https://github.com/anthropics/claude-code) -- Open source repository
- [Claude Code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) -- Version history and UI fixes

### Blog Posts and Guides
- [How I Use Claude Code - Builder.io](https://www.builder.io/blog/claude-code) -- Practical interface descriptions and tips
- [Claude Code CLI: The Definitive Technical Reference - Introl](https://introl.com/blog/claude-code-cli-comprehensive-guide-2025) -- Comprehensive CLI guide
- [Claude Code Status Line: Display Model, Cost, and Git Branch - Medium](https://medium.com/@CodeCoup/claude-code-status-line-display-model-cost-and-git-branch-in-your-terminal-27e4d4317372) -- Status line configuration
- [Fixing Claude Code's Flat or Washed-Out Remote Colors - Medium](https://ranang.medium.com/fixing-claude-codes-flat-or-washed-out-remote-colors-82f8143351ed) -- Color rendering in remote sessions
- [Terminal Configuration Guide - eesel.ai](https://www.eesel.ai/blog/terminal-configuration-claude-code) -- Terminal setup
- [Claude Code Terminal Setup Guide - claudefa.st](https://claudefa.st/blog/guide/terminal-setup-guide) -- Terminal configuration
- [How to Get a Proper IDE Diff Viewer - eesel.ai](https://www.eesel.ai/blog/ide-diff-viewer-claude-code) -- Diff viewing options

### GitHub Issues (UI/Theme-related)
- [Issue #1302 - Custom Terminal Themes](https://github.com/anthropics/claude-code/issues/1302) -- Theme options discussion
- [Issue #1185 - Theme Color Options Too Limited](https://github.com/anthropics/claude-code/issues/1185) -- 6 built-in themes confirmed
- [Issue #11813 - System Theme Support (Auto Light/Dark)](https://github.com/anthropics/claude-code/issues/11813) -- Auto theme switching request
- [Issue #10828 - Real-time Token Usage in Status Bar](https://github.com/anthropics/claude-code/issues/10828) -- Token display feature request
- [Issue #4385 - Highlight User Prompts for Better Visibility](https://github.com/anthropics/claude-code/issues/4385) -- User message styling
- [Issue #29706 - Terminal Color Rendering Bug](https://github.com/anthropics/claude-code/issues/29706) -- ANSI color rendering issues
- [Issue #22367 - Theme Color Customization for Diff Highlighting](https://github.com/anthropics/claude-code/issues/22367) -- Diff color customization
- [Issue #25219 - Input Text Not Visible in Long Conversations](https://github.com/anthropics/claude-code/issues/25219) -- Input visibility bug
- [Issue #21647 - Prompt Bar UI Bug](https://github.com/anthropics/claude-code/issues/21647) -- Text disappears in prompt

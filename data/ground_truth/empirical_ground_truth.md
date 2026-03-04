# Empirical Ground Truth: Claude Code Interface

Gathered from DIRECT OBSERVATION by Claude running inside Claude Code v2.1.66.
This is first-person empirical evidence, not documentation-based.

## Source: My Own System Prompt (what I actually receive)

From my system prompt, I can directly observe:
1. "You are Claude Code, Anthropic's official CLI for Claude."
2. Platform: win32, Shell: bash
3. OS Version: Windows 11 Enterprise 10.0.26100
4. Model: claude-opus-4-6[1m] (Opus 4.6 with 1M context)
5. Working directory: C:\Users\hyogon.ryu\Desktop\project\claude-code-meta-recognition
6. Git status is provided at conversation start
7. "All text you output outside of tool use is displayed to the user"
8. "You can use Github-flavored markdown for formatting, and will be rendered in a monospace font using the CommonMark specification"
9. Tool outputs include <system-reminder> tags
10. The system will "automatically compress prior messages" as context limits approach

## Source: My Available Tools

I can directly observe my tool set:
- Bash (shell execution)
- Glob (file pattern matching)
- Grep (content search via ripgrep)
- Read (file reading, supports images/PDFs)
- Edit (string replacement in files)
- Write (file creation/overwrite)
- NotebookEdit (Jupyter notebook editing)
- WebFetch (URL content fetching)
- WebSearch (web search)
- Agent (launch subagents)
- TaskOutput (get background task output)
- TaskStop (stop background tasks)
- AskUserQuestion (ask user questions with options)
- EnterPlanMode (enter planning mode)
- ExitPlanMode (exit planning mode)
- TaskCreate, TaskGet, TaskUpdate, TaskList (task management)
- EnterWorktree (git worktree isolation)
- Skill (invoke skills/slash commands)
- Plus MCP tools (mcp__supervisor__ask_supervisor, mcp__supervisor__check_status)

## Source: claude --help Output (Actual v2.1.66)

Version: 2.1.66

CLI Commands:
- claude (start interactive session)
- claude "query" (with initial prompt)
- claude -p "query" (print mode, non-interactive)
- claude -c (continue most recent conversation)
- claude -r (resume by session ID)
- claude update/upgrade
- claude auth (login/logout/status)
- claude agents (list agents)
- claude mcp (configure MCP)
- claude doctor (health check)
- claude install (install native build)
- claude setup-token (long-lived auth token)
- claude plugin (manage plugins)

Key Flags:
- --model (select model: 'sonnet', 'opus', or full name)
- --permission-mode (choices: acceptEdits, bypassPermissions, default, dontAsk, plan)
- --allowedTools / --disallowedTools
- --system-prompt / --append-system-prompt
- --worktree / -w (git worktree isolation)
- --chrome / --no-chrome
- --verbose
- --debug
- --max-budget-usd (print mode only)
- --agents (JSON for custom agents)
- --effort (low, medium, high)
- --tools (restrict available tools)

## Source: My System Prompt Instructions About Interface

What my system prompt tells me about user interaction:
1. "Output text to communicate with the user"
2. Markdown rendered in monospace font, CommonMark spec
3. "Tool results and user messages may include <system-reminder> or other tags"
4. Users can configure 'hooks' (shell commands for tool events)
5. "The system will automatically compress prior messages"
6. Permission modes exist (referenced by Shift+Tab toggling)
7. Users see tool calls and can approve/deny them
8. /help, /clear mentioned as built-in CLI commands
9. Skills are invocable via / prefix

## Source: Skill System (What's Actually Available)

From system reminders, these skills are available:
- keybindings-help
- simplify
- claude-developer-platform
- commit-commands:clean_gone
- commit-commands:commit-push-pr
- commit-commands:commit
- ralph-loop:cancel-ralph
- ralph-loop:help
- ralph-loop:ralph-loop

## Source: Director's Screenshot (v2.1.66)

Actual startup screen shows:
- Bordered box with ╭╮╰╯ rounded corners
- "Claude Code v2.1.66" in top border
- Two-column layout inside the box:
  - LEFT: "Welcome back 유효곤!" + small ASCII logo (▐▛███▜▌) + model info + org + working dir
  - RIGHT: "Tips for getting started" + "Recent activity"
- Input area below with ❯ prompt character
- Horizontal separator lines
- Status: "⏵⏵ bypass permissions on (shift+tab to cycle)"

## Source: My Observations During This Session

What I've directly experienced:
1. Tool calls require user approval (I see approval/denial feedback)
2. Subagents can run in background (I launched 8 in parallel)
3. TaskCreate/TaskUpdate/TaskList work for progress tracking
4. Ctrl+T toggles task list (mentioned in system reminders)
5. System sends <system-reminder> tags inline with tool results
6. Background agents complete and I receive notifications
7. Bash tool has timeout (default 120s, max 600s)
8. Read tool can view images (I used it to verify figures)
9. Read tool can view PDFs (I used it for report verification)
10. Git operations work normally from Bash
11. WebSearch and WebFetch are available for internet access
12. Multiple tool calls can be made in parallel in one response

## Key Interface Elements I Can VERIFY

### Confirmed by direct experience:
- Terminal-based CLI ✅
- Markdown rendering (I produce markdown and it's rendered) ✅
- Tool approval dialogs exist (tools get approved/denied) ✅
- Multiple permission modes (system prompt mentions them) ✅
- Shift+Tab cycles permission modes ✅
- Background tasks with IDs ✅
- Task list system (Ctrl+T) ✅
- Subagent system (Agent tool) ✅
- Slash commands / Skills system ✅
- Session continuity (--continue flag) ✅
- Git worktree support (--worktree flag) ✅
- Working directory shown ✅
- Model info displayed ✅
- Version info available (v2.1.66) ✅
- Cost/token tracking (--max-budget-usd exists) ✅
- Streaming output (I produce tokens progressively) ✅
- Context compression when approaching limits ✅

### Confirmed INCORRECT by screenshot:
- Prompt character is ❯ (NOT > as Claude suggested) ❌
- Startup has 2-column layout (NOT single-column) ❌
- Logo is small abstract art (NOT large "CLAUDE CODE" banner) ❌
- Welcome has personalized greeting "Welcome back [name]!" ❌ (Claude didn't know)
- Organization info shown (KRAFTON Inc.) ❌ (Claude didn't know)

### Cannot verify (would need nested session):
- Exact colors/themes
- Spinner animation appearance
- Diff view exact formatting
- Error display exact formatting
- Exact appearance of /help output

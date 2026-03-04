# E6: Claude Code Visual Interface Knowledge

## E6.1: Compact Mode vs Full Mode

**Confidence: Medium-High**

Claude Code operates in a terminal/CLI environment and has two primary output modes that affect how conversation history is managed and displayed:

**Full Mode (Default):**
- The entire conversation history is sent to the model with each turn. All previous messages, tool calls, tool results, and assistant responses are preserved in full fidelity.
- The user sees the complete scrollback of the conversation in their terminal. Each message from the user, each response from Claude, and each tool call/result is visible if the user scrolls up.
- Tool call outputs (file contents, command outputs, search results) are displayed in their entirety within the conversation flow.
- The conversation can grow quite long, and eventually may approach context window limits.

**Compact Mode:**
- Compact mode is triggered either automatically (when the context window is getting full) or manually by the user via the `/compact` slash command.
- When compaction occurs, the entire conversation history is summarized into a condensed representation. The model generates a summary of what has been discussed, what files have been read/edited, what decisions have been made, and what the current task state is.
- Visually, when compaction happens, the user sees a message or indicator that the conversation has been compacted. The terminal does not erase previous output (since it is a scrollback terminal), but logically the model now operates from the summary rather than the full history.
- After compaction, new messages continue to appear normally in the terminal. The user can still scroll up to see old output, but the model no longer has access to the raw details -- only the summary.
- The `/compact` command can optionally take a prompt/instruction to guide what the summary should focus on, e.g., `/compact focus on the database migration work`.

**Visual Differences:**
- There is no dramatic visual change between modes. The terminal output looks similar in both cases. The key difference is operational: in compact mode, the model may occasionally lose track of fine details that were in earlier parts of the conversation because they were summarized away.
- When auto-compaction triggers, there may be a brief system message or status line indicating that the context was compacted.
- The `/compact` command itself produces output confirming that compaction occurred and may show a brief summary of what was retained.

## E6.2: Diff View for File Edits

**Confidence: Medium-High**

When Claude Code edits a file using the Edit tool (or Write tool), the diff is displayed to the user in the terminal before the edit is applied (or as part of the permission prompt). The visual presentation is as follows:

**Diff Display Format:**
- The diff is shown in a unified diff-like format, similar to `git diff` output but rendered with terminal colors for readability.
- **Additions (new lines)** are displayed in **green** text, typically prefixed with a `+` character. These represent lines that will be added to the file.
- **Deletions (removed lines)** are displayed in **red** text, typically prefixed with a `-` character. These represent lines that will be removed from the file.
- **Context lines** (unchanged lines surrounding the edit) are displayed in the default terminal color (usually white or gray) without a prefix or with a space prefix. A few lines of context above and below the change are shown to help the user understand where in the file the edit occurs.
- The file path is displayed at the top of the diff block, indicating which file is being modified.

**Permission Flow:**
- Before the edit is applied, the user is prompted to approve or reject it. The diff is shown as part of this approval prompt.
- The user can accept the edit (press Enter or type 'y'), reject it, or in some cases edit the proposed change.
- If the user has configured auto-accept for certain tools or is running in a mode with relaxed permissions (e.g., `--dangerously-skip-permissions`), the diff may still be displayed but the edit proceeds without waiting for confirmation.

**Additional Details:**
- For the Edit tool specifically, the `old_string` and `new_string` are used to compute the diff. The display highlights exactly what text is being replaced.
- For the Write tool (which overwrites an entire file), the diff may show the full file content difference, which can be lengthy for large files.
- Line numbers are typically shown alongside the diff to help locate the change within the file.
- The diff block is visually set apart from regular conversation text, often with a border, box, or distinct background formatting that the terminal supports (using ANSI escape sequences for styling).

## E6.3: Multi-File Edit Workflow

**Confidence: Medium**

When Claude Code edits multiple files in sequence, each edit is presented individually to the user as a separate tool call. The visual flow is as follows:

**Sequential Display:**
1. Claude's response text appears first, explaining what changes it plans to make and why.
2. The first file edit is displayed as a tool call block. The file path is shown, followed by the diff (as described in E6.2). The user is prompted to approve or reject this edit.
3. After the first edit is approved (or rejected), Claude may output additional explanatory text, then the second file edit appears as another tool call block with its own diff and approval prompt.
4. This continues for each file that needs editing.

**Visual Structure:**
- Each tool call (Edit or Write) appears as a distinct block in the terminal output. These blocks are visually separated from Claude's prose text.
- The tool name and parameters may be shown in a header line for each block (e.g., "Edit file: /path/to/file.ts").
- Between edits, Claude may provide explanatory text about what the next edit will accomplish.
- There is no unified "multi-file diff view" that shows all changes across files at once. Each file's changes are presented one at a time.

**Batch Behavior:**
- Claude can issue multiple tool calls in a single response turn. When this happens, the tool calls may be displayed in sequence within the same response block, but each still requires individual approval (unless auto-accept is enabled).
- The user sees each file's changes as they come, allowing them to approve or reject on a per-file basis.
- If one edit is rejected, Claude can still proceed with subsequent edits (the rejection of one does not cancel the others, though Claude may adjust its approach based on the rejection).

**Progress Indication:**
- There is no explicit progress bar or "3 of 5 files edited" counter. The user tracks progress by observing the sequence of tool calls in the terminal output.
- After all edits are complete, Claude typically provides a summary of what was changed.

## E6.4: Thinking/Reasoning Display

**Confidence: Medium-High**

Claude Code supports an "extended thinking" or "chain-of-thought" mode where Claude's internal reasoning process is displayed to the user.

**Thinking Display:**
- When extended thinking is enabled (which it typically is by default in Claude Code), Claude's thinking/reasoning appears in a visually distinct block before the main response.
- The thinking block is displayed in a **dimmed, muted, or lighter color** compared to the main response text. This visually separates the internal reasoning from the actual actions/responses.
- The thinking text may appear in a collapsible or summarized format. In the terminal, it is often shown with a distinct prefix or indentation to differentiate it from the main output.
- The thinking content shows Claude's step-by-step reasoning: analyzing the problem, considering different approaches, planning which files to examine or edit, and deciding on a course of action.

**Visual Characteristics:**
- The thinking block typically appears at the beginning of Claude's response, before any tool calls or prose output.
- It may be prefixed with a label like "Thinking..." or displayed within a bordered box or indented block.
- The text within the thinking block is Claude's stream-of-consciousness reasoning -- it can include considerations about file structure, potential approaches, trade-offs, and plans.
- As Claude streams its response, the thinking text appears first (character by character or chunk by chunk), followed by the main response.

**User Control:**
- Users can influence thinking behavior through the model configuration or system prompt settings.
- The thinking is genuine extended thinking from the model, not a simulated display -- it reflects the model's actual reasoning tokens.
- In some configurations, the thinking may be hidden or minimized by default, with the option to expand it. However, in the standard Claude Code terminal interface, it is shown inline.

**Streaming Behavior:**
- During streaming, the thinking text appears progressively as it is generated. The user can watch Claude's reasoning unfold in real time.
- Once thinking is complete, there may be a visual transition (a divider line or change in text style) before the main response begins.

## E6.5: Error Display

**Confidence: Medium**

When a tool call fails or Claude encounters an error in Claude Code, the error is displayed in a distinctive visual format in the terminal.

**Tool Call Errors:**
- When a tool call (Bash command, file read, file edit, etc.) fails, the error output is displayed in **red text** or within a red-highlighted block to clearly indicate failure.
- The error message from the tool is shown verbatim. For example:
  - A failed Bash command shows the stderr output and the non-zero exit code.
  - A failed Edit shows an error message like "old_string not found in file" or "old_string is not unique in file."
  - A failed Read shows "file not found" or permission errors.
- The error block includes the tool name and the parameters that were used, so the user can see exactly what was attempted.

**Error Recovery Flow:**
- After an error, Claude typically acknowledges the failure in its response text and attempts an alternative approach. For example, if an Edit fails because the `old_string` was not unique, Claude might re-read the file and try a more specific `old_string`.
- The error does not terminate the conversation or the current turn. Claude continues processing and can make additional tool calls.

**System-Level Errors:**
- If there is a network error, API error, or context window overflow, a different kind of error message may appear. These are typically displayed as system messages rather than tool results.
- Context window overflow errors prompt the auto-compaction behavior described in E6.1.
- Rate limiting or API errors may show a message indicating that Claude is waiting to retry, sometimes with a countdown or spinner.

**Visual Formatting:**
- Error messages are typically rendered with:
  - Red or orange text color (ANSI terminal colors)
  - A distinct prefix or icon (possibly an "X" or error symbol)
  - Clear separation from normal output via boxing, indentation, or horizontal rules
- The error is shown inline within the conversation flow, at the point where the tool call was made.
- Failed commands in the Bash tool show both stdout and stderr, with stderr potentially highlighted differently.

**Permission Denied Errors:**
- When Claude attempts an action that the user has not granted permission for, a permission prompt appears instead of an error. The user can then grant or deny the permission.
- If denied, this appears as a specific kind of "tool not allowed" result, and Claude acknowledges it and adjusts its approach.

---

*These responses are based on training knowledge about Claude Code's terminal interface as of the knowledge cutoff. Some specific visual details (exact colors, border styles, formatting characters) may vary across versions, terminal emulators, and operating system environments.*

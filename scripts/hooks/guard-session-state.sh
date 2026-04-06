#!/usr/bin/env bash
# guard-session-state.sh — PreToolCall hook
# Blocks unauthorized writes to the SESSION STATE block in tasks/todo.md
#
# Called by Claude Code before Write/Edit tool calls.
# Receives tool call info via stdin as JSON.
#
# PRIMARY PATH: MCP tool calls (mcp__ak-state-machine__transition_session,
# mcp__ak-state-machine__set_active_persona) bypass this hook entirely —
# MCP calls are not intercepted by Write/Edit PreToolCall hooks. This guard
# only fires when a skill uses the fallback direct-file-write path.
#
# FALLBACK AUTH: session-open and session-close write a lock file at
# tasks/.session-transition-lock before any direct STATE edit, and delete it
# after. This guard checks for that file instead of the ACTIVE_SKILL env var
# (which Claude Code's skill loader does not propagate).
#
# DETECTION: The guard reads the actual target file from disk and determines
# whether the proposed edit overlaps the ## SESSION STATE block by position.
# It does NOT pattern-match the diff text — that approach is bypassable by
# omitting the "SESSION STATE" marker from old_string/new_string.
#
# STALE LOCK: if the lock file is older than 30 minutes, a previous run
# likely crashed before cleanup. The guard blocks with STALE_LOCK_FLAG and
# prints the recovery command.
#
# Exit 0 = allow, Exit 2 = block with message on stderr

set -euo pipefail

LOCK_FILE="tasks/.session-transition-lock"
STALE_THRESHOLD_SECONDS=1800  # 30 minutes

INPUT="$(cat)"

# Extract the target file path from the tool call
FILE_PATH="$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
params = data.get('tool_input', {})
print(params.get('file_path', params.get('path', '')))
" 2>/dev/null || echo "")"

# Only care about tasks/todo.md — exact suffix match.
# Using an exact pattern avoids matching unrelated paths that happen to contain
# the substring "tasks/todo.md" (e.g. /docs/tasks/todo.md.backup).
if [[ "$FILE_PATH" != "tasks/todo.md" && "$FILE_PATH" != */tasks/todo.md ]]; then
  exit 0
fi

# Exclude the project-template copy using an exact path-component match.
# A substring check (*project-template*) would bypass the guard for any real
# project whose path happens to contain "project-template" as a directory name.
if [[ "$FILE_PATH" == */project-template/tasks/todo.md ]]; then
  exit 0
fi

# Determine whether this edit actually modifies content inside the SESSION STATE
# block by reading the current file from disk and checking edit overlap by position.
#
# This is the only reliable approach — matching patterns in the diff text (old_string,
# new_string, content) is bypassable because those fields contain only the changed
# fragment, not the block header or surrounding context.
#
# LOCK_FILE is passed as a positional argument (sys.argv[1]) to avoid path injection
# from expanding shell variables inside Python string literals.
TOUCHES_SESSION_STATE="$(echo "$INPUT" | python3 -c '
import sys, json, re

def get_session_state_span(text):
    """Return (start, end) character offsets of the ## SESSION STATE block, or (None, None)."""
    header = "## SESSION STATE"
    idx = text.find(header)
    if idx == -1:
        return None, None
    rest = text[idx + len(header):]
    # Block ends at the next ## heading (or EOF)
    m = re.search(r"\n## ", rest)
    end = idx + len(header) + (m.start() if m else len(rest))
    return idx, end

try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.stdout.write("false\n")
    sys.exit(0)

params = data.get("tool_input", {})
file_path = sys.argv[1] if len(sys.argv) > 1 else ""

# Read the current file from disk
try:
    with open(file_path, "r") as f:
        current = f.read()
except FileNotFoundError:
    # File does not exist yet — this is a Write creating it fresh.
    # Check whether the new content contains a SESSION STATE block.
    new_content = params.get("content", "")
    sys.stdout.write("true\n" if "## SESSION STATE" in new_content else "false\n")
    sys.exit(0)
except Exception:
    sys.stdout.write("false\n")
    sys.exit(0)

cur_start, cur_end = get_session_state_span(current)

if "content" in params:
    # Write tool — full file replacement.
    # Compare SESSION STATE block in current file vs new content.
    new_content = params["content"]
    new_start, new_end = get_session_state_span(new_content)
    if cur_start is None and new_start is None:
        # Neither has SESSION STATE — no protected content touched
        sys.stdout.write("false\n")
    elif cur_start is None or new_start is None:
        # SESSION STATE block added or removed — that is a state mutation
        sys.stdout.write("true\n")
    else:
        cur_block = current[cur_start:cur_end]
        new_block = new_content[new_start:new_end]
        sys.stdout.write("true\n" if cur_block != new_block else "false\n")

elif "old_string" in params:
    # Edit tool — check whether old_string is located within the SESSION STATE block.
    old_string = params["old_string"]
    if cur_start is None:
        # No SESSION STATE block in current file — nothing to protect
        sys.stdout.write("false\n")
    else:
        pos = current.find(old_string)
        if pos == -1:
            # old_string not found — the Edit will fail anyway; let it through
            sys.stdout.write("false\n")
        else:
            # The edit overlaps SESSION STATE if its position range intersects the block
            edit_end = pos + len(old_string)
            overlaps = pos < cur_end and edit_end > cur_start
            sys.stdout.write("true\n" if overlaps else "false\n")
else:
    sys.stdout.write("false\n")
' "$FILE_PATH" 2>/dev/null || echo "false")"

if [[ "$TOUCHES_SESSION_STATE" != "true" ]]; then
  # Edit does not modify the SESSION STATE block — allow unconditionally
  exit 0
fi

# SESSION STATE is being modified — require a valid lock file

if [[ ! -f "$LOCK_FILE" ]]; then
  echo "BLOCKED: Direct edits to SESSION STATE require the session-open or session-close skill." >&2
  echo "         Use /session-open or /session-close — they manage SESSION STATE transitions." >&2
  echo "         If you are running a session skill and seeing this, the lock file is missing." >&2
  echo "         Lock file expected at: ${LOCK_FILE}" >&2
  exit 2
fi

# Stale lock check.
# LOCK_FILE is passed as a positional argument to python3 to avoid path injection —
# embedding a shell variable inside a Python string literal is unsafe if the path
# contains quotes, backslashes, or newlines.
LOCK_AGE_SECONDS="$(python3 -c "
import os, time, sys
try:
    mtime = os.path.getmtime(sys.argv[1])
    print(int(time.time() - mtime))
except Exception:
    print(9999)
" "$LOCK_FILE" 2>/dev/null || echo "9999")"

if [[ "$LOCK_AGE_SECONDS" -gt "$STALE_THRESHOLD_SECONDS" ]]; then
  echo "BLOCKED: STALE_LOCK_FLAG — tasks/.session-transition-lock is ${LOCK_AGE_SECONDS}s old (threshold: ${STALE_THRESHOLD_SECONDS}s)." >&2
  echo "         A previous session-open or session-close likely crashed before cleanup." >&2
  echo "         Recovery: rm tasks/.session-transition-lock" >&2
  echo "         Then re-run your session skill." >&2
  exit 2
fi

# Verify lock file content is a known skill name
LOCK_CONTENT="$(cat "$LOCK_FILE" 2>/dev/null | tr -d '[:space:]')"
if [[ "$LOCK_CONTENT" != "session-open" && "$LOCK_CONTENT" != "session-close" ]]; then
  echo "BLOCKED: tasks/.session-transition-lock has unexpected content: '${LOCK_CONTENT}'." >&2
  echo "         Expected 'session-open' or 'session-close'." >&2
  echo "         Recovery: rm tasks/.session-transition-lock" >&2
  exit 2
fi

# Lock file is present, fresh, and valid — allow the edit
exit 0

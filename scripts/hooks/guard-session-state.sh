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

# Only care about writes to the live tasks/todo.md — not the project-template copy.
# The pattern *tasks/todo.md would also match project-template/tasks/todo.md without this check.
if [[ "$FILE_PATH" != *"tasks/todo.md" ]]; then
  exit 0
fi
if [[ "$FILE_PATH" == *"project-template"* ]]; then
  exit 0
fi

# Check if the edit touches SESSION STATE
CONTENT="$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
params = data.get('tool_input', {})
content = params.get('content', '') + params.get('new_string', '') + params.get('old_string', '')
print(content)
" 2>/dev/null || echo "")"

if ! echo "$CONTENT" | grep -qi "SESSION STATE\|^Status:"; then
  # Edit does not touch SESSION STATE — allow
  exit 0
fi

# SESSION STATE edit detected — check for valid lock file

if [[ ! -f "$LOCK_FILE" ]]; then
  echo "BLOCKED: Direct edits to SESSION STATE require the session-open or session-close skill." >&2
  echo "         Use /session-open or /session-close — they manage SESSION STATE transitions." >&2
  echo "         If you are running a session skill and seeing this, the lock file is missing." >&2
  echo "         Lock file expected at: ${LOCK_FILE}" >&2
  exit 2
fi

# Check for stale lock (process crash before cleanup)
LOCK_AGE_SECONDS="$(python3 -c "
import os, time
try:
    mtime = os.path.getmtime('${LOCK_FILE}')
    print(int(time.time() - mtime))
except Exception:
    print(9999)
" 2>/dev/null || echo "9999")"

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

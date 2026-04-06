#!/usr/bin/env bash
# guard-session-state.sh — PreToolCall hook
# Blocks unauthorized writes to the SESSION STATE block in tasks/todo.md
#
# Called by Claude Code before Write/Edit tool calls.
# Receives tool call info via stdin as JSON.
#
# PRIMARY PATH — MCP:
#   session-open and session-close call mcp__ak-state-machine__transition_session
#   directly. MCP tool calls are not intercepted by Write/Edit PreToolCall hooks,
#   so they bypass this guard entirely.
#
# FALLBACK PATH — Sentinel file:
#   When MCP is unavailable, session-open/session-close write a sentinel file
#   (.session-state-transition) via Bash BEFORE making any Edit/Write call.
#   This guard checks for the sentinel and allows the write.
#   The sentinel is removed by the skill after the write completes.
#
# This guard is DEFENSE-IN-DEPTH: it blocks accidental direct edits to
# SESSION STATE that come from neither MCP nor the sentinel path.
#
# Exit 0 = allow, Exit 2 = block with message on stderr

set -euo pipefail

INPUT="$(cat)"

# Derive project root from the file path being edited (strip tasks/todo.md suffix)
FILE_PATH="$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
params = data.get('tool_input', {})
print(params.get('file_path', params.get('path', '')))
" 2>/dev/null || echo "")"

# Only care about writes to tasks/todo.md
if [[ "$FILE_PATH" != *"tasks/todo.md" ]]; then
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

if echo "$CONTENT" | grep -qi "SESSION STATE\|^Status:"; then
  # Derive project root: strip trailing /tasks/todo.md
  PROJECT_ROOT="$(echo "$FILE_PATH" | sed 's|/tasks/todo\.md$||')"
  SENTINEL="${PROJECT_ROOT}/.session-state-transition"

  # Allow if sentinel file is present (written by session-open or session-close via Bash)
  if [[ -f "$SENTINEL" ]]; then
    exit 0
  fi

  echo "BLOCKED: Only /session-open and /session-close may modify SESSION STATE. Write the sentinel file first: touch ${SENTINEL}" >&2
  exit 2
fi

exit 0

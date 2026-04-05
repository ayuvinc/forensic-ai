#!/usr/bin/env bash
# guard-session-state.sh — PreToolCall hook
# Blocks unauthorized writes to the SESSION STATE block in tasks/todo.md
#
# Called by Claude Code before Write/Edit tool calls.
# Receives tool call info via stdin as JSON.
#
# MCP IS THE PRIMARY PATH for SESSION STATE transitions.
# session-open and session-close call mcp__ak-state-machine__transition_session
# directly — those writes bypass this hook entirely (MCP tool calls are not
# intercepted by Write/Edit PreToolCall hooks).
#
# This guard is DEFENSE-IN-DEPTH: it blocks any direct Edit/Write to
# tasks/todo.md that touches SESSION STATE without going through the MCP
# server. In normal workflow this guard should never fire — it exists to
# catch accidental direct file edits only.
#
# Environment:
#   ACTIVE_SKILL — set by session-open/session-close skills (or empty)
#
# Exit 0 = allow, Exit 2 = block with message on stderr

set -euo pipefail

INPUT="$(cat)"

# Extract the target file path from the tool call
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
  ALLOWED_SKILLS="session-open session-close"
  CURRENT="${ACTIVE_SKILL:-unknown}"
  for skill in $ALLOWED_SKILLS; do
    if [[ "$CURRENT" == "$skill" ]]; then
      exit 0
    fi
  done
  echo "BLOCKED: Only /session-open and /session-close may modify SESSION STATE. Active skill: ${CURRENT}" >&2
  exit 2
fi

exit 0

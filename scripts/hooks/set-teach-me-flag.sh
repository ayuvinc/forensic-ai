#!/usr/bin/env bash
# set-teach-me-flag.sh — PostToolUse hook (Write|Edit matcher)
# Creates .teach-me-required flag when IN_PROGRESS is written to tasks/todo.md.
# This flag is read by auto-teach.sh (UserPromptSubmit) to block Claude's response.
#
# Exit 0 always — flag creation is best-effort.

set -euo pipefail

INPUT="$(cat)"

FILE_PATH="$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
params = data.get('tool_input', {})
print(params.get('file_path', params.get('path', '')))
" 2>/dev/null || echo "")"

if [[ "$FILE_PATH" != *"tasks/todo.md" ]]; then
  exit 0
fi

CONTENT="$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
params = data.get('tool_input', {})
print(params.get('new_string', params.get('content', '')))
" 2>/dev/null || echo "")"

if ! echo "$CONTENT" | grep -q 'IN_PROGRESS'; then
  exit 0
fi

TASK_ID="$(echo "$CONTENT" | python3 -c "
import sys, re
content = sys.stdin.read()
match = re.search(r'(TASK-\w+)', content)
print(match.group(1) if match else 'unknown')
" 2>/dev/null || echo "unknown")"

# Write flag — auto-teach.sh will block until /teach-me clears it
echo "$TASK_ID" > .teach-me-required

exit 0

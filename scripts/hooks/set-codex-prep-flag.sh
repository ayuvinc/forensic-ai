#!/usr/bin/env bash
# set-codex-prep-flag.sh — PostToolUse hook (Write|Edit matcher)
# Creates .codex-prep-required flag when READY_FOR_REVIEW is written to tasks/todo.md.
# This flag is read by auto-codex-prep.sh (UserPromptSubmit) to block Claude's response.
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

if ! echo "$CONTENT" | grep -q 'READY_FOR_REVIEW'; then
  exit 0
fi

TASK_ID="$(echo "$CONTENT" | python3 -c "
import sys, re
content = sys.stdin.read()
match = re.search(r'(TASK-\w+)', content)
print(match.group(1) if match else 'unknown')
" 2>/dev/null || echo "unknown")"

# Write flag — auto-codex-prep.sh will block until /codex-prep clears it
echo "$TASK_ID" > .codex-prep-required

exit 0

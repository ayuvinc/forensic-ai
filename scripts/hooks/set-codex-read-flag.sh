#!/usr/bin/env bash
# set-codex-read-flag.sh — PostToolUse hook (Write|Edit matcher)
# Creates .codex-read-required flag when VERDICT: is written to tasks/codex-review.md.
# This flag is read by auto-codex-read.sh (UserPromptSubmit) to block Claude's response.
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

if [[ "$FILE_PATH" != *"tasks/codex-review.md" ]]; then
  exit 0
fi

CONTENT="$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
params = data.get('tool_input', {})
print(params.get('new_string', params.get('content', '')))
" 2>/dev/null || echo "")"

# Only fire if VERDICT: is being written (Codex has responded)
if ! echo "$CONTENT" | grep -qE '^VERDICT:'; then
  exit 0
fi

# Don't re-flag if already processed
if echo "$CONTENT" | grep -q 'Status: PROCESSED'; then
  exit 0
fi

TASK_ID="$(grep -E '^## Codex Review' tasks/codex-review.md 2>/dev/null | head -1 | sed 's/.*— //' || echo "unknown task")"

# Write flag — auto-codex-read.sh will block until /codex-read clears it
echo "$TASK_ID" > .codex-read-required

exit 0

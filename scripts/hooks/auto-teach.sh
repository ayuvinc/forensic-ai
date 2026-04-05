#!/usr/bin/env bash
# auto-teach.sh — UserPromptSubmit hook
# BLOCKS Claude's response until /teach-me has been run after a task moves to IN_PROGRESS.
#
# Enforcement mechanism:
#   After IN_PROGRESS is written to tasks/todo.md, a flag file
#   .teach-me-required is created. This hook fires on every user prompt
#   and blocks Claude's response until the flag is cleared.
#   /teach-me clears the flag by writing .teach-me-done.
#
# Flag files (in project root):
#   .teach-me-required   — created when IN_PROGRESS detected, cleared by /teach-me
#
# Exit 0 = allow Claude to respond
# Exit 2 = block Claude's response with message

set -euo pipefail

# Drain stdin (UserPromptSubmit hooks receive prompt JSON — not needed here)
cat > /dev/null 2>&1 || true

FLAG_REQUIRED=".teach-me-required"
FLAG_DONE=".teach-me-done"

# If no flag file, nothing to enforce
if [[ ! -f "$FLAG_REQUIRED" ]]; then
  exit 0
fi

# Check if /teach-me has already been run (flag cleared)
if [[ -f "$FLAG_DONE" ]]; then
  REQUIRED_TASK="$(cat "$FLAG_REQUIRED" 2>/dev/null || echo "unknown")"
  DONE_TASK="$(cat "$FLAG_DONE" 2>/dev/null || echo "unknown")"
  if [[ "$REQUIRED_TASK" == "$DONE_TASK" ]]; then
    rm -f "$FLAG_REQUIRED" "$FLAG_DONE"
    exit 0
  fi
fi

# Still required — block
TASK_ID="$(cat "$FLAG_REQUIRED" 2>/dev/null || echo "the task")"
echo "BLOCKED: /teach-me has not been run for ${TASK_ID}." >&2
echo "" >&2
echo "A task just moved to IN_PROGRESS. Run /teach-me to write the plain-language" >&2
echo "brief to memory/teaching-log.md before any code is written." >&2
echo "" >&2
echo "This is enforced — Claude cannot proceed until /teach-me completes." >&2
exit 2

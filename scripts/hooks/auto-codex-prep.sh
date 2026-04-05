#!/usr/bin/env bash
# auto-codex-prep.sh — UserPromptSubmit hook
# BLOCKS Claude's response until /codex-prep has been run after READY_FOR_REVIEW is set.
#
# Enforcement mechanism:
#   After READY_FOR_REVIEW is written to tasks/todo.md, a flag file
#   .codex-prep-required is created. This hook fires on every user prompt
#   and blocks Claude's response until tasks/codex-review.md exists with content.
#   /codex-prep satisfies the gate by writing tasks/codex-review.md.
#
# Flag files (in project root):
#   .codex-prep-required  — created when READY_FOR_REVIEW detected, cleared when codex-review.md written
#
# Exit 0 = allow Claude to respond
# Exit 2 = block Claude's response with message

set -euo pipefail

# Drain stdin
cat > /dev/null 2>&1 || true

FLAG_REQUIRED=".codex-prep-required"
CODEX_REVIEW="tasks/codex-review.md"

# If no flag file, nothing to enforce
if [[ ! -f "$FLAG_REQUIRED" ]]; then
  exit 0
fi

# Check if /codex-prep has run — tasks/codex-review.md must exist and have content
if [[ -f "$CODEX_REVIEW" ]]; then
  CONTENT_LINES="$(wc -l < "$CODEX_REVIEW" | tr -d ' ')"
  if [[ "$CONTENT_LINES" -gt 5 ]]; then
    # codex-review.md exists with real content — gate satisfied
    rm -f "$FLAG_REQUIRED"
    exit 0
  fi
fi

# Still required — block
TASK_ID="$(cat "$FLAG_REQUIRED" 2>/dev/null || echo "the task")"
echo "BLOCKED: /codex-prep has not been run for ${TASK_ID}." >&2
echo "" >&2
echo "A task was marked READY_FOR_REVIEW. Run /codex-prep to prepare" >&2
echo "tasks/codex-review.md before any QA work begins." >&2
echo "" >&2
echo "Codex review is a hard gate — QA cannot start until /codex-read routes a PASS verdict." >&2
echo "This is enforced — Claude cannot proceed until /codex-prep completes." >&2
exit 2

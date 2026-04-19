#!/usr/bin/env bash
# auto-codex-read.sh — UserPromptSubmit hook
# BLOCKS Claude's response until /codex-read has been run after Codex responds.
#
# Enforcement mechanism (flag-file pattern — same as auto-codex-prep.sh):
#   After VERDICT: is written to tasks/codex-review.md, set-codex-read-flag.sh
#   creates .codex-read-required. This hook fires on every user prompt and blocks
#   Claude's response until the gate is satisfied.
#   Gate is satisfied when tasks/codex-review.md contains "Status: PROCESSED"
#   (written by /codex-read). The hook then clears the flag and exits 0.
#
# This hook NEVER parses stdin — no deadlock possible.
#
# Exit 0 = allow Claude to respond
# Exit 2 = block Claude's response with message

set -euo pipefail

# Drain stdin (UserPromptSubmit hooks receive prompt JSON — not needed here)
cat > /dev/null 2>&1 || true

FLAG_REQUIRED=".codex-read-required"
CODEX_REVIEW="tasks/codex-review.md"

# If no flag file, nothing to enforce
if [[ ! -f "$FLAG_REQUIRED" ]]; then
  exit 0
fi

# Check if /codex-read has already run — gate satisfied when Status: PROCESSED
if [[ -f "$CODEX_REVIEW" ]] && grep -q 'Status: PROCESSED' "$CODEX_REVIEW" 2>/dev/null; then
  rm -f "$FLAG_REQUIRED"
  exit 0
fi

# Still required — block
TASK_ID="$(cat "$FLAG_REQUIRED" 2>/dev/null || echo "the task")"
VERDICT="$(grep -E '^VERDICT:' "$CODEX_REVIEW" 2>/dev/null | tail -1 | awk '{print $2}' || echo "UNKNOWN")"

echo "BLOCKED: /codex-read has not been run for ${TASK_ID}." >&2
echo "" >&2
echo "Codex has responded with VERDICT: ${VERDICT} in tasks/codex-review.md." >&2
echo "Run /codex-read to route the task and write findings to channel.md." >&2
echo "" >&2
echo "This is enforced — Claude cannot proceed until /codex-read completes." >&2
exit 2

#!/usr/bin/env bash
# auto-codex-read.sh — UserPromptSubmit hook
# BLOCKS Claude's response until /codex-read has been run after Codex responds.
#
# Enforcement mechanism:
#   When tasks/codex-review.md contains VERDICT: but Status is not PROCESSED,
#   this hook blocks Claude from doing anything other than running /codex-read.
#   /codex-read satisfies the gate by writing "Status: PROCESSED" to codex-review.md.
#
# Exit 0 = allow Claude to respond
# Exit 2 = block Claude's response with message

set -euo pipefail

# Drain stdin
cat > /dev/null 2>&1 || true

CODEX_REVIEW="tasks/codex-review.md"

# If codex-review.md doesn't exist, nothing to enforce
if [[ ! -f "$CODEX_REVIEW" ]]; then
  exit 0
fi

# Check if VERDICT: is present
if ! grep -qE '^VERDICT:' "$CODEX_REVIEW" 2>/dev/null; then
  exit 0
fi

# Check if already processed — gate satisfied
if grep -q 'Status: PROCESSED' "$CODEX_REVIEW" 2>/dev/null; then
  exit 0
fi

# VERDICT present but not processed — block
VERDICT="$(grep -E '^VERDICT:' "$CODEX_REVIEW" | head -1 | awk '{print $2}' || echo "UNKNOWN")"
TASK_ID="$(grep -E '^## Codex Review' "$CODEX_REVIEW" | head -1 | sed 's/.*— //' || echo "unknown task")"

echo "BLOCKED: /codex-read has not been run for ${TASK_ID}." >&2
echo "" >&2
echo "Codex has responded with VERDICT: ${VERDICT} in tasks/codex-review.md." >&2
echo "Run /codex-read to route the task and write findings to channel.md." >&2
echo "" >&2
echo "This is enforced — Claude cannot proceed until /codex-read completes." >&2
exit 2

#!/usr/bin/env bash
# auto-persona-detect.sh — user-prompt-submit hook
# Reads tasks/next-action.md to detect the expected persona and
# prints a reminder if the user hasn't activated the right one.
#
# This is advisory — it prints to stderr but does not block.

set -euo pipefail

NEXT_ACTION="tasks/next-action.md"

if [[ ! -f "$NEXT_ACTION" ]]; then
  exit 0
fi

# Extract NEXT_PERSONA from next-action.md
EXPECTED_PERSONA="$(python3 -c "
import sys
with open('$NEXT_ACTION', 'r') as f:
    for line in f:
        line = line.strip()
        if line.lower().startswith('next_persona:') or line.lower().startswith('next persona:'):
            val = line.split(':', 1)[1].strip().strip('\"').strip(\"'\")
            if val and val != 'none' and val != '[PERSONA]':
                print(val)
                break
" 2>/dev/null || echo "")"

if [[ -z "$EXPECTED_PERSONA" ]]; then
  exit 0
fi

ACTIVE="${ACTIVE_PERSONA:-}"

# If no persona is set, remind the user
if [[ -z "$ACTIVE" ]]; then
  echo "PERSONA HINT: next-action.md expects persona '${EXPECTED_PERSONA}'. Run /${EXPECTED_PERSONA} to activate." >&2
elif [[ "$ACTIVE" != "$EXPECTED_PERSONA" ]]; then
  echo "PERSONA MISMATCH: Active persona is '${ACTIVE}' but next-action.md expects '${EXPECTED_PERSONA}'. Run /${EXPECTED_PERSONA} to switch." >&2
fi

exit 0

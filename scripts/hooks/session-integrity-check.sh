#!/usr/bin/env bash
# session-integrity-check.sh — Stop hook (runs when Claude Code session ends)
# Warns if SESSION STATE is still OPEN when the user exits.
#
# This is advisory — prints warning to stderr, does not block exit.

set -euo pipefail

TODO_FILE="tasks/todo.md"

if [[ ! -f "$TODO_FILE" ]]; then
  exit 0
fi

# Check if session is still OPEN
if ! grep -q 'Status:.*OPEN' "$TODO_FILE" 2>/dev/null; then
  exit 0
fi

# Gather context for a useful warning

# 1. Next persona from tasks/next-action.md
NEXT_PERSONA=""
if [[ -f "tasks/next-action.md" ]]; then
  NEXT_PERSONA="$(python3 -c "
import sys
try:
    with open('tasks/next-action.md', 'r') as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith('next_persona:'):
                val = line.split(':', 1)[1].strip().strip('\"').strip(\"'\")
                if val and val.lower() not in ('none', '[persona]'):
                    print(val)
                    break
except Exception:
    pass
" 2>/dev/null || echo "")"
fi

# 2. Open task count (PENDING or IN_PROGRESS) from tasks/todo.md
OPEN_TASKS="$(python3 -c "
import re
try:
    with open('tasks/todo.md', 'r') as f:
        content = f.read()
    matches = re.findall(r'^\- Status:\s+(PENDING|IN_PROGRESS)', content, re.MULTILINE)
    print(len(matches))
except Exception:
    print(0)
" 2>/dev/null || echo "0")"

echo "" >&2
echo "================================================================" >&2
echo "  WARNING: Session is still OPEN!" >&2
echo "================================================================" >&2
echo "" >&2
echo "  You are exiting without running /session-close." >&2
echo "  This means:" >&2
echo "    - SESSION STATE remains OPEN in tasks/todo.md" >&2
echo "    - tasks/next-action.md will not be updated" >&2
echo "    - Audit log will be missing SESSION_CLOSED entry" >&2
echo "    - Next session may start with stale context" >&2
echo "" >&2
if [[ -n "$NEXT_PERSONA" ]]; then
  echo "  Next persona: ${NEXT_PERSONA}" >&2
fi
echo "  Open tasks: ${OPEN_TASKS}" >&2
echo "" >&2
echo "  To fix: Re-open Claude Code and run /session-close" >&2
echo "================================================================" >&2

# Advisory check 1: Unprocessed Codex verdict
# Warns if tasks/codex-review.md has a VERDICT line but has not been marked Status: PROCESSED.
# Implements stage-gates.md Pre-Closeout Gate row 4 (STEP-30).
if [[ -f "tasks/codex-review.md" ]]; then
  if grep -q 'VERDICT:' "tasks/codex-review.md" 2>/dev/null; then
    if ! grep -q 'Status: PROCESSED' "tasks/codex-review.md" 2>/dev/null; then
      echo "" >&2
      echo "================================================================" >&2
      echo "  WARNING: Unprocessed Codex verdict detected!" >&2
      echo "================================================================" >&2
      echo "" >&2
      echo "  tasks/codex-review.md contains a VERDICT but has not been" >&2
      echo "  marked Status: PROCESSED. Run /codex-read to process it." >&2
      echo "================================================================" >&2
    fi
  fi
fi

# Advisory check 2: Open BOUNDARY_FLAGs
# Warns if tasks/todo.md contains unresolved BOUNDARY_FLAG entries.
if [[ -f "$TODO_FILE" ]]; then
  FLAG_COUNT="$(grep -cE '^BOUNDARY_FLAG:' "$TODO_FILE" 2>/dev/null || echo "0")"
  if [[ "$FLAG_COUNT" -gt 0 ]]; then
    echo "" >&2
    echo "================================================================" >&2
    echo "  WARNING: Open BOUNDARY_FLAGs detected!" >&2
    echo "================================================================" >&2
    echo "" >&2
    echo "  tasks/todo.md contains ${FLAG_COUNT} unresolved BOUNDARY_FLAG" >&2
    echo "  entries. Resolve all flags before closing the session." >&2
    echo "================================================================" >&2
  fi
fi

# Advisory check 3: Unresolved S0 risks
# Warns if tasks/risk-register.md has any OPEN risk block containing "S0".
# Implements stage-gates.md Pre-Closeout Gate (STEP-30).
if [[ -f "tasks/risk-register.md" ]]; then
  S0_COUNT="$(python3 -c "
import re
try:
    with open('tasks/risk-register.md', 'r') as f:
        content = f.read()
    blocks = re.split(r'(?=^## \[RISK-)', content, flags=re.MULTILINE)
    count = 0
    for block in blocks:
        if (re.search(r'^- Status:\s+OPEN', block, re.MULTILINE) and
                re.search(r'S0', block)):
            count += 1
    print(count)
except Exception:
    print(0)
" 2>/dev/null || echo "0")"
  if [[ "$S0_COUNT" -gt 0 ]]; then
    echo "" >&2
    echo "================================================================" >&2
    echo "  WARNING: Unresolved S0 risk(s) detected!" >&2
    echo "================================================================" >&2
    echo "" >&2
    echo "  tasks/risk-register.md contains ${S0_COUNT} OPEN risk(s) tagged S0." >&2
    echo "  S0 risks require explicit resolution before release." >&2
    echo "  Run /risk-manager to review and update risk status." >&2
    echo "================================================================" >&2
  fi
fi

# Advisory check 4: Governance
# Warns if the governance validator returns WARN or FAIL.
# Advisory only — never exits with non-zero code.
GOVERNANCE_STATUS="$(python3 -m validators.runner . --only governance --format json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('results', [])
    for r in results:
        if r.get('name') == 'governance':
            print(r.get('status', ''))
            break
except Exception:
    pass
" 2>/dev/null || echo "")"

if [[ "$GOVERNANCE_STATUS" == "WARN" || "$GOVERNANCE_STATUS" == "FAIL" ]]; then
  echo "" >&2
  echo "================================================================" >&2
  echo "  WARNING: Governance validator returned ${GOVERNANCE_STATUS}!" >&2
  echo "================================================================" >&2
  echo "" >&2
  echo "  One or more governance checks did not pass." >&2
  echo "  Run: python3 validators/runner.py . --only governance" >&2
  echo "  Resolve before next release push to main." >&2
  echo "================================================================" >&2
fi

exit 0

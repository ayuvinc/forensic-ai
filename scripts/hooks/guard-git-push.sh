#!/usr/bin/env bash
# guard-git-push.sh — PreToolCall hook
# Blocks git push to main/master unless:
#   1. Active persona is Architect
#   2. QA_APPROVED task exists in tasks/todo.md
#   3. tasks/codex-review.md has VERDICT: PASS and Status: PROCESSED (if file exists)
# If tasks/todo.md does not exist (new project), QA_APPROVED check is skipped.
# If tasks/codex-review.md does not exist, Codex gate is skipped with a warning.
#
# Called by Claude Code before Bash tool calls.
# Receives tool call info via stdin as JSON.
#
# Exit 0 = allow, Exit 2 = block with message on stderr

set -euo pipefail

INPUT="$(cat)"

COMMAND="$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")"

# Only care about git push commands
if ! echo "$COMMAND" | grep -qE '^\s*git\s+push'; then
  exit 0
fi

# Block force push always (match flag -f or --force, not substrings like -framework)
if echo "$COMMAND" | grep -qE '(^|\s)--force(\s|$)|(^|\s)-f(\s|$)'; then
  echo "BLOCKED: Force push is not allowed. Use regular push only." >&2
  exit 2
fi

# Helper: check if command targets main/master (branch name or refspec syntax)
targets_main() {
  echo "$1" | grep -qE '\s+(origin\s+)?(main|master)\s*$|\s+(origin\s+)?(main|master)\s' && return 0
  echo "$1" | grep -qE ':(main|master)(\s|$)' && return 0
  return 1
}

# Block push to main/master
if targets_main "$COMMAND"; then
  PERSONA="${ACTIVE_PERSONA:-unknown}"

  # Check persona first
  if [[ "$PERSONA" != "architect" ]]; then
    echo "BLOCKED: Only the Architect persona may push to main/master. Active persona: ${PERSONA}" >&2
    exit 2
  fi

  # Check QA_APPROVED exists in tasks/todo.md (skip if file doesn't exist — new project)
  # Pattern matches "- Status: QA_APPROVED" in an actual task block — not the STATUS LIFECYCLE comment.
  if [[ -f "tasks/todo.md" ]]; then
    if ! grep -qE "^\- Status:[[:space:]]+QA_APPROVED" "tasks/todo.md" 2>/dev/null; then
      echo "BLOCKED: No QA_APPROVED tasks found in tasks/todo.md. Get QA sign-off before pushing to main." >&2
      exit 2
    fi
  fi

  # Check Codex review gate (skip if codex-review.md doesn't exist — warn only)
  if [[ -f "tasks/codex-review.md" ]]; then
    CODEX_VERDICT="$(grep -E '^VERDICT:' "tasks/codex-review.md" 2>/dev/null | head -1 | awk '{print $2}' || echo "")"
    CODEX_STATUS="$(grep -E '^Status:' "tasks/codex-review.md" 2>/dev/null | head -1 | awk '{print $2}' || echo "")"

    if [[ "$CODEX_VERDICT" == "FAIL" ]]; then
      echo "BLOCKED: Codex review returned FAIL for the last reviewed task. Fix Codex findings before pushing to main." >&2
      echo "         Run /codex-read to see the routing, or check channel.md for findings." >&2
      exit 2
    fi

    if [[ "$CODEX_STATUS" == "AWAITING_CODEX" ]]; then
      echo "BLOCKED: tasks/codex-review.md is awaiting Codex response. Invoke Codex on the file before pushing." >&2
      exit 2
    fi

    if [[ "$CODEX_VERDICT" != "PASS" ]]; then
      echo "WARNING: tasks/codex-review.md exists but VERDICT is missing or unrecognised ('${CODEX_VERDICT}'). Proceeding with caution." >&2
    fi
  else
    echo "WARNING: tasks/codex-review.md not found — Codex review gate skipped. Consider running /codex-prep before merge." >&2
  fi

  # Security/compliance gate (Standard and High-Risk tiers only; skip for MVP)
  # Blocks push when tasks/risk-register.md has any OPEN entry with Category: Security.
  # This implements stage-gates.md Pre-Release Gate rows 4-5 (STEP-29).
  TIER_SEC=""
  if [[ -f "CLAUDE.md" ]]; then
    TIER_SEC="$(grep -E '^Tier:' CLAUDE.md 2>/dev/null | head -1 | awk '{print $2}' || echo "")"
  fi

  if [[ "$TIER_SEC" != "MVP" ]]; then
    if [[ -f "tasks/risk-register.md" ]]; then
      OPEN_SECURITY_RISKS="$(python3 -c "
import re, sys
try:
    with open('tasks/risk-register.md', 'r') as f:
        content = f.read()
    blocks = re.split(r'(?=^## \[RISK-)', content, flags=re.MULTILINE)
    found = []
    for block in blocks:
        if (re.search(r'^- Status:\s+OPEN', block, re.MULTILINE) and
                re.search(r'^- Category:\s+Security', block, re.MULTILINE)):
            m = re.search(r'^## \[(RISK-\d+)\]', block, re.MULTILINE)
            if m:
                found.append(m.group(1))
    print(' '.join(found))
except Exception:
    pass
" 2>/dev/null || echo "")"
      if [[ -n "$OPEN_SECURITY_RISKS" ]]; then
        echo "BLOCKED: Open security risks must be resolved before pushing to main." >&2
        echo "         OPEN security entries: ${OPEN_SECURITY_RISKS}" >&2
        echo "         Run /security-sweep, update tasks/risk-register.md to MITIGATED, then retry." >&2
        exit 2
      fi
    else
      echo "WARNING: tasks/risk-register.md not found — security risk gate skipped." >&2
    fi
  fi

  # Governance gate — checks Phase 10 governance docs and version stamp.
  # FAIL blocks push (exit 2); WARN allows push with a warning message.
  # Runs only inside this targets_main block (non-main pushes are unaffected).
  GOVERNANCE_OUTPUT="$(python3 -m validators.runner . --only governance --format json 2>/dev/null || echo "")"
  GOVERNANCE_STATUS="$(echo "$GOVERNANCE_OUTPUT" | python3 -c "
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

  if [[ "$GOVERNANCE_STATUS" == "FAIL" ]]; then
    echo "BLOCKED: governance validator returned FAIL. Resolve governance issues before pushing to main." >&2
    echo "         Run: python3 validators/runner.py . --only governance" >&2
    exit 2
  fi

  if [[ "$GOVERNANCE_STATUS" == "WARN" ]]; then
    echo "WARNING: governance validator returned WARN. Review governance issues before release." >&2
    echo "         Run: python3 validators/runner.py . --only governance" >&2
  fi
fi

exit 0

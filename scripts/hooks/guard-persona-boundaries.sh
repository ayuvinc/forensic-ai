#!/usr/bin/env bash
# guard-persona-boundaries.sh — PreToolCall hook
# Enforces CAN/CANNOT file-path restrictions per persona.
#
# Called by Claude Code before Write/Edit tool calls.
# Receives tool call info via stdin as JSON.
#
# Environment:
#   ACTIVE_PERSONA — set from SESSION STATE (e.g., "junior-dev", "architect")
#
# Exit 0 = allow, Exit 2 = block with message on stderr

set -euo pipefail

INPUT="$(cat)"

FILE_PATH="$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
params = data.get('tool_input', {})
print(params.get('file_path', params.get('path', '')))
" 2>/dev/null || echo "")"

PERSONA="${ACTIVE_PERSONA:-}"

# No persona set = no enforcement (framework-level work)
if [[ -z "$PERSONA" ]]; then
  exit 0
fi

# Define blocked paths per persona
case "$PERSONA" in
  junior-dev)
    # Junior Dev cannot modify: types/, shared services, config files, tasks/ management files
    BLOCKED_PATTERNS=(
      "*/types/*"
      "*/lib/*"
      "*/middleware/*"
      "*/tasks/todo.md"
      "*/tasks/next-action.md"
      "*/tasks/risk-register.md"
      "*/tasks/roadmap.md"
      "*/releases/*"
      "*CLAUDE.md"
      "*.claude/settings.json"
    )
    for pattern in "${BLOCKED_PATTERNS[@]}"; do
      # shellcheck disable=SC2254
      if [[ "$FILE_PATH" == $pattern ]]; then
        echo "BLOCKED: Persona 'junior-dev' cannot write to ${FILE_PATH}. This path requires Architect approval." >&2
        exit 2
      fi
    done
    ;;
  qa)
    # QA cannot modify source code — only tasks/ and test files
    if [[ "$FILE_PATH" != *"tasks/"* && "$FILE_PATH" != *"test"* && "$FILE_PATH" != *"spec"* && "$FILE_PATH" != *".test."* ]]; then
      echo "BLOCKED: Persona 'qa' cannot write to ${FILE_PATH}. QA may only modify tasks/ and test files." >&2
      exit 2
    fi
    ;;
  ba)
    # BA can only write to tasks/ba-logic.md and docs/
    if [[ "$FILE_PATH" != *"tasks/ba-logic.md" && "$FILE_PATH" != *"docs/"* && "$FILE_PATH" != *"channel.md" ]]; then
      echo "BLOCKED: Persona 'ba' cannot write to ${FILE_PATH}. BA may only modify tasks/ba-logic.md, docs/, and channel.md." >&2
      exit 2
    fi
    ;;
  ux)
    # UX can only write to tasks/ux-specs.md and docs/
    if [[ "$FILE_PATH" != *"tasks/ux-specs.md" && "$FILE_PATH" != *"docs/"* && "$FILE_PATH" != *"channel.md" ]]; then
      echo "BLOCKED: Persona 'ux' cannot write to ${FILE_PATH}. UX may only modify tasks/ux-specs.md, docs/, and channel.md." >&2
      exit 2
    fi
    ;;
  # architect, designer, researcher, compliance — no path restrictions (by design)
esac

exit 0

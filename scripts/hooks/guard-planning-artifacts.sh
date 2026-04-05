#!/usr/bin/env bash
# guard-planning-artifacts.sh — PreToolUse hook
# Blocks Junior Dev from writing source code when required planning documents are missing.
# Only enforces for the junior-dev persona on Standard and High-Risk tier projects.
# MVP tier projects (Tier: MVP in CLAUDE.md) are exempt.
# Missing Tier field in CLAUDE.md defaults to Standard (enforce).
#
# Called by Claude Code before Write and Edit tool calls.
# Receives tool call info via stdin as JSON.
#
# Exit 0 = allow, Exit 2 = block with message on stderr

set -euo pipefail

INPUT="$(cat)"

# Only enforce for Junior Dev persona
PERSONA="${ACTIVE_PERSONA:-unknown}"
if [[ "$PERSONA" != "junior-dev" ]]; then
  exit 0
fi

# Check tier — skip enforcement for MVP projects
TIER=""
if [[ -f "CLAUDE.md" ]]; then
  TIER="$(grep -E '^Tier:' CLAUDE.md 2>/dev/null | head -1 | awk '{print $2}' || echo "")"
fi
if [[ "$TIER" == "MVP" ]]; then
  exit 0
fi

# Parse file path from tool input (handles both file_path and path keys)
FILE_PATH="$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    params = data.get('tool_input', {})
    print(params.get('file_path', params.get('path', '')))
except Exception:
    print('')
" 2>/dev/null || echo "")"

# Skip if no path — cannot determine write target, allow through
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Skip excluded paths: planning docs, config, framework artifacts, and tool files
# These paths are legitimate targets regardless of planning doc state
EXCLUDED_PATTERN="^(tasks/|docs/|framework/|\.claude/|scripts/|schemas/|validators/|project-template/|guides/|releases/|memory/|mcp-servers/|CLAUDE|README|QUICKSTART|\.ak-cogos|\.gitignore|\.claudeignore|channel\.md)"
if echo "$FILE_PATH" | grep -qE "$EXCLUDED_PATTERN"; then
  exit 0
fi

# Check required planning documents
MISSING=""
if [[ ! -f "docs/problem-definition.md" ]]; then
  MISSING="${MISSING}  - docs/problem-definition.md\n"
fi
if [[ ! -f "docs/scope-brief.md" ]]; then
  MISSING="${MISSING}  - docs/scope-brief.md\n"
fi
if [[ ! -f "docs/hld.md" ]]; then
  MISSING="${MISSING}  - docs/hld.md\n"
fi

if [[ -n "$MISSING" ]]; then
  echo "BLOCKED: Junior Dev cannot write source code — required planning documents are missing." >&2
  echo "Missing:" >&2
  printf "${MISSING}" >&2
  echo "" >&2
  echo "Run /ba to create docs/problem-definition.md, then /architect to create" >&2
  echo "docs/scope-brief.md and docs/hld.md before implementing any feature work." >&2
  echo "MVP projects (Tier: MVP in CLAUDE.md) are exempt from this gate." >&2
  exit 2
fi

exit 0

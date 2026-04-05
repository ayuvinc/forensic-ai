#!/usr/bin/env bash
# validate-envelope.sh — PostToolCall hook
# Validates that skill/persona output contains the required 10-field envelope.
#
# Called by Claude Code after tool calls complete.
# Reads tool result from stdin as JSON.
#
# Exit 0 = pass (always — this is advisory, not blocking)
# Writes warnings to stderr which Claude Code surfaces to the user.

set -euo pipefail

INPUT="$(cat)"

# Extract the tool result text
python3 -c "
import sys, json

data = json.load(sys.stdin)
output = data.get('tool_result', data.get('stdout', ''))
if not isinstance(output, str):
    output = json.dumps(output)

# Only check outputs that look like they contain envelope fields
# (at least 3 envelope keywords present = likely a skill output)
envelope_fields = [
    'run_id', 'agent', 'origin', 'status', 'timestamp_utc',
    'summary', 'failures', 'warnings', 'artifacts_written', 'next_action'
]

matches = sum(1 for f in envelope_fields if f + ':' in output or f + '\"' in output)

# If fewer than 3 envelope fields detected, this isn't a skill output — skip
if matches < 3:
    sys.exit(0)

# It looks like a skill output — check for all 10 fields
missing = []
for field in envelope_fields:
    if field + ':' not in output and field + '\"' not in output:
        missing.append(field)

if missing:
    print(f'ENVELOPE WARNING: Skill output is missing required fields: {missing}', file=sys.stderr)
    print(f'See schemas/output-envelope.md for the required 10-field contract.', file=sys.stderr)

sys.exit(0)
" <<< "$INPUT" 2>/dev/null || true

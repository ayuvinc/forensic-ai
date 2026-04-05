#!/usr/bin/env bash
# auto-audit-log.sh — PostToolCall hook (Notification)
# Auto-appends audit entries after skill execution completes.
#
# Called after any slash command completes.
# Looks for output envelope fields in the tool result and appends to audit log.
# Primary path: MCP ak-audit-log tool (append_audit_entry).
# Fallback path: direct file append if MCP is unavailable.
#
# This is a best-effort hook — it will not block on failure.

set -euo pipefail

INPUT="$(cat)"

# Extract envelope fields from tool result
ENVELOPE="$(echo "$INPUT" | python3 -c "
import sys, json

data = json.load(sys.stdin)
output = data.get('tool_result', data.get('stdout', ''))
if not isinstance(output, str):
    output = json.dumps(output)

envelope_fields = [
    'run_id', 'agent', 'origin', 'status', 'timestamp_utc',
    'summary', 'failures', 'warnings', 'artifacts_written', 'next_action'
]
matches = sum(1 for f in envelope_fields if f + ':' in output or f + '\"' in output)

# If fewer than 3 envelope fields detected, this is not a skill output — skip
if matches < 3:
    sys.exit(0)

run_id = ''
agent = ''
status = ''
summary = ''

for line in output.splitlines():
    line = line.strip()
    if line.startswith('run_id:'):
        run_id = line.split(':', 1)[1].strip().strip('\"')
    elif line.startswith('agent:'):
        agent = line.split(':', 1)[1].strip().strip('\"')
    elif line.startswith('status:'):
        status = line.split(':', 1)[1].strip().strip('\"')
    elif line.startswith('summary:'):
        summary = line.split(':', 1)[1].strip().strip('\"')

if run_id and agent and status:
    import json as j
    print(j.dumps({'run_id': run_id, 'agent': agent, 'status': status, 'summary': summary}))
" 2>/dev/null || echo "")"

if [[ -z "$ENVELOPE" ]]; then
  exit 0
fi

# Parse extracted fields
RUN_ID="$(echo "$ENVELOPE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('run_id',''))" 2>/dev/null || echo "")"
AGENT="$(echo "$ENVELOPE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('agent',''))" 2>/dev/null || echo "")"
STATUS="$(echo "$ENVELOPE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || echo "")"
SUMMARY="$(echo "$ENVELOPE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('summary',''))" 2>/dev/null || echo "")"

if [[ -z "$RUN_ID" || -z "$AGENT" || -z "$STATUS" ]]; then
  exit 0
fi

# ----- PRIMARY PATH: MCP audit log tool -----
# Attempt to call mcp__ak-audit-log__append_audit_entry via the MCP server.
# The MCP server handles duplicate-run-id protection and atomic writes.
MCP_RESULT="$(python3 -c "
import sys, json, subprocess, os

payload = {
    'run_id': sys.argv[1],
    'agent': sys.argv[2],
    'status': sys.argv[3],
    'summary': sys.argv[4],
}

# Attempt to import and call the audit log server logic directly
# (avoids subprocess round-trip; falls back gracefully on ImportError)
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath('.')), 'mcp-servers'))
    sys.path.insert(0, 'mcp-servers')
    from audit_log_server import append_audit_entry
    result = append_audit_entry(
        run_id=payload['run_id'],
        agent=payload['agent'],
        status=payload['status'],
        summary=payload['summary'],
    )
    print(json.dumps(result))
except ImportError:
    print(json.dumps({'success': False, 'error': 'MCP_UNAVAILABLE'}))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
" "$RUN_ID" "$AGENT" "$STATUS" "$SUMMARY" 2>/dev/null || echo '{"success":false,"error":"MCP_UNAVAILABLE"}')"

MCP_SUCCESS="$(echo "$MCP_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")"

if [[ "$MCP_SUCCESS" == "True" ]]; then
  exit 0
fi

# ----- FALLBACK PATH: direct file append -----
echo "WARN: MCP audit log unavailable — falling back to direct file append." >&2

AUDIT_LOG=""
for candidate in "tasks/audit-log.md" "releases/audit-log.md"; do
  if [[ -f "$candidate" ]]; then
    AUDIT_LOG="$candidate"
    break
  fi
done

if [[ -z "$AUDIT_LOG" ]]; then
  exit 0
fi

TS="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || echo 'unknown')"
SUMMARY_SAFE="${SUMMARY//|/\\|}"
echo "| ${TS} | ${AGENT} | ${STATUS} | ${RUN_ID} | ${SUMMARY_SAFE} |" >> "$AUDIT_LOG"

exit 0

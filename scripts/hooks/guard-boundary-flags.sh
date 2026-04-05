#!/usr/bin/env bash
# guard-boundary-flags.sh — UserPromptSubmit hook
# Warns when unresolved BOUNDARY_FLAG entries exist in tasks/todo.md.
#
# Called by Claude Code on each user prompt submission.
# Reads tasks/todo.md and checks each task block for unresolved BOUNDARY_FLAGs.
# A BOUNDARY_FLAG is considered resolved if the word RESOLVED appears
# anywhere within the same task block.
#
# Advisory only — exit 0 in all code paths. Never blocks.

set -euo pipefail

# Consume stdin (UserPromptSubmit hooks receive prompt JSON via stdin)
# We don't use it, but must drain it to avoid broken pipe errors.
cat > /dev/null 2>&1 || true

TODO_FILE="tasks/todo.md"

if [[ ! -f "$TODO_FILE" ]]; then
  exit 0
fi

# Use python3 to parse task blocks and detect unresolved BOUNDARY_FLAGs
UNRESOLVED="$(python3 -c "
import re, sys

try:
    with open('$TODO_FILE', 'r') as f:
        content = f.read()
except Exception:
    sys.exit(0)

unresolved = []

# Find all task blocks: <!-- TASK-NNN --> ... <!-- /TASK-NNN -->
block_pattern = re.compile(
    r'<!--\s*(TASK-\w+)\s*-->(.*?)<!--\s*/TASK-\w+\s*-->',
    re.DOTALL
)

for match in block_pattern.finditer(content):
    task_id = match.group(1)
    block_text = match.group(2)
    if 'BOUNDARY_FLAG' in block_text and 'RESOLVED' not in block_text:
        unresolved.append(task_id)

# Also check lines outside any task block
outside = block_pattern.sub('', content)
for line in outside.splitlines():
    if 'BOUNDARY_FLAG' in line and 'RESOLVED' not in line:
        unresolved.append('(outside task block)')
        break

if unresolved:
    print(' '.join(unresolved))
" 2>/dev/null || true)"

if [[ -n "$UNRESOLVED" ]]; then
  echo "" >&2
  echo "BOUNDARY_FLAG WARNING: Unresolved BOUNDARY_FLAG entries in tasks/todo.md: ${UNRESOLVED}" >&2
  echo "  Architect must resolve all BOUNDARY_FLAG entries before merging." >&2
fi

exit 0

#!/usr/bin/env python3
"""
audit_log_server.py — MCP Server for AK Cognitive OS append-only audit log.

Exposes two tools:
  append_audit_entry()   — append one row to the audit log (append-only)
  get_recent_entries()   — return last N entries from the audit log

Transport: stdio
Env:
  PROJECT_ROOT    — path to project root (default: ".")
  AUDIT_LOG_PATH  — explicit path to audit log file (overrides discovery)
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import mcp.server.stdio
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    sys.stderr.write("ERROR: mcp package not installed. Run: pip install mcp>=1.0.0\n")
    sys.exit(1)

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", ".")).resolve()

# --------------------------------------------------------------------------- #
# Audit log path resolution
# --------------------------------------------------------------------------- #

def _resolve_audit_log() -> Path:
    """Resolve audit log path: env var → tasks/audit-log.md → releases/audit-log.md."""
    explicit = os.environ.get("AUDIT_LOG_PATH", "")
    if explicit:
        p = Path(explicit)
        return p if p.is_absolute() else PROJECT_ROOT / p

    candidates = [
        PROJECT_ROOT / "tasks" / "audit-log.md",
        PROJECT_ROOT / "releases" / "audit-log.md",
    ]
    for c in candidates:
        if c.exists():
            return c

    # Default to tasks/audit-log.md (will be created on first write)
    return PROJECT_ROOT / "tasks" / "audit-log.md"


# --------------------------------------------------------------------------- #
# Tool implementations
# --------------------------------------------------------------------------- #

def append_audit_entry(
    run_id: str,
    agent: str,
    status: str,
    summary: str,
    timestamp_utc: str = "",
) -> dict:
    """Append one row to the audit log. Append-only — no update, no delete."""
    if not run_id:
        return {"success": False, "error": "run_id is required"}
    if not agent:
        return {"success": False, "error": "agent is required"}
    if not status:
        return {"success": False, "error": "status is required"}
    if not summary:
        return {"success": False, "error": "summary is required"}

    if not timestamp_utc:
        timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    log_path = _resolve_audit_log()

    # Ensure parent directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize file with header if it doesn't exist
    if not log_path.exists():
        header = (
            "# Audit Log\n\n"
            "| Timestamp | Agent | Status | Run ID | Summary |\n"
            "|-----------|-------|--------|--------|---------|\n"
        )
        log_path.write_text(header, encoding="utf-8")

    # DUPLICATE_RUN_ID check: scan last 100 lines
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_100 = lines[-100:] if len(lines) > 100 else lines
        for line in last_100:
            if run_id in line:
                return {"success": False, "error": f"DUPLICATE_RUN_ID: run_id '{run_id}' already exists in audit log"}
    except OSError as e:
        return {"success": False, "error": f"AUDIT_LOG_NOT_FOUND: cannot read audit log — {e}"}

    # Sanitize pipe characters in summary to avoid breaking table format
    summary_safe = summary.replace("|", "\\|")

    row = f"| {timestamp_utc} | {agent} | {status} | {run_id} | {summary_safe} |\n"

    # Append-only write
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(row)
    except OSError as e:
        return {"success": False, "error": f"WRITE_FAILED: {e}"}

    # Generate a stable entry_id from run_id + timestamp
    entry_id = f"{run_id}:{timestamp_utc}"
    return {"success": True, "entry_id": entry_id, "log_path": str(log_path)}


def get_recent_entries(n: int = 10) -> list:
    """Return last N data rows from the audit log as list of dicts."""
    log_path = _resolve_audit_log()

    if not log_path.exists():
        return []

    try:
        text = log_path.read_text(encoding="utf-8")
    except OSError:
        return []

    # Parse markdown table rows (skip header rows and empty lines)
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip header/separator rows
        if re.match(r"^\|[-| ]+\|$", line):
            continue
        if "Timestamp" in line and "Agent" in line:
            continue

        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) >= 5:
            entries.append({
                "timestamp_utc": parts[0],
                "agent": parts[1],
                "status": parts[2],
                "run_id": parts[3],
                "summary": parts[4].replace("\\|", "|"),
            })

    return entries[-n:] if len(entries) > n else entries


# --------------------------------------------------------------------------- #
# MCP server wiring
# --------------------------------------------------------------------------- #

server = Server("ak-audit-log")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="append_audit_entry",
            description=(
                "Append one row to the audit log. Append-only — no updates, no deletes. "
                "Returns {success, entry_id, log_path, error?}. "
                "Errors: DUPLICATE_RUN_ID, AUDIT_LOG_NOT_FOUND, WRITE_FAILED."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "Unique ID for this run (e.g. session-4-architect-001)",
                    },
                    "agent": {
                        "type": "string",
                        "description": "Persona/agent name (e.g. Architect, QA, Junior Dev)",
                    },
                    "status": {
                        "type": "string",
                        "description": "Outcome status (e.g. COMPLETE, QA_APPROVED, QA_REJECTED, FAILED)",
                    },
                    "summary": {
                        "type": "string",
                        "description": "One-line summary of what was done",
                    },
                    "timestamp_utc": {
                        "type": "string",
                        "description": "ISO 8601 UTC timestamp (optional — defaults to now)",
                    },
                },
                "required": ["run_id", "agent", "status", "summary"],
            },
        ),
        Tool(
            name="get_recent_entries",
            description=(
                "Return the last N entries from the audit log as a list of dicts. "
                "Each entry has: timestamp_utc, agent, status, run_id, summary."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of recent entries to return (default: 10)",
                        "default": 10,
                    }
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "append_audit_entry":
        result = append_audit_entry(
            run_id=arguments.get("run_id", ""),
            agent=arguments.get("agent", ""),
            status=arguments.get("status", ""),
            summary=arguments.get("summary", ""),
            timestamp_utc=arguments.get("timestamp_utc", ""),
        )
    elif name == "get_recent_entries":
        n = int(arguments.get("n", 10))
        result = get_recent_entries(n)
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

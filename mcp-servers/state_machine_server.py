#!/usr/bin/env python3
"""
state_machine_server.py — MCP Server for AK Cognitive OS session state management.

Exposes three tools:
  get_session_state()       — read current SESSION STATE from tasks/todo.md
  transition_session()      — CLOSED→OPEN or OPEN→CLOSED transition
  set_active_persona()      — update Active persona field (session must be OPEN)

Transport: stdio
Env:
  PROJECT_ROOT — path to project root (default: ".")
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
TODO_PATH = PROJECT_ROOT / "tasks" / "todo.md"

# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #

SESSION_STATE_HEADER = "## SESSION STATE"

STATE_FIELDS = {
    "status":         re.compile(r"^Status:\s*(.+)$", re.MULTILINE),
    "active_task":    re.compile(r"^Active task:\s*(.+)$", re.MULTILINE),
    "active_persona": re.compile(r"^Active persona:\s*(.+)$", re.MULTILINE),
    "blocking_issue": re.compile(r"^Blocking issue:\s*(.+)$", re.MULTILINE),
    "last_updated":   re.compile(r"^Last updated:\s*(.+)$", re.MULTILINE),
}


def _read_todo() -> str:
    if not TODO_PATH.exists():
        raise FileNotFoundError(f"tasks/todo.md not found at {TODO_PATH}")
    return TODO_PATH.read_text(encoding="utf-8")


def _session_block(text: str) -> str:
    """Return the text from ## SESSION STATE to the next ## heading (or EOF)."""
    idx = text.find(SESSION_STATE_HEADER)
    if idx == -1:
        raise ValueError("SESSION_STATE_MISSING: '## SESSION STATE' block not found in tasks/todo.md")
    rest = text[idx:]
    # Find next ## heading after the block header
    next_heading = re.search(r"\n##\s", rest[len(SESSION_STATE_HEADER):])
    if next_heading:
        return rest[: len(SESSION_STATE_HEADER) + next_heading.start()]
    return rest


def _parse_state(block: str) -> dict:
    state = {}
    for key, pattern in STATE_FIELDS.items():
        m = pattern.search(block)
        state[key] = m.group(1).strip() if m else ""
    return state


def _write_field(text: str, field_label: str, new_value: str) -> str:
    """Replace a field value in the SESSION STATE block."""
    pattern = re.compile(rf"^({re.escape(field_label)}:\s*)(.+)$", re.MULTILINE)
    if not pattern.search(text):
        raise ValueError(f"Field '{field_label}' not found in tasks/todo.md")
    return pattern.sub(rf"\g<1>{new_value}", text, count=1)


def _write_todo(content: str) -> None:
    TODO_PATH.write_text(content, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Tool implementations
# --------------------------------------------------------------------------- #

def get_session_state() -> dict:
    try:
        text = _read_todo()
        block = _session_block(text)
        return _parse_state(block)
    except FileNotFoundError as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": str(e)}


def transition_session(to_state: str) -> dict:
    valid_states = {"OPEN", "CLOSED"}
    if to_state not in valid_states:
        return {"success": False, "error": f"INVALID_TRANSITION: to_state must be OPEN or CLOSED, got '{to_state}'"}

    try:
        text = _read_todo()
        block = _session_block(text)
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    except ValueError as e:
        return {"success": False, "error": str(e)}

    state = _parse_state(block)
    current = state.get("status", "").upper()

    legal = {
        "OPEN": "CLOSED",    # CLOSED → OPEN
        "CLOSED": "OPEN",    # OPEN → CLOSED
    }
    if to_state not in legal or legal[to_state] != current:
        return {
            "success": False,
            "error": f"INVALID_TRANSITION: cannot go from '{current}' to '{to_state}'. "
                     f"Legal transitions: CLOSED→OPEN, OPEN→CLOSED",
            "current_state": current,
        }

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        new_text = _write_field(text, "Status", to_state)
        new_text = _write_field(new_text, "Last updated", f"{timestamp} — state transition by MCP server")
        _write_todo(new_text)
    except Exception as e:
        return {"success": False, "error": f"WRITE_FAILED: {e}"}

    # Verify the write
    try:
        verify_text = _read_todo()
        verify_block = _session_block(verify_text)
        verify_state = _parse_state(verify_block)
        if verify_state.get("status", "").upper() != to_state:
            return {"success": False, "error": "WRITE_FAILED: post-write verification mismatch"}
    except Exception as e:
        return {"success": False, "error": f"WRITE_FAILED: verification error — {e}"}

    return {"success": True, "previous_state": current, "new_state": to_state}


def set_active_persona(persona: str) -> dict:
    try:
        text = _read_todo()
        block = _session_block(text)
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    except ValueError as e:
        return {"success": False, "error": str(e)}

    state = _parse_state(block)
    if state.get("status", "").upper() != "OPEN":
        return {
            "success": False,
            "error": "INVALID_TRANSITION: set_active_persona is only allowed when Status == OPEN",
        }

    try:
        new_text = _write_field(text, "Active persona", persona)
        _write_todo(new_text)
    except Exception as e:
        return {"success": False, "error": f"WRITE_FAILED: {e}"}

    return {"success": True, "active_persona": persona}


# --------------------------------------------------------------------------- #
# MCP server wiring
# --------------------------------------------------------------------------- #

server = Server("ak-state-machine")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_session_state",
            description=(
                "Read the current SESSION STATE from tasks/todo.md. "
                "Returns status, active_task, active_persona, blocking_issue, last_updated."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="transition_session",
            description=(
                "Transition session state: CLOSED→OPEN or OPEN→CLOSED. "
                "Illegal transitions are rejected. "
                "Returns {success, previous_state, new_state, error?}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "to_state": {
                        "type": "string",
                        "enum": ["OPEN", "CLOSED"],
                        "description": "Target session state",
                    }
                },
                "required": ["to_state"],
            },
        ),
        Tool(
            name="set_active_persona",
            description=(
                "Update the Active persona field in SESSION STATE. "
                "Only allowed when Status == OPEN. "
                "Returns {success, active_persona, error?}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "persona": {
                        "type": "string",
                        "description": "Persona name to set as active (e.g. Architect, QA, Junior Dev)",
                    }
                },
                "required": ["persona"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_session_state":
        result = get_session_state()
    elif name == "transition_session":
        to_state = arguments.get("to_state", "")
        result = transition_session(to_state)
    elif name == "set_active_persona":
        persona = arguments.get("persona", "")
        result = set_active_persona(persona)
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

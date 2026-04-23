"""Crash report writer for Streamlit page and pipeline error boundaries.

write_crash_report() captures exception details and sanitised session context
and writes a JSON file to logs/crash_reports/ that Maher can share with Claude
for diagnosis. Case content is never included.
"""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path


_CRASH_DIR = Path(__file__).parent.parent.parent / "logs" / "crash_reports"
_ACTIVITY_LOG = Path(__file__).parent.parent.parent / "logs" / "activity.jsonl"


def write_crash_report(page_name: str, exception: Exception) -> str:
    """Write a crash report JSON and return the file path as a string.

    Captures: exception type/message/traceback, sanitised session context
    (active_project slug, workflow type, pipeline status only), and the last
    10 lines of the activity log.

    Never reads from cases/ — no case content is included.
    """
    _CRASH_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc)
    filename = f"crash_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    path = _CRASH_DIR / filename

    session_context = _read_session_context()
    recent_activity = _read_recent_activity()

    report = {
        "timestamp_utc": timestamp.isoformat(),
        "page": Path(page_name).name,
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "traceback": traceback.format_exc(),
        "session_context": session_context,
        "recent_activity": recent_activity,
    }

    try:
        path.write_text(json.dumps(report, indent=2, default=str))
    except Exception:
        # If we can't write the report, return a best-effort path
        pass

    return str(path)


def _read_session_context() -> dict:
    """Extract only slug/workflow/status from st.session_state — no case content."""
    try:
        import streamlit as st
        state = st.session_state

        pipeline_status = None
        active_project = state.get("active_project")
        if active_project:
            try:
                from tools.file_tools import load_state
                s = load_state(active_project)
                pipeline_status = s.get("status") if s else None
            except Exception:
                pass

        return {
            "active_project": active_project,
            "active_workflow_type": state.get("active_workflow_type"),
            "pipeline_status": pipeline_status,
        }
    except Exception:
        return {"active_project": None, "active_workflow_type": None, "pipeline_status": None}


def _read_recent_activity() -> list:
    """Return last 10 lines of logs/activity.jsonl, or [] if absent."""
    try:
        if not _ACTIVITY_LOG.exists():
            return []
        lines = _ACTIVITY_LOG.read_text().strip().splitlines()
        recent = lines[-10:]
        return [json.loads(line) for line in recent]
    except Exception:
        return []

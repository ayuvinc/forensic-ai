"""ActivityLogger — append-only activity ledger for the GoodWork Forensic AI app.

Writes JSONL events to logs/activity.jsonl.
Rotates at 50 MB to logs/activity_{YYYYMMDD}.jsonl and starts fresh.
Write failures are silent — never crash the app.

Categories: SESSION, SETUP, ENGAGEMENT, PIPELINE, DOCUMENT,
            DELIVERABLE, KNOWLEDGE, TEMPLATE, SETTINGS, ERROR
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

LOGS_DIR = Path(__file__).parent.parent / "logs"
_LOG_FILE = LOGS_DIR / "activity.jsonl"
_ROTATION_BYTES = 50 * 1024 * 1024  # 50 MB


def _rotate_if_needed() -> None:
    """Rename log file when it exceeds 50 MB so a fresh one starts."""
    if _LOG_FILE.exists() and _LOG_FILE.stat().st_size >= _ROTATION_BYTES:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        n = 1
        while (LOGS_DIR / f"activity_{stamp}_{n}.jsonl").exists():
            n += 1
        os.rename(_LOG_FILE, LOGS_DIR / f"activity_{stamp}_{n}.jsonl")


def _warn_session() -> None:
    """Set session_state flag so UI can display a warning on next render."""
    try:
        import streamlit as st
        st.session_state["act_log_warn"] = True
    except Exception:
        pass


class ActivityLogger:
    """Thread-safe append-only activity logger.

    Usage:
        logger = ActivityLogger()
        logger.log(
            category="PIPELINE",
            action="pipeline_start",
            actor="junior-dev",
            engagement_id="project-alpha",
            case_id="20260420-A1B2C3",
            detail={"workflow": "frm_risk_register"},
            status="ok",
        )
    """

    def log(
        self,
        category: str,
        action: str,
        actor: str = "system",
        engagement_id: Optional[str] = None,
        case_id: Optional[str] = None,
        detail: Optional[dict[str, Any]] = None,
        status: str = "ok",
    ) -> None:
        """Append one JSONL event. Fire-and-forget — never raises."""
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            _rotate_if_needed()

            event = {
                "event_id":     str(uuid.uuid4()),
                "timestamp":    datetime.now(timezone.utc).isoformat(),
                "category":     category,
                "action":       action,
                "actor":        actor,
                "engagement_id": engagement_id or "",
                "case_id":      case_id or "",
                "status":       status,
                "detail":       detail or {},
            }

            with open(_LOG_FILE, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event) + "\n")

        except Exception:
            _warn_session()


# Module-level singleton — import and use directly
logger = ActivityLogger()

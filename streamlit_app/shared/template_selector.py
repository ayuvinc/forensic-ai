"""Template selector Streamlit component (RD-02).

render_template_selector(workflow_type) — inline widget used on Settings tab and
workflow pages. Checks firm.json for existing template; if absent offers two options:
"Use my template" (file uploader) or "Use default".

Saves uploaded template to firm_profile/templates/{workflow_type}.docx and updates
firm.json["templates"][workflow_type]. Returns the resolved template path (str | None).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional


_WORKFLOW_LABELS = {
    "investigation_report": "Investigation Report",
    "frm_risk_register":    "FRM Risk Register",
    "due_diligence":        "Due Diligence",
    "transaction_testing":  "Transaction Testing",
    "sanctions_screening":  "Sanctions Screening",
    "client_proposal":      "Client Proposal",
}


def render_template_selector(workflow_type: str) -> Optional[str]:
    """Render template selector for a given workflow_type.

    Returns the resolved template path as a string, or None if using default.
    Uses Streamlit widgets — must be called inside a Streamlit page context.
    """
    import streamlit as st
    from config import FIRM_PROFILE_DIR

    firm_json_path = FIRM_PROFILE_DIR / "firm.json"
    label = _WORKFLOW_LABELS.get(workflow_type, workflow_type.replace("_", " ").title())

    # Load current template setting from firm.json
    current_template = _get_current_template(firm_json_path, workflow_type)

    if current_template:
        tpl_path = FIRM_PROFILE_DIR / "templates" / current_template
        st.caption(f"Current template: `{current_template}`")
        col_change, col_clear = st.columns([2, 1])
        with col_change:
            change = st.button(f"Change {label} template", key=f"tsel_change_{workflow_type}")
        with col_clear:
            if st.button("Use default", key=f"tsel_clear_{workflow_type}"):
                _clear_template(firm_json_path, workflow_type)
                st.rerun()
        if change:
            st.session_state[f"tsel_upload_open_{workflow_type}"] = True

    if not current_template or st.session_state.get(f"tsel_upload_open_{workflow_type}"):
        if not current_template:
            col_upload, col_default = st.columns(2)
            with col_default:
                if st.button("Use default", key=f"tsel_default_{workflow_type}"):
                    return None

        uploaded = st.file_uploader(
            f"Upload {label} template (.docx)",
            type=["docx"],
            key=f"tsel_file_{workflow_type}",
        )
        if uploaded:
            saved_path = _save_template(firm_json_path, workflow_type, uploaded.read())
            if saved_path:
                st.session_state.pop(f"tsel_upload_open_{workflow_type}", None)
                st.success(f"Template saved: `{saved_path.name}`")
                st.rerun()
            else:
                st.error("Failed to save template.")
        return None

    # Return resolved absolute path if template file exists, else None
    if current_template:
        tpl_path = FIRM_PROFILE_DIR / "templates" / current_template
        if tpl_path.exists():
            return str(tpl_path)

    return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_current_template(firm_json_path: Path, workflow_type: str) -> Optional[str]:
    if not firm_json_path.exists():
        return None
    try:
        data = json.loads(firm_json_path.read_text(encoding="utf-8"))
        return data.get("templates", {}).get(workflow_type)
    except Exception:
        return None


def _save_template(firm_json_path: Path, workflow_type: str, file_bytes: bytes) -> Optional[Path]:
    """Save uploaded bytes to firm_profile/templates/{workflow_type}.docx; update firm.json."""
    try:
        from config import FIRM_PROFILE_DIR
        tpl_dir = FIRM_PROFILE_DIR / "templates"
        tpl_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{workflow_type}.docx"
        dest = tpl_dir / filename
        tmp = dest.with_suffix(".tmp")
        tmp.write_bytes(file_bytes)
        os.replace(tmp, dest)

        # Update firm.json["templates"][workflow_type]
        if firm_json_path.exists():
            data = json.loads(firm_json_path.read_text(encoding="utf-8"))
        else:
            data = {}
        data.setdefault("templates", {})[workflow_type] = filename
        tmp_json = firm_json_path.with_suffix(".tmp")
        tmp_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp_json, firm_json_path)

        return dest
    except Exception:
        return None


def _clear_template(firm_json_path: Path, workflow_type: str) -> None:
    """Remove template entry from firm.json for workflow_type."""
    if not firm_json_path.exists():
        return
    try:
        data = json.loads(firm_json_path.read_text(encoding="utf-8"))
        data.get("templates", {}).pop(workflow_type, None)
        tmp = firm_json_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, firm_json_path)
    except Exception:
        pass

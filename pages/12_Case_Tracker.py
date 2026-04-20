"""Case Tracker — Streamlit page (UX-004).

Reads cases/index.json written by write_state() on every state transition (ARCH-INS-02).
O(1) index load — no os.listdir() / glob directory scan at runtime.
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from config import CASES_DIR
from streamlit_app.shared.session import bootstrap
from tools.file_tools import build_case_index

session = bootstrap(st)

_INDEX_PATH = CASES_DIR / "index.json"

_WORKFLOW_LABELS: dict[str, str] = {
    "frm_risk_register":    "FRM Risk Register",
    "investigation_report": "Investigation Report",
    "persona_review":       "Persona Review",
    "policy_sop":           "Policy / SOP",
    "training_material":    "Training Material",
    "client_proposal":      "Client Proposal",
    "proposal_deck":        "Proposal Deck",
    "engagement_scoping":   "Engagement Scoping",
    "due_diligence":        "Due Diligence",
    "sanctions_screening":  "Sanctions Screening",
    "transaction_testing":  "Transaction Testing",
}

# Status sets used for badge colouring (UX-004 4-tier colour system)
_GREEN_TERMINAL = {"OWNER_APPROVED", "DELIVERABLE_WRITTEN"}
_AMBER_REVISION = {"PM_REVISION_REQUESTED", "PARTNER_REVISION_REQ"}

# Shown when PIPELINE_ERROR — guidance text only, no raw stack trace (UX-004)
_PIPELINE_ERROR_GUIDANCE = (
    "The pipeline stopped before completing. To recover: open the workflow page and "
    "re-run — the orchestrator will offer to resume from the last valid state. "
    "For full detail, check `audit_log.jsonl` in the case folder."
)


_STATUS_LABELS: dict[str, str] = {
    "OWNER_APPROVED":         "Approved",
    "DELIVERABLE_WRITTEN":    "Complete",
    "PM_REVISION_REQUESTED":  "Revision (PM)",
    "PARTNER_REVISION_REQ":   "Revision (Partner)",
    "PIPELINE_ERROR":         "Error",
    "INTAKE_CREATED":         "Intake",
    "JUNIOR_DRAFT_COMPLETE":  "Draft",
    "PM_REVIEW_COMPLETE":     "PM Review",
    "PARTNER_REVIEW_COMPLETE":"Partner Review",
    "OWNER_READY":            "Ready",
    "OWNER_REJECTED":         "Rejected",
}


def _status_badge(status: str) -> str:
    """Return coloured prefix + human label for table display."""
    label = _STATUS_LABELS.get(status, status.replace("_", " ").title())
    if status in _GREEN_TERMINAL:
        return f"✓ {label}"
    if status in _AMBER_REVISION:
        return f"~ {label}"
    if status == "PIPELINE_ERROR":
        return f"✗ {label}"
    return label


def _workflow_label(key: str) -> str:
    return _WORKFLOW_LABELS.get(key, key.replace("_", " ").title())


def _load_index() -> tuple[list[dict] | None, str | None, bool]:
    """Load cases/index.json.

    Returns (entries, error_msg, was_backfilled).
    - entries=None  → corrupt JSON; error_msg is set.
    - entries=[]    → no cases at all.
    - was_backfilled → True when index was rebuilt from folder scan (show warning to user).

    When index.json is absent, build_case_index() is called — it handles the dir scan
    internally (tools/file_tools.py) so this page never calls glob() or os.listdir().
    """
    if not _INDEX_PATH.exists():
        # Delegate scan to build_case_index — no direct dir scan in this page
        build_case_index()
        entries, err = _read_index_file()
        # Only show the backfill warning if cases were actually found
        was_backfilled = entries is not None and len(entries) > 0
        return entries, err, was_backfilled

    entries, err = _read_index_file()
    return entries, err, False


def _read_index_file() -> tuple[list[dict] | None, str | None]:
    """Parse cases/index.json. Returns (entries, error_msg)."""
    try:
        return json.loads(_INDEX_PATH.read_text(encoding="utf-8")), None
    except json.JSONDecodeError:
        return None, "Case index is corrupt. Delete cases/index.json and refresh to rebuild."


def _embedding_badge(status: str, chunk_count: int | None = None) -> str:
    """Return coloured label string for a document's embedding_status (EMB-03)."""
    if status == "indexed":
        suffix = f" — {chunk_count} chunk{'s' if chunk_count != 1 else ''}" if chunk_count else ""
        return f"🟢 Indexed{suffix}"
    if status == "pending":
        return "🟡 Pending"
    if status == "failed":
        return "🔴 Failed"
    return "⚪ Unavailable — embedding library not installed"


def _render_document_badges(case_id: str) -> None:
    """Load document_index.json and show embedding badge per document (EMB-03)."""
    idx_path = CASES_DIR / case_id / "document_index.json"
    if not idx_path.exists():
        return
    try:
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        docs = data.get("documents", [])
    except (json.JSONDecodeError, OSError):
        return
    if not docs:
        return

    with st.expander(f"Documents ({len(docs)})", expanded=False):
        for doc in docs:
            emb_status = doc.get("embedding_status", "unavailable")
            filename   = doc.get("filename", doc.get("doc_id", "unknown"))
            badge      = _embedding_badge(emb_status)
            st.markdown(f"**{filename}** — {badge}")


def _render_case_detail(case_id: str, status: str) -> None:
    """Render deliverables, document badges, audit log, and error guidance."""
    cdir = CASES_DIR / case_id

    if not cdir.exists():
        st.caption("Case folder not found on disk.")
        return

    # Deliverable download buttons — check F_Final/ (P9 projects) and root
    report_files = sorted(
        list((cdir / "F_Final").glob("final_report.*.md"))
        + list(cdir.glob("final_report.*.md"))
    )
    if report_files:
        for rf in report_files:
            st.download_button(
                label=f"Download {rf.name}",
                data=rf.read_bytes(),
                file_name=rf.name,
                mime="text/markdown",
                key=f"dl_{case_id}_{rf.name}",
            )
    else:
        st.caption("No deliverables yet for this case.")

    # Embedding status badges per document (EMB-03)
    _render_document_badges(case_id)

    # Audit log presence check — label only, not rendered inline
    audit_log = cdir / "audit_log.jsonl"
    st.caption(
        f"Audit log: **present**  (`cases/{case_id}/audit_log.jsonl`)"
        if audit_log.exists()
        else f"Audit log: not yet written  (`cases/{case_id}/audit_log.jsonl`)"
    )

    # PIPELINE_ERROR guidance — human-readable, no raw traceback (UX-004)
    if status == "PIPELINE_ERROR":
        st.warning(_PIPELINE_ERROR_GUIDANCE)


# ── Page ──────────────────────────────────────────────────────────────────────

st.title("Case Tracker")
st.caption("All cases — loaded from index in one read, no directory scan.")

if st.button("Refresh", key="tracker_refresh"):
    st.rerun()

with st.spinner("Loading cases..."):
    entries, error_msg, was_backfilled = _load_index()

if error_msg:
    st.error(error_msg)
    st.stop()

if was_backfilled:
    st.warning("Case index rebuilt from folder scan.")

if not entries:
    st.info("No cases yet. Run a workflow to create your first case.")
    st.stop()

# Sort newest first by last_updated
entries_sorted = sorted(entries, key=lambda e: e.get("last_updated", ""), reverse=True)

# Build display rows — Case ID truncated at 16 chars for narrow viewports (UX-004 mobile)
rows = []
for e in entries_sorted:
    cid = e.get("case_id", "")
    cid_display = cid[:16] + "…" if len(cid) > 16 else cid
    rows.append({
        "Case ID":      cid_display,
        "_case_id":     cid,           # full ID retained for detail lookup — not shown
        "Client":       e.get("client_name", ""),
        "Workflow":     _workflow_label(e.get("workflow", "")),
        "Status":       _status_badge(e.get("status", "")),
        "Last Updated": e.get("last_updated", "")[:19].replace("T", " "),
        "_engagement_id": e.get("engagement_id", ""),  # scaffold — not shown
    })

df = pd.DataFrame(rows)
display_cols = ["Case ID", "Client", "Workflow", "Status", "Last Updated"]
# on_select="rerun" enables row-click selection (UX-F-05)
event = st.dataframe(
    df[display_cols],
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    key="tracker_df",
)

# ── Row detail — driven by dataframe row click or selectbox fallback ──────────
st.divider()
selected_rows = event.selection.get("rows", []) if hasattr(event, "selection") else []
if selected_rows:
    selected_idx = selected_rows[0]
    selected = rows[selected_idx]["_case_id"] if selected_idx < len(rows) else None
else:
    # Selectbox fallback for environments where dataframe row-click is unavailable
    case_id_list = [r["_case_id"] for r in rows]
    selected = st.selectbox(
        "Select case",
        options=["— select a case to view details —"] + case_id_list,
        key="tracker_selected_case",
        label_visibility="collapsed",
    )
    if selected == "— select a case to view details —":
        selected = None

if selected:
    entry = next((e for e in entries if e.get("case_id") == selected), None)
    status = entry.get("status", "") if entry else ""
    engagement_id = entry.get("engagement_id", "") if entry else ""

    with st.expander(f"Case: {selected}", expanded=True):
        if engagement_id:
            st.caption(f"Engagement ID: {engagement_id}")
        _render_case_detail(selected, status)

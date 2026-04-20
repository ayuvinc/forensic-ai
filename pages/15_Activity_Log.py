"""Activity Log — Streamlit page (ACT-03 / UX-020).

Read-only view of logs/activity.jsonl.
Filters: date range, category multiselect, free-text search.
Paginated 50 events per page. CSV export.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import date, datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_app.shared.session import bootstrap

bootstrap(st)

_LOG_FILE = Path(__file__).parent.parent / "logs" / "activity.jsonl"
_PAGE_SIZE = 50

_CATEGORIES = [
    "SESSION", "SETUP", "ENGAGEMENT", "PIPELINE",
    "DOCUMENT", "DELIVERABLE", "KNOWLEDGE", "TEMPLATE", "SETTINGS", "ERROR",
]

st.title("Activity Log")
st.caption("Read-only audit trail of all system events. Events are append-only.")

# ── Activity log write-failure warning ────────────────────────────────────────
if st.session_state.get("act_log_warn"):
    st.warning(
        "Activity log could not be written during a recent operation. "
        "Check disk space and permissions for the logs/ directory."
    )
    st.session_state["act_log_warn"] = False

# ── Load log file ─────────────────────────────────────────────────────────────

def _load_events() -> tuple[list[dict], str | None]:
    """Parse activity.jsonl line by line.

    Returns (events, error_message). If error_message is set, events may be partial.
    Corrupt lines are skipped and counted.
    """
    if not _LOG_FILE.exists():
        return [], None

    events: list[dict] = []
    corrupt_lines = 0

    try:
        raw = _LOG_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        return [], f"Could not read activity log: {exc}"

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            corrupt_lines += 1

    if corrupt_lines > 0:
        return events, f"{corrupt_lines} corrupt line(s) skipped."
    return events, None


with st.spinner("Loading activity log..."):
    all_events, load_error = _load_events()

if load_error and not all_events:
    st.error(load_error)
    st.stop()

if load_error:
    st.warning(load_error)

if not all_events:
    st.info("No activity recorded yet. Run a workflow to generate events.")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────
st.subheader("Filters")
col1, col2 = st.columns(2)

with col1:
    min_ts = min((e.get("timestamp", "") for e in all_events), default="")[:10]
    max_ts = max((e.get("timestamp", "") for e in all_events), default="")[:10]

    try:
        default_start = date.fromisoformat(min_ts) if min_ts else date.today()
        default_end   = date.fromisoformat(max_ts) if max_ts else date.today()
    except ValueError:
        default_start = default_end = date.today()

    date_start = st.date_input("From", value=default_start, key="act_date_start")
    date_end   = st.date_input("To",   value=default_end,   key="act_date_end")

with col2:
    selected_categories = st.multiselect(
        "Categories",
        options=_CATEGORIES,
        default=[],
        key="act_categories",
    )

search_text = st.text_input(
    "Search (action, engagement ID, detail)",
    placeholder="e.g. pipeline_start, project-alpha",
    key="act_search",
)

# ── Apply filters ─────────────────────────────────────────────────────────────

def _matches(event: dict) -> bool:
    ts_str = event.get("timestamp", "")
    ts_date = ts_str[:10]

    # Date range filter
    try:
        if date_start and ts_date < date_start.isoformat():
            return False
        if date_end and ts_date > date_end.isoformat():
            return False
    except (AttributeError, ValueError):
        pass

    # Category filter
    if selected_categories and event.get("category", "") not in selected_categories:
        return False

    # Free-text search — checks action, engagement_id, detail, case_id
    if search_text:
        needle = search_text.lower()
        haystack = " ".join([
            event.get("action", ""),
            event.get("engagement_id", ""),
            event.get("case_id", ""),
            json.dumps(event.get("detail", {})),
            event.get("actor", ""),
        ]).lower()
        if needle not in haystack:
            return False

    return True


filtered = [e for e in reversed(all_events) if _matches(e)]  # newest first

st.caption(f"Showing **{len(filtered)}** of **{len(all_events)}** events")

# ── Pagination ────────────────────────────────────────────────────────────────
total_pages = max(1, (len(filtered) + _PAGE_SIZE - 1) // _PAGE_SIZE)

if "act_page" not in st.session_state:
    st.session_state["act_page"] = 1

# Reset page to 1 on filter change
filter_key = f"{date_start}|{date_end}|{','.join(selected_categories)}|{search_text}"
if st.session_state.get("_act_filter_key") != filter_key:
    st.session_state["act_page"] = 1
    st.session_state["_act_filter_key"] = filter_key

current_page = st.session_state["act_page"]
current_page = max(1, min(current_page, total_pages))

page_start = (current_page - 1) * _PAGE_SIZE
page_events = filtered[page_start : page_start + _PAGE_SIZE]

# ── Event table ───────────────────────────────────────────────────────────────
if page_events:
    import pandas as pd

    rows = []
    for e in page_events:
        detail_str = json.dumps(e.get("detail", {}))
        if len(detail_str) > 120:
            detail_str = detail_str[:117] + "…"
        rows.append({
            "Timestamp":     e.get("timestamp", "")[:19].replace("T", " "),
            "Category":      e.get("category", ""),
            "Action":        e.get("action", ""),
            "Actor":         e.get("actor", ""),
            "Engagement":    e.get("engagement_id", ""),
            "Status":        e.get("status", ""),
            "Detail":        detail_str,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No events match the current filters.")

# ── Pagination controls ───────────────────────────────────────────────────────
if total_pages > 1:
    st.caption(f"Page {current_page} of {total_pages}")
    pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
    with pcol1:
        if st.button("◀ Previous", disabled=(current_page <= 1), key="act_prev"):
            st.session_state["act_page"] = current_page - 1
            st.rerun()
    with pcol3:
        if st.button("Next ▶", disabled=(current_page >= total_pages), key="act_next"):
            st.session_state["act_page"] = current_page + 1
            st.rerun()

# ── CSV export ────────────────────────────────────────────────────────────────
st.divider()
if filtered:
    def _to_csv(events: list[dict]) -> bytes:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=[
            "timestamp", "category", "action", "actor",
            "engagement_id", "case_id", "status", "detail",
        ], extrasaction="ignore")
        writer.writeheader()
        for e in events:
            e_row = {**e, "detail": json.dumps(e.get("detail", {}))}
            writer.writerow(e_row)
        return buf.getvalue().encode("utf-8")

    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="Export filtered events as CSV",
        data=_to_csv(filtered),
        file_name=f"activity_log_{now_str}.csv",
        mime="text/csv",
    )

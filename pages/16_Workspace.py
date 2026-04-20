"""Engagement Workspace — Input Session UI (P9-05).

Full workspace for an active engagement: A-F folder tree, document upload,
session notes, key facts, red flags, context budget, and Final Run panel.

Entry point: from pages/01_Engagements.py via "Open Workspace" button
(sets st.session_state.active_project = slug before switching).

If active_project is not set, shows a picker to select an engagement.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from config import CASES_DIR, CONTEXT_BUDGET_CHARS
from streamlit_app.shared.session import bootstrap
from tools.project_manager import ProjectManager

session = bootstrap(st)
pm = ProjectManager()


def _save_stakeholder(slug: str, entry: dict) -> None:
    """Append stakeholder entry to D_Working_Papers/stakeholder_inputs.json.

    FR-01: repeated saves append entries rather than overwriting.
    Raises ValueError if 'name' key is missing or empty.
    """
    import json as _json
    import os as _os
    from datetime import datetime, timezone

    if not entry.get("name", "").strip():
        raise ValueError("Stakeholder name is required")

    entry["saved_at"] = datetime.now(timezone.utc).isoformat()
    wp_dir = CASES_DIR / slug / "D_Working_Papers"
    wp_dir.mkdir(parents=True, exist_ok=True)
    path = wp_dir / "stakeholder_inputs.json"
    entries = []
    if path.exists():
        try:
            entries = _json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    entries.append(entry)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(_json.dumps(entries, indent=2, default=str), encoding="utf-8")
    _os.replace(tmp, path)


def _draft_finding_for_lead(st, session, lead_description: str, slug: str) -> None:
    """Use Haiku to draft a brief finding stub for a confirmed lead.

    WF-01b: non-blocking best-effort. Failure is silently logged, not surfaced.
    The draft is appended to D_Working_Papers/session_notes_YYYYMMDD.md.
    """
    try:
        import anthropic
        import config
        from datetime import datetime, timezone

        client = anthropic.Anthropic()
        prompt = (
            f"You are a forensic analyst. A lead has been confirmed: '{lead_description}'. "
            "Draft a one-paragraph factual finding stub following ACFE format: "
            "procedure performed → observation → implication. Keep it under 150 words."
        )
        response = client.messages.create(
            model=config.HAIKU,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        draft = response.content[0].text.strip()
        pm.add_session_note(slug, f"**AI draft finding for confirmed lead:**\n\n{draft}")
        st.info("AI draft finding added to session notes.")
    except Exception:
        pass  # best-effort — lead still registered even if Haiku fails

# ── Workspace ─────────────────────────────────────────────────────────────────

st.title("Engagement Workspace")

# Resolve active project
slug = st.session_state.get("active_project")

if not slug:
    # No active project — show picker
    projects = pm.list_projects()
    if not projects:
        st.info("No engagements found. Create one on the Engagements page.")
        st.stop()
    options = {p["case_id"]: f"{p['case_id']} — {p.get('client_name','')}" for p in projects}
    choice = st.selectbox("Select engagement to open", list(options.keys()), format_func=lambda x: options[x])
    if st.button("Open Workspace", type="primary"):
        st.session_state["active_project"] = choice
        st.rerun()
    st.stop()

state = pm.get_project(slug)
if not state:
    st.error(f"Engagement `{slug}` not found.")
    st.stop()

# ── P9-05a: Project header ─────────────────────────────────────────────────────
lang_labels = {
    "acfe":           "ACFE Internal Review",
    "expert_witness": "Expert Witness",
    "regulatory":     "Regulatory Submission",
    "board_pack":     "Board Pack",
}
lang_std = getattr(state, "language_standard", "acfe")
last_session = (
    state.sessions[-1].started_at.strftime("%Y-%m-%d")
    if state.sessions else "—"
)

col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.subheader(slug)
    st.caption(f"Client: {state.client_name}  |  Service: {state.service_type}  |  Last session: {last_session}")
with col_h2:
    st.markdown(
        f'<span style="background:#F5F2F0;border:1px solid #D5D5D5;border-radius:4px;'
        f'padding:2px 8px;font-size:12px;">{lang_labels.get(lang_std, lang_std)}</span>',
        unsafe_allow_html=True,
    )

st.divider()

# ── P9-05c: Mode selector ──────────────────────────────────────────────────────
mode = st.radio(
    "Session mode",
    ["Input Session", "Final Run"],
    horizontal=True,
    key="workspace_mode",
)

st.divider()

# ── P9-05b: A-F folder tree ────────────────────────────────────────────────────
AF_FOLDER_LABELS = {
    "A_Engagement_Management": "A — Engagement Management",
    "B_Planning":              "B — Planning",
    "C_Evidence":              "C — Evidence",
    "D_Working_Papers":        "D — Working Papers",
    "E_Drafts":                "E — Drafts",
    "F_Final":                 "F — Final",
}

cdir = CASES_DIR / slug

with st.expander("Folder Structure (A–F)", expanded=False):
    for folder_name, label in AF_FOLDER_LABELS.items():
        folder_path = cdir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        files = [f for f in folder_path.iterdir() if f.is_file()] if folder_path.exists() else []

        st.markdown(f"**{label}**")
        if files:
            for f in files[:5]:
                size_kb = f.stat().st_size / 1024
                st.caption(f"&nbsp;&nbsp;`{f.name}` — {size_kb:.1f} KB")
            if len(files) > 5:
                st.caption(f"&nbsp;&nbsp;... and {len(files) - 5} more")
        else:
            st.caption("&nbsp;&nbsp;*(empty)*")

        # Upload button for this folder (only in input mode)
        if mode == "Input Session":
            uploaded = st.file_uploader(
                f"Upload to {label}",
                key=f"upload_{slug}_{folder_name}",
                label_visibility="collapsed",
            )
            if uploaded is not None:
                dest = folder_path / uploaded.name
                dest.write_bytes(uploaded.getbuffer())
                st.success(f"Uploaded `{uploaded.name}` to {label}.")

# ── P9-05d: Input Session panel ───────────────────────────────────────────────
if mode == "Input Session":
    st.subheader("Input Session")

    # Document upload → C_Evidence
    st.markdown("**Upload Evidence Documents**")
    evidence_dir = cdir / "C_Evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    upload_dir = evidence_dir / ts
    doc_upload = st.file_uploader(
        "Upload document(s) to C_Evidence",
        accept_multiple_files=True,
        key=f"evidence_upload_{slug}",
    )
    if doc_upload:
        upload_dir.mkdir(parents=True, exist_ok=True)
        for f in doc_upload:
            (upload_dir / f.name).write_bytes(f.getbuffer())
        st.success(f"Uploaded {len(doc_upload)} file(s) to C_Evidence/{ts}/")

    st.divider()

    # Session notes
    st.markdown("**Session Notes**")
    note_text = st.text_area(
        "Note",
        placeholder="Observations from this session...",
        height=100,
        key=f"session_note_{slug}",
    )
    if st.button("Save Note", key=f"save_note_{slug}"):
        if note_text.strip():
            pm.add_session_note(slug, note_text.strip())
            st.success("Note saved.")
            st.session_state[f"session_note_{slug}"] = ""
            st.rerun()
        else:
            st.warning("Note is empty.")

    st.divider()

    # Key facts
    st.markdown("**Key Facts**")
    col_fact1, col_fact2, col_fact3 = st.columns([3, 2, 1])
    with col_fact1:
        fact_text = st.text_input("Fact", placeholder="Describe the key fact...", key=f"fact_text_{slug}")
    with col_fact2:
        fact_source = st.text_input("Source", placeholder="Document / interview", key=f"fact_src_{slug}")
    with col_fact3:
        fact_date = st.text_input("Date", placeholder="YYYY-MM-DD", key=f"fact_date_{slug}")
    if st.button("Add Key Fact", key=f"add_fact_{slug}"):
        if fact_text.strip():
            pm.add_key_fact(slug, {"fact": fact_text.strip(), "source": fact_source, "date": fact_date})
            st.success("Key fact saved.")
            st.rerun()
        else:
            st.warning("Fact text is required.")

    st.divider()

    # Red flags
    st.markdown("**Red Flags**")
    col_rf1, col_rf2 = st.columns([3, 1])
    with col_rf1:
        rf_desc = st.text_input("Description", placeholder="Describe the red flag...", key=f"rf_desc_{slug}")
    with col_rf2:
        rf_sev = st.selectbox("Severity", ["high", "medium", "low"], key=f"rf_sev_{slug}")
    if st.button("Flag", key=f"add_rf_{slug}"):
        if rf_desc.strip():
            pm.add_red_flag(slug, {"description": rf_desc.strip(), "severity": rf_sev})
            st.success("Red flag saved.")
            st.rerun()
        else:
            st.warning("Description is required.")

    st.divider()

    # WF-01b: Exhibit Register
    with st.expander("Exhibit Register", expanded=False):
        st.caption("Register physical or documentary exhibits for the case file.")
        col_ex1, col_ex2, col_ex3 = st.columns([2, 4, 2])
        with col_ex1:
            ex_id = st.text_input("Exhibit ID", placeholder="E001", key=f"ex_id_{slug}")
        with col_ex2:
            ex_desc = st.text_input("Description", placeholder="Describe the exhibit...", key=f"ex_desc_{slug}")
        with col_ex3:
            ex_date = st.text_input("Date", placeholder="YYYY-MM-DD", key=f"ex_date_{slug}")
        if st.button("Add Exhibit", key=f"add_exhibit_{slug}"):
            if ex_id.strip() and ex_desc.strip():
                pm.add_exhibit(slug, {"exhibit_id": ex_id.strip(), "description": ex_desc.strip(), "date": ex_date.strip()})
                st.success(f"Exhibit {ex_id.strip()} registered.")
                st.rerun()
            else:
                st.warning("Exhibit ID and description are required.")

    st.divider()

    # WF-01b: Leads Register
    with st.expander("Investigative Leads", expanded=False):
        st.caption("Track investigative leads. Confirmed leads trigger a draft finding via AI.")
        col_l1, col_l2, col_l3 = st.columns([2, 4, 2])
        with col_l1:
            lead_id = st.text_input("Lead ID", placeholder="L001", key=f"lead_id_{slug}")
        with col_l2:
            lead_desc = st.text_input("Description", placeholder="Describe the lead...", key=f"lead_desc_{slug}")
        with col_l3:
            lead_status = st.selectbox("Status", ["open", "active", "confirmed", "closed"], key=f"lead_status_{slug}")
        if st.button("Add Lead", key=f"add_lead_{slug}"):
            if lead_id.strip() and lead_desc.strip():
                pm.add_lead(slug, {"lead_id": lead_id.strip(), "description": lead_desc.strip(), "status": lead_status})
                st.success(f"Lead {lead_id.strip()} added.")
                if lead_status == "confirmed":
                    # Haiku draft finding for confirmed leads
                    _draft_finding_for_lead(st, session, lead_desc.strip(), slug)
                st.rerun()
            else:
                st.warning("Lead ID and description are required.")

        # Show open leads
        open_leads = pm.get_open_leads(slug)
        if open_leads:
            st.caption(f"{len(open_leads)} open lead(s):")
            for lead in open_leads:
                st.markdown(f"- **{lead.get('lead_id', '—')}** [{lead.get('status','open')}]: {lead.get('description','')}")

    st.divider()

    # FR-01: Stakeholder Input form
    with st.expander("Stakeholder Inputs (FRM)", expanded=False):
        st.caption("Record stakeholder perspectives for injection into the FRM pipeline.")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            s_name = st.text_input("Name", placeholder="Full name", key=f"s_name_{slug}")
            s_concern = st.text_area("Key concern", height=60, placeholder="Main concern or risk area...", key=f"s_concern_{slug}")
        with col_s2:
            s_role = st.text_input("Role / Title", placeholder="e.g. CFO", key=f"s_role_{slug}")
            s_risk_view = st.text_area("Risk view", height=60, placeholder="How do they view the risk level?", key=f"s_risk_{slug}")

        if st.button("Save Stakeholder", key=f"save_stakeholder_{slug}"):
            if s_name.strip():
                _save_stakeholder(slug, {
                    "name": s_name.strip(), "role": s_role.strip(),
                    "key_concern": s_concern.strip(), "risk_view": s_risk_view.strip(),
                })
                st.success(f"Stakeholder '{s_name.strip()}' saved.")
                st.rerun()
            else:
                st.error("Name is required.")

        # FR-01: Interview notes uploader (separate from evidence upload)
        st.caption("Interview notes (stored in D_Working_Papers/)")
        interview_upload = st.file_uploader(
            "Upload interview notes",
            type=["pdf", "docx", "txt"],
            key=f"interview_notes_{slug}",
        )
        if interview_upload:
            wp_dir = (CASES_DIR / slug / "D_Working_Papers")
            wp_dir.mkdir(parents=True, exist_ok=True)
            dest = wp_dir / f"interview_{interview_upload.name}"
            dest.write_bytes(interview_upload.getbuffer())
            st.success(f"Interview notes uploaded: {interview_upload.name}")

    st.divider()

    # EMB-03: Semantic Search
    with st.expander("Semantic Search", expanded=False):
        st.caption("Search across all ingested documents using semantic similarity.")
        search_query = st.text_input(
            "Search query",
            placeholder="e.g. 'unusual transactions above threshold'",
            key=f"sem_search_query_{slug}",
        )
        if st.button("Search", key=f"sem_search_btn_{slug}"):
            if search_query.strip():
                try:
                    from tools.embedding_engine import EmbeddingEngine
                    engine = EmbeddingEngine(slug)
                    if not engine.available:
                        st.warning(
                            "Semantic search is unavailable — sentence-transformers or "
                            "ChromaDB could not be loaded. Documents are still accessible "
                            "via session notes and the Final Run pipeline."
                        )
                    else:
                        results = engine.search(search_query.strip(), n=5)
                        if not results:
                            st.info("No matching chunks found. Try a different query or upload more documents.")
                        else:
                            st.markdown(f"**{len(results)} result(s) for:** _{search_query.strip()}_")
                            for i, chunk in enumerate(results, 1):
                                with st.container():
                                    st.markdown(f"**Result {i}** — _{chunk.source_citation}_")
                                    st.text(chunk.chunk_text[:600])
                                    st.divider()
                except Exception as exc:
                    st.error(f"Search error: {exc}")
            else:
                st.warning("Enter a search query first.")

    st.divider()

    # P9-05d: Context budget bar
    ctx = pm.get_context_summary(slug)
    budget_pct = ctx.get("context_budget_used_pct", 0.0)
    st.markdown("**Context Budget**")
    st.progress(min(budget_pct / 100.0, 1.0), text=f"{budget_pct:.0f}% of document budget used")
    if budget_pct >= 75:
        st.warning(
            "Context limit approaching — a summary will be written to Working Papers.",
            icon="⚠",
        )

# ── P9-05e: Final Run panel ────────────────────────────────────────────────────
else:
    st.subheader("Final Run")

    # Materials summary
    ctx = pm.get_context_summary(slug)
    doc_count   = ctx.get("document_count", 0)
    budget_pct  = ctx.get("context_budget_used_pct", 0.0)
    interim_written = ctx.get("interim_context_written", False)

    # Count notes, facts, flags
    wp_dir = cdir / "D_Working_Papers"
    note_count = 0
    fact_count = 0
    flag_count = 0
    try:
        note_count = len(list(wp_dir.glob("session_notes_*.md")))
    except Exception:
        pass
    try:
        facts = json.loads((wp_dir / "key_facts.json").read_text()) if (wp_dir / "key_facts.json").exists() else []
        fact_count = len(facts)
    except Exception:
        pass
    try:
        flags = json.loads((wp_dir / "red_flags.json").read_text()) if (wp_dir / "red_flags.json").exists() else []
        flag_count = len(flags)
    except Exception:
        pass

    st.markdown("**Accumulated Materials**")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Documents", doc_count)
    col_m2.metric("Session notes", note_count)
    col_m3.metric("Key facts", fact_count)
    col_m4.metric("Red flags", flag_count)

    if interim_written:
        st.info("Interim context summary written — agents will use the condensed briefing.")

    st.divider()

    # AIC-02: pre-final-run review gate
    from streamlit_app.shared.aic import render_prefinalrun_review

    materials_summary = (
        f"Project: {slug}\n"
        f"Client: {state.client_name}\n"
        f"Service: {state.service_type}\n"
        f"Documents: {doc_count}\n"
        f"Key facts: {fact_count}\n"
        f"Red flags: {flag_count}\n"
        f"Context used: {budget_pct:.0f}%\n"
        f"Interim context written: {interim_written}"
    )

    all_acknowledged = render_prefinalrun_review(st, slug, materials_summary)

    if all_acknowledged:
        service_type = state.service_type
        _WORKFLOW_PAGE = {
            "FRM Risk Register":       "pages/06_FRM.py",
            "Investigation Report":    "pages/02_Investigation.py",
            "Due Diligence":           "pages/09_Due_Diligence.py",
            "Sanctions Screening":     "pages/10_Sanctions.py",
            "Transaction Testing":     "pages/11_Transaction_Testing.py",
            "Policy / SOP":            "pages/04_Policy_SOP.py",
            "Training Material":       "pages/05_Training.py",
            "Proposal":                "pages/07_Proposal.py",
            "Engagement Scoping":      "pages/01_Scope.py",
        }
        st.divider()
        if st.button(f"Run {service_type} Pipeline", type="primary", key=f"run_pipeline_{slug}"):
            st.session_state["active_project"] = slug
            page = _WORKFLOW_PAGE.get(service_type)
            if page and Path(page).exists():
                try:
                    st.switch_page(page)
                except Exception:
                    st.info(f"Navigate to **{service_type}** in the sidebar to start the pipeline.")
            else:
                st.info(f"Navigate to **{service_type}** in the sidebar to start the pipeline.")

# ── Evidence Chat panel (bottom of page) ─────────────────────────────────────
from streamlit_app.shared.evidence_chat_panel import render_evidence_chat_panel
render_evidence_chat_panel(st, slug)

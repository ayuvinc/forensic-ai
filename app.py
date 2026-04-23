"""GoodWork Forensic AI — Streamlit entry point.

Run: streamlit run app.py --server.address=localhost

Navigation is structured via st.navigation() into 5 sections:
  MAIN, PROPOSALS, MONITOR, SETTINGS, WORKFLOWS.
00_Setup is not in the nav (redirect-only via bootstrap).
"""

import os
import streamlit as st

st.set_page_config(
    page_title="GoodWork Forensic AI",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bootstrap session (registry, hook_engine, firm_name)
try:
    from streamlit_app.shared.session import bootstrap
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    st.error(f"First-time setup required: {_bootstrap_err}")
    st.info("Open **00 Setup** in the sidebar to configure your firm profile and API keys.")
    st.stop()

# KB-02: Bootstrap firm knowledge index in background (non-blocking).
# On each render: check if a background index just completed → show toast once.
# On first render after startup: start background thread if reindex needed.
try:
    from tools.firm_knowledge_engine import FirmKnowledgeEngine as _FKE
    import threading as _threading

    _fke = _FKE()
    if _fke.available:
        if st.session_state.get("_kb_indexing") and not _fke.needs_reindex():
            # Background thread finished since last render — notify once
            st.session_state["_kb_indexing"] = False
            st.toast("Knowledge base indexed")
        elif _fke.needs_reindex() and not st.session_state.get("_kb_indexing"):
            st.session_state["_kb_indexing"] = True
            _threading.Thread(target=_fke.index_all, daemon=True).start()
except Exception:
    pass  # never block app startup on KB failure

# ── Sidebar chrome ────────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.markdown(f"### {session.firm_name}")

    mode = session.research_mode
    if mode == "knowledge_only":
        st.warning("RESEARCH MODE: Knowledge Only — no live regulatory/sanctions data")
    else:
        st.success("RESEARCH MODE: Live (Tavily active)")

    st.divider()

# ── Navigation ────────────────────────────────────────────────────────────────
pg = st.navigation(
    {
        "MAIN": [
            st.Page("pages/01_Engagements.py", title="Engagements"),
            st.Page("pages/16_Workspace.py",   title="Workspace"),
        ],
        "PROPOSALS": [
            st.Page("pages/01_Scope.py",   title="Scope"),
            st.Page("pages/07_Proposal.py", title="Proposals"),
        ],
        "MONITOR": [
            st.Page("pages/12_Case_Tracker.py",  title="Case Tracker"),
            st.Page("pages/15_Activity_Log.py",  title="Activity Log"),
        ],
        "SETTINGS": [
            st.Page("pages/13_Team.py",     title="Team"),
            st.Page("pages/14_Settings.py", title="Settings"),
        ],
        "WORKFLOWS": [
            st.Page("pages/02_Investigation.py",      title="Investigation Report"),
            st.Page("pages/06_FRM.py",                title="FRM Risk Register"),
            st.Page("pages/09_Due_Diligence.py",      title="Due Diligence"),
            st.Page("pages/10_Sanctions.py",          title="Sanctions Screening"),
            st.Page("pages/11_Transaction_Testing.py",title="Transaction Testing"),
            st.Page("pages/04_Policy_SOP.py",         title="Policy / SOP"),
            st.Page("pages/05_Training.py",           title="Training Material"),
            st.Page("pages/08_PPT_Pack.py",           title="PPT Pack"),
            st.Page("pages/03_Persona_Review.py",     title="Individual Due Diligence - Background checks"),
        ],
    }
)
pg.run()

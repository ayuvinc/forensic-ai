"""GoodWork Forensic AI — Streamlit entry point.

Run: streamlit run app.py --server.address=localhost

The CLI (python run.py) remains the dev/debug entry point.
This file is the browser-based UI. All business logic, agents, and schemas
live in the existing modules — this file only wires the landing screen.

Page routing is handled by Streamlit's pages/ convention:
each file in pages/ becomes a sidebar entry, ordered by filename prefix.
"""

import streamlit as st

st.set_page_config(
    page_title="GoodWork Forensic AI",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bootstrap session (registry, hook_engine, firm_name)
from streamlit_app.shared.session import bootstrap
session = bootstrap(st)

# ── Sidebar chrome ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### {session.firm_name}")

    # RESEARCH_MODE banner — mirrors CLI banner from ui/display.py
    mode = session.research_mode
    if mode == "knowledge_only":
        st.warning("RESEARCH MODE: Knowledge Only — no live regulatory/sanctions data")
    else:
        st.success("RESEARCH MODE: Live (Tavily active)")

    st.divider()
    st.caption("Navigate using the pages above.")

# ── Landing screen ────────────────────────────────────────────────────────────
st.title("GoodWork Forensic AI")
st.markdown(
    "Select a workflow from the sidebar to begin. "
    "All outputs are saved to the local `cases/` folder with a full audit trail."
)

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Investigation**")
    st.markdown("- New Case Intake\n- Investigation Report\n- Persona Review")

with col2:
    st.markdown("**Compliance**")
    st.markdown("- Policy / SOP\n- Training Material\n- FRM Risk Register")

with col3:
    st.markdown("**Business**")
    st.markdown("- Client Proposal\n- PPT Prompt Pack\n- Case Tracker\n- Browse SOPs")

"""Proposal Deck / PPT Pack — Streamlit page.

UX-003 shell: Zone A (intake + deck config) → Zone B (pipeline) → Zone C (output + download).
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir

session = bootstrap(st)

st.title("PPT Prompt Pack")
st.caption("Generate a DeckStoryboard and per-slide prompt pack for presentation tools")

AUDIENCES = {
    "CFO": "CFO",
    "CEO / Board": "CEO / Board",
    "Legal Counsel": "Legal Counsel",
    "Audit Committee": "Audit Committee",
    "UAE Regulator": "UAE Regulator",
    "Insurance Adjuster": "Insurance Adjuster",
}

if "ppt_stage" not in st.session_state:
    st.session_state.ppt_stage = "intake"

if st.session_state.ppt_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["ppt_stage", "ppt_intake", "ppt_params", "ppt_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.ppt_stage == "intake":
    intake = generic_intake_form(st, "proposal_deck", "PPT Pack — Intake")

    if intake is not None:
        audience = st.selectbox(
            "Primary audience",
            options=list(AUDIENCES.keys()),
            format_func=lambda k: AUDIENCES[k],
        )
        deck_objective = st.text_input(
            "Deck objective (what decision should this drive?)",
            value=f"Engage {intake.client_name} for forensic consulting services",
        )
        decision_required = st.text_input(
            "Decision required from audience",
            value="Approve engagement and sign service agreement",
        )
        slide_count = st.number_input("Approximate slide count", min_value=6, max_value=30, value=12, step=1)

        if st.button("Generate PPT Pack", type="primary"):
            st.session_state.ppt_intake = intake
            st.session_state.ppt_params = {
                "audience": audience,
                "deck_objective": deck_objective.strip(),
                "decision_required": decision_required.strip(),
                "slide_count": slide_count,
            }
            st.session_state.ppt_stage = "ai_questions"
            st.rerun()

# ── STAGE: ai_questions ───────────────────────────────────────────────────────
elif st.session_state.ppt_stage == "ai_questions":
    intake = st.session_state.ppt_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = f"Client: {intake.client_name}. {intake.description}"
    if render_intake_questions(st, intake.case_id, intake_summary):
        st.session_state.ppt_stage = "running"
        st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.ppt_stage == "running":
    intake = st.session_state.ppt_intake
    params = st.session_state.ppt_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Client:** {intake.client_name} | **Audience:** {params['audience']} | **Slides:** {params['slide_count']}")

    from workflows.proposal_deck import run_proposal_deck_workflow

    try:
        result = run_in_status(
            st,
            "Generating PPT prompt pack...",
            run_proposal_deck_workflow,
            intake,
            headless_params=params,
        )
        st.session_state.ppt_result = result
        st.session_state.ppt_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.ppt_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.ppt_stage == "done":
    intake = st.session_state.ppt_intake
    result = st.session_state.ppt_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        slide_count = len(result.slides) if hasattr(result, "slides") else "?"
        st.success(f"PPT Pack complete — {slide_count} slides — Case ID: `{intake.case_id}`")

        if hasattr(result, "key_messages") and result.key_messages:
            with st.expander("Key Messages"):
                for msg in result.key_messages:
                    st.markdown(f"- {msg}")

    cdir = case_dir(intake.case_id)
    master_path = cdir / "deck_master_prompt.v1.md"
    if master_path.exists():
        st.download_button(
            label="Download master prompt (.md)",
            data=master_path.read_text(encoding="utf-8"),
            file_name=f"DeckMaster_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )

    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")
    st.caption("Per-slide prompt files (slide_01_prompt.md …) are in the case folder.")

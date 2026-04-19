"""Engagement Scoping — Streamlit page.

UX-003 shell: Zone A (intake + situation description) → Zone B (pipeline) → Zone C (scope doc + download).
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir

session = bootstrap(st)

st.title("Engagement Scoping")
st.caption("5-step scoping conversation — identify the right engagement type from the client's situation")

st.info("Start here for any new engagement. Scoping takes 2–3 minutes and determines which pipeline is right for your case.", icon="ℹ️")

if "scope_stage" not in st.session_state:
    st.session_state.scope_stage = "intake"

if st.session_state.scope_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["scope_stage", "scope_intake", "scope_params", "scope_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.scope_stage == "intake":
    intake = generic_intake_form(st, "engagement_scoping", "Engagement Scoping — Intake")

    if intake is not None:
        st.markdown("**Client Situation**")
        situation = st.text_area(
            "What is the client facing? Describe the problem.",
            value=intake.description,
            height=100,
        )
        trigger = st.text_input(
            "What triggered this engagement?",
            placeholder="e.g. complaint, audit finding, suspicion, regulatory inquiry",
        )
        desired_outcome = st.text_input(
            "What does the client want to walk away with?",
            placeholder="e.g. investigation report, clean bill of health, compliance program",
        )
        constraints = st.text_input(
            "Any constraints? (timeline, budget, data access)",
            value="",
        )
        red_flags = st.text_input(
            "Any specific red flags or suspicions already identified?",
            value="",
        )

        if st.button("Run Scoping", type="primary"):
            if not trigger.strip():
                st.error("Required: Engagement trigger")
            elif not desired_outcome.strip():
                st.error("Required: Desired outcome")
            else:
                st.session_state.scope_intake = intake
                st.session_state.scope_params = {
                    "situation": situation.strip(),
                    "trigger": trigger.strip(),
                    "desired_outcome": desired_outcome.strip(),
                    "constraints": constraints.strip(),
                    "red_flags": red_flags.strip(),
                }
                st.session_state.scope_stage = "running"
                st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.scope_stage == "running":
    intake = st.session_state.scope_intake
    params = st.session_state.scope_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Client:** {intake.client_name} | **Trigger:** {params['trigger']}")

    from workflows.engagement_scoping import run_engagement_scoping_workflow

    try:
        result = run_in_status(
            st,
            "Running engagement scoping...",
            run_engagement_scoping_workflow,
            intake,
            headless_params=params,
        )
        st.session_state.scope_result = result
        st.session_state.scope_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.scope_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.scope_stage == "done":
    intake = st.session_state.scope_intake
    result = st.session_state.scope_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Scope document complete — Case ID: `{intake.case_id}`")
        if hasattr(result, "primary_engagement"):
            st.markdown(f"**Recommended engagement:** {result.primary_engagement.replace('_', ' ').title()}")
        if hasattr(result, "scope_components") and result.scope_components:
            st.markdown("**Scope components:** " + " | ".join(result.scope_components[:4]))

    cdir = case_dir(intake.case_id)
    scope_path = cdir / "confirmed_scope.json"
    if scope_path.exists():
        st.download_button(
            label="Download scope document (.json)",
            data=scope_path.read_text(encoding="utf-8"),
            file_name=f"Scope_{intake.client_name}_{intake.case_id}.json",
            mime="application/json",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

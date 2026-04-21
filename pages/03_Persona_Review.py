"""Persona Review — Streamlit page.

UX-003 shell: Zone A (intake + persona selection) → Zone B (pipeline) → Zone C (output).
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status

try:
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    st.error(f"Page failed to load: {_bootstrap_err}")
    st.stop()

st.title("Individual Due Diligence - Background checks")
st.caption("Review a deliverable from CFO, Legal Counsel, UAE Regulator, and Insurance Adjuster perspectives")

PERSONA_OPTIONS = {
    "cfo": "CFO",
    "lawyer": "Legal Counsel",
    "regulator": "UAE Regulator",
    "insurance_adjuster": "Insurance Adjuster",
}

if "pr_stage" not in st.session_state:
    st.session_state.pr_stage = "intake"

if st.session_state.pr_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["pr_stage", "pr_intake", "pr_params", "pr_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.pr_stage == "intake":
    intake = generic_intake_form(st, "persona_review", "Individual Due Diligence - Background checks — Intake")

    if intake is not None:
        st.markdown("**Select personas to review**")
        selected = st.multiselect(
            "Personas",
            options=list(PERSONA_OPTIONS.keys()),
            default=list(PERSONA_OPTIONS.keys()),
            format_func=lambda k: PERSONA_OPTIONS[k],
        )

        deliverable_text = st.text_area(
            "Paste report content to review (leave blank to load from case folder)",
            height=200,
        )

        if st.button("Run Individual Due Diligence", type="primary"):
            if not selected:
                st.error("Select at least one persona.")
            else:
                st.session_state.pr_intake = intake
                st.session_state.pr_params = {
                    "persona_ids": selected,
                    "deliverable_text": deliverable_text.strip(),
                }
                st.session_state.pr_stage = "running"
                st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.pr_stage == "running":
    intake = st.session_state.pr_intake
    params = st.session_state.pr_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Client:** {intake.client_name} | **Personas:** {', '.join(params['persona_ids'])}")

    from workflows.persona_review import run_persona_review_workflow

    try:
        result = run_in_status(
            st,
            "Running Individual Due Diligence...",
            run_persona_review_workflow,
            intake,
            session.registry,
            session.hook_engine,
            headless_params=params,
        )
        st.session_state.pr_result = result
        st.session_state.pr_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.pr_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.pr_stage == "done":
    intake = st.session_state.pr_intake
    result = st.session_state.pr_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Individual Due Diligence complete — {len(result)} review(s) — Case ID: `{intake.case_id}`")
        for review in result:
            with st.expander(f"{review.persona} — {review.overall_verdict.upper()}"):
                st.markdown(f"**Perspective:** {review.perspective}")
                if review.objections:
                    st.markdown("**Objections:** " + "; ".join(review.objections[:3]))
                if review.regulatory_gaps:
                    st.markdown("**Regulatory gaps:** " + "; ".join(review.regulatory_gaps[:2]))
                st.markdown(f"**Recommendation:** {review.recommendation}")

    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

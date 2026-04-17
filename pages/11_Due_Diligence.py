"""Due Diligence — Streamlit page.

UX-003 shell: Zone A (intake + subject fields) → Zone B (pipeline) → Zone C (output + download).
Individual and Entity branches via selectbox.
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir

session = bootstrap(st)

st.title("Due Diligence")
st.caption("Individual and Entity DD — Standard Phase 1 and Enhanced Phase 2 branches")

if "dd_stage" not in st.session_state:
    st.session_state.dd_stage = "intake"

if st.session_state.dd_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["dd_stage", "dd_intake", "dd_params", "dd_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.dd_stage == "intake":
    intake = generic_intake_form(st, "due_diligence", "Due Diligence — Intake")

    if intake is not None:
        subject_type = st.selectbox("Subject type", ["individual", "entity"], format_func=str.title)
        subject_name = st.text_input(
            "Full legal name of subject",
            placeholder="Individual: full name as on passport  |  Entity: registered legal name",
        )
        jurisdictions_raw = st.text_input(
            "Operating jurisdictions (comma-separated)",
            value=intake.primary_jurisdiction,
        )
        dd_purpose_options = ["onboarding", "investment", "partnership", "employment", "acquisition", "other"] if subject_type == "individual" else ["acquisition", "investment", "vendor_onboarding", "joint_venture", "partnership", "other"]
        dd_purpose = st.selectbox("Purpose of DD", dd_purpose_options, format_func=lambda v: v.replace("_", " ").title())
        screening_level = st.selectbox(
            "Screening level",
            ["standard_phase1", "enhanced_phase2"],
            format_func=lambda v: "Standard Phase 1" if v == "standard_phase1" else "Enhanced Phase 2",
        )
        specific_concerns = st.text_area("Specific concerns or red flags (optional)", height=80)

        if st.button("Run Due Diligence", type="primary"):
            if not subject_name.strip():
                st.error("Required: Subject name")
            else:
                jurisdictions = [j.strip() for j in jurisdictions_raw.split(",") if j.strip()]
                st.session_state.dd_intake = intake
                st.session_state.dd_params = {
                    "subject_type": subject_type,
                    "subject_name": subject_name.strip(),
                    "jurisdictions": jurisdictions,
                    "dd_purpose": dd_purpose,
                    "screening_level": screening_level,
                    "specific_concerns": specific_concerns.strip(),
                    "screening_lists": ["all"],
                    "deliverable_format": "full_report",
                }
                st.session_state.dd_stage = "running"
                st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.dd_stage == "running":
    intake = st.session_state.dd_intake
    params = st.session_state.dd_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Subject:** {params['subject_name']} ({params['subject_type']}) | **Level:** {params['screening_level'].replace('_', ' ').title()}")

    from workflows.due_diligence import run_due_diligence_workflow

    try:
        result = run_in_status(
            st,
            "Running Due Diligence pipeline...",
            run_due_diligence_workflow,
            intake,
            session.registry,
            session.hook_engine,
            headless_params=params,
        )
        st.session_state.dd_result = result
        st.session_state.dd_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.dd_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.dd_stage == "done":
    intake = st.session_state.dd_intake
    result = st.session_state.dd_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Due Diligence report complete — Case ID: `{intake.case_id}`")

    report_path = case_dir(intake.case_id) / "final_report.en.md"
    if report_path.exists():
        st.download_button(
            label="Download DD report (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"DD_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

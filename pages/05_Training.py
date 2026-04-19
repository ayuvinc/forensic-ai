"""Training Material Generator — Streamlit page.

UX-003 shell: Zone A (intake + topic/audience) → Zone B (pipeline) → Zone C (output + download).
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir

session = bootstrap(st)

st.title("Training Material")
st.caption("Generate role-specific AML, fraud awareness, and compliance training modules")

TRAINING_TOPICS = {
    "aml_awareness": "AML Awareness",
    "fraud_awareness": "Fraud Awareness",
    "bribery_corruption_awareness": "Bribery & Corruption Awareness",
    "data_privacy": "Data Privacy",
    "whistleblowing_procedures": "Whistleblowing Procedures",
    "kyc_procedures": "KYC Procedures",
}

TARGET_AUDIENCES = {
    "all_staff": "All Staff",
    "finance_team": "Finance Team",
    "senior_management": "Senior Management",
    "board_directors": "Board / Directors",
    "compliance_team": "Compliance Team",
    "front_line_staff": "Front Line Staff",
}

if "tr_stage" not in st.session_state:
    st.session_state.tr_stage = "intake"

if st.session_state.tr_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["tr_stage", "tr_intake", "tr_params", "tr_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.tr_stage == "intake":
    intake = generic_intake_form(st, "training_material", "Training Material — Intake")

    if intake is not None:
        topic = st.selectbox(
            "Training topic",
            options=list(TRAINING_TOPICS.keys()),
            format_func=lambda k: TRAINING_TOPICS[k],
        )
        target_audience = st.selectbox(
            "Target audience",
            options=list(TARGET_AUDIENCES.keys()),
            format_func=lambda k: TARGET_AUDIENCES[k],
        )
        duration = st.number_input("Duration (minutes)", min_value=15, max_value=480, value=60, step=15)
        include_quiz = st.checkbox("Include knowledge check quiz", value=True)
        include_case_study = st.checkbox("Include case study", value=True)

        if st.button("Generate Training Material", type="primary"):
            st.session_state.tr_intake = intake
            st.session_state.tr_params = {
                "topic": topic,
                "target_audience": target_audience,
                "duration": duration,
                "include_quiz": include_quiz,
                "include_case_study": include_case_study,
            }
            st.session_state.tr_stage = "running"
            st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.tr_stage == "running":
    intake = st.session_state.tr_intake
    params = st.session_state.tr_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Client:** {intake.client_name} | **Topic:** {TRAINING_TOPICS.get(params['topic'], params['topic'])} | **Audience:** {TARGET_AUDIENCES.get(params['target_audience'], params['target_audience'])}")

    from workflows.training_material import run_training_material_workflow

    try:
        result = run_in_status(
            st,
            "Generating training material...",
            run_training_material_workflow,
            intake,
            headless_params=params,
        )
        st.session_state.tr_result = result
        st.session_state.tr_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.tr_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.tr_stage == "done":
    intake = st.session_state.tr_intake
    result = st.session_state.tr_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Training material complete — Case ID: `{intake.case_id}`")

    report_path = case_dir(intake.case_id) / "final_report.en.md"
    if report_path.exists():
        st.download_button(
            label="Download training material (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"Training_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

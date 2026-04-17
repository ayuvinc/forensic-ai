"""Investigation Report — Streamlit page.

UX-003 shell: Zone A (intake + type/audience) → Zone B (pipeline) → Zone C (output + download).
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status, PipelineEvent

session = bootstrap(st)

st.title("Investigation Report")
st.caption("Full three-agent pipeline — Asset Misappropriation, Corruption, Cyber Fraud, and more")

INVESTIGATION_TYPES = {
    "asset_misappropriation": "Asset Misappropriation",
    "financial_statement_fraud": "Financial Statement Fraud",
    "corruption_bribery": "Corruption & Bribery",
    "cyber_fraud": "Cyber Fraud / Digital Investigation",
    "procurement_fraud": "Procurement Fraud",
    "revenue_leakage": "Revenue Leakage",
    "compliance_investigation": "Compliance Investigation",
}

AUDIENCES = {
    "management": "Management",
    "board": "Board",
    "legal_proceedings": "Legal Proceedings (Expert Witness)",
    "regulatory_submission": "Regulatory Submission",
}

if "inv_stage" not in st.session_state:
    st.session_state.inv_stage = "intake"

if st.session_state.inv_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["inv_stage", "inv_intake", "inv_params", "inv_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.inv_stage == "intake":
    intake = generic_intake_form(st, "investigation_report", "Investigation Report — Intake")

    if intake is not None:
        inv_type = st.selectbox(
            "Investigation type",
            options=list(INVESTIGATION_TYPES.keys()),
            format_func=lambda k: INVESTIGATION_TYPES[k],
            key="inv_type_select",
        )
        audience = st.selectbox(
            "Report audience",
            options=list(AUDIENCES.keys()),
            format_func=lambda k: AUDIENCES[k],
            key="inv_audience_select",
        )

        if st.button("Run Investigation", type="primary"):
            st.session_state.inv_intake = intake
            st.session_state.inv_params = {"investigation_type": inv_type, "audience": audience}
            st.session_state.inv_stage = "running"
            st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.inv_stage == "running":
    intake = st.session_state.inv_intake
    params = st.session_state.inv_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Client:** {intake.client_name} | **Type:** {INVESTIGATION_TYPES.get(params['investigation_type'], params['investigation_type'])} | **Audience:** {AUDIENCES.get(params['audience'], params['audience'])}")

    from workflows.investigation_report import run_investigation_workflow

    try:
        result = run_in_status(
            st,
            "Running Investigation pipeline...",
            run_investigation_workflow,
            intake,
            session.registry,
            session.hook_engine,
            headless_params=params,
        )
        st.session_state.inv_result = result
        st.session_state.inv_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.inv_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.inv_stage == "done":
    intake = st.session_state.inv_intake
    result = st.session_state.inv_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Investigation Report complete — Case ID: `{intake.case_id}`")

    from tools.file_tools import case_dir
    report_path = case_dir(intake.case_id) / "final_report.en.md"
    if report_path.exists():
        st.download_button(
            label="Download final_report.en.md",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"Investigation_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

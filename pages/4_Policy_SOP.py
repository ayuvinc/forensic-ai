"""Policy / SOP Generator — Streamlit page.

UX-003 shell: Zone A (intake + doc type) → Zone B (pipeline) → Zone C (output + download).
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir

session = bootstrap(st)

st.title("Policy / SOP Generator")
st.caption("Draft AML/CFT policies, fraud prevention policies, SOPs with regulatory citations")

POLICY_TYPES = {
    "aml_cft_policy": "AML / CFT Policy",
    "fraud_prevention_policy": "Fraud Prevention Policy",
    "whistleblower_policy": "Whistleblower Policy",
    "procurement_policy": "Procurement Policy",
    "conflict_of_interest_policy": "Conflict of Interest Policy",
    "data_privacy_policy": "Data Privacy Policy",
}

SOP_TYPES = {
    "transaction_monitoring_sop": "Transaction Monitoring SOP",
    "kyc_due_diligence_sop": "KYC / Due Diligence SOP",
    "fraud_investigation_sop": "Fraud Investigation SOP",
    "sanctions_screening_sop": "Sanctions Screening SOP",
    "suspicious_activity_reporting_sop": "Suspicious Activity Reporting SOP",
}

if "ps_stage" not in st.session_state:
    st.session_state.ps_stage = "intake"

if st.session_state.ps_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["ps_stage", "ps_intake", "ps_params", "ps_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.ps_stage == "intake":
    intake = generic_intake_form(st, "policy_sop", "Policy / SOP — Intake")

    if intake is not None:
        doc_type = st.selectbox("Document type", ["policy", "sop"], format_func=str.title)

        if doc_type == "policy":
            subtypes = POLICY_TYPES
        else:
            subtypes = SOP_TYPES

        doc_subtype = st.selectbox(
            "Document subtype",
            options=list(subtypes.keys()),
            format_func=lambda k: subtypes[k],
        )

        gap_analysis = st.selectbox(
            "Mode",
            ["new", "gap"],
            format_func=lambda v: "New document" if v == "new" else "Gap analysis of existing",
        )

        if st.button("Generate Document", type="primary"):
            st.session_state.ps_intake = intake
            st.session_state.ps_params = {
                "doc_type": doc_type,
                "doc_subtype": doc_subtype,
                "gap_analysis": gap_analysis,
            }
            st.session_state.ps_stage = "running"
            st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.ps_stage == "running":
    intake = st.session_state.ps_intake
    params = st.session_state.ps_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Client:** {intake.client_name} | **Type:** {params['doc_subtype'].replace('_', ' ').title()}")

    from workflows.policy_sop import run_policy_sop_workflow

    try:
        result = run_in_status(
            st,
            "Generating Policy / SOP...",
            run_policy_sop_workflow,
            intake,
            session.registry,
            session.hook_engine,
            headless_params=params,
        )
        st.session_state.ps_result = result
        st.session_state.ps_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.ps_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.ps_stage == "done":
    intake = st.session_state.ps_intake
    result = st.session_state.ps_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Document complete — Case ID: `{intake.case_id}`")

    report_path = case_dir(intake.case_id) / "final_report.en.md"
    if report_path.exists():
        st.download_button(
            label="Download document (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"PolicySOP_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

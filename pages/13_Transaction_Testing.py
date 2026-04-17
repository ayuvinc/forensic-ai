"""Transaction Testing — Streamlit page.

UX-003 shell: Zone A (intake + 2-stage context) → Zone B (pipeline with auto-confirmed plan) → Zone C (output + download).
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir

session = bootstrap(st)

st.title("Transaction Testing")
st.caption("Fraud quantification, procurement fraud testing, AML transaction analysis, and audit compliance")

ENGAGEMENT_CONTEXTS = {
    "fraud_discovery": "Fraud Discovery (does fraud exist?)",
    "fraud_quantification": "Fraud Quantification (measure the loss)",
    "audit_compliance": "Audit / Controls Compliance",
    "due_diligence": "Due Diligence (pre-acquisition financial integrity)",
    "regulatory": "Regulatory (regulator-mandated testing)",
}

FRAUD_TYPOLOGIES = {
    "procurement_fraud": "Procurement Fraud",
    "payroll_fraud": "Payroll Fraud",
    "expense_fraud": "Expense Fraud",
    "cash_fraud": "Cash Fraud",
    "financial_stmt_fraud": "Financial Statement Fraud",
    "aml": "AML / Suspicious Transactions",
}

EVIDENCE_STANDARDS = {
    "internal_review": "Internal Review",
    "regulatory_submission": "Regulatory Submission",
    "court_ready": "Court Ready",
    "board_pack": "Board Pack",
}

if "tt_stage" not in st.session_state:
    st.session_state.tt_stage = "intake"

if st.session_state.tt_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["tt_stage", "tt_intake", "tt_params", "tt_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.tt_stage == "intake":
    intake = generic_intake_form(st, "transaction_testing", "Transaction Testing — Intake")

    if intake is not None:
        engagement_context = st.selectbox(
            "Engagement context",
            options=list(ENGAGEMENT_CONTEXTS.keys()),
            format_func=lambda k: ENGAGEMENT_CONTEXTS[k],
        )

        fraud_typology = None
        if engagement_context in ("fraud_discovery", "fraud_quantification"):
            fraud_typology = st.selectbox(
                "Fraud typology",
                options=list(FRAUD_TYPOLOGIES.keys()),
                format_func=lambda k: FRAUD_TYPOLOGIES[k],
            )

        date_range = st.text_input(
            "Transaction date range",
            placeholder="e.g. Jan 2023 – Dec 2024",
        )
        data_inventory = st.text_input(
            "Data available / expected",
            placeholder="e.g. GL export Jan-Dec 2024, AP ledger",
            value="TBD",
        )
        evidence_standard = st.selectbox(
            "Evidence standard",
            options=list(EVIDENCE_STANDARDS.keys()),
            format_func=lambda k: EVIDENCE_STANDARDS[k],
        )

        if st.button("Run Transaction Testing", type="primary"):
            if not date_range.strip():
                st.error("Required: Transaction date range")
            else:
                st.session_state.tt_intake = intake
                st.session_state.tt_params = {
                    "engagement_context": engagement_context,
                    "fraud_typology": fraud_typology,
                    "date_range": date_range.strip(),
                    "data_inventory": data_inventory.strip(),
                    "evidence_standard": evidence_standard,
                    "sampling": "full_population",
                }
                st.session_state.tt_stage = "running"
                st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.tt_stage == "running":
    intake = st.session_state.tt_intake
    params = st.session_state.tt_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Client:** {intake.client_name} | **Context:** {ENGAGEMENT_CONTEXTS.get(params['engagement_context'], params['engagement_context'])} | **Date range:** {params['date_range']}")

    from workflows.transaction_testing import run_transaction_testing_workflow

    try:
        result = run_in_status(
            st,
            "Running Transaction Testing pipeline...",
            run_transaction_testing_workflow,
            intake,
            session.registry,
            session.hook_engine,
            headless_params=params,
        )
        st.session_state.tt_result = result
        st.session_state.tt_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.tt_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.tt_stage == "done":
    intake = st.session_state.tt_intake
    result = st.session_state.tt_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Transaction Testing report complete — Case ID: `{intake.case_id}`")

    report_path = case_dir(intake.case_id) / "final_report.en.md"
    if report_path.exists():
        st.download_button(
            label="Download testing report (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"TT_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

"""Policy / SOP Generator — Streamlit page.

UX-003 shell: Zone A (intake + doc type) → Zone B (pipeline) → Zone C (output + download).
Fixed types only (11 subtypes); co-build mode deferred to Sprint-IA-04 (BA-IA-09).
"""

import streamlit as st
from datetime import datetime, timezone
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import render_engagement_banner, get_project_language_standard
from streamlit_app.shared.hybrid_intake import (
    HybridIntakeEngine,
    _POLICY_SOP_FIELD_CONFIG,
    POLICY_SUBTYPE_LABELS,
)
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir, get_final_report_path

# Label → pipeline key maps
_POLICY_SUBTYPE_KEYS = {
    "AML / CFT Policy":                    "aml_cft_policy",
    "Fraud Prevention Policy":             "fraud_prevention_policy",
    "Whistleblower Policy":                "whistleblower_policy",
    "Procurement Policy":                  "procurement_policy",
    "Conflict of Interest Policy":         "conflict_of_interest_policy",
    "Data Privacy Policy":                 "data_privacy_policy",
    "Transaction Monitoring SOP":          "transaction_monitoring_sop",
    "KYC / Due Diligence SOP":             "kyc_due_diligence_sop",
    "Fraud Investigation SOP":             "fraud_investigation_sop",
    "Sanctions Screening SOP":             "sanctions_screening_sop",
    "Suspicious Activity Reporting SOP":   "suspicious_activity_reporting_sop",
}

try:
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    st.error(f"Page failed to load: {_bootstrap_err}")
    st.stop()

st.title("Policy / SOP Generator")
st.caption("Draft AML/CFT policies, fraud prevention policies, SOPs with regulatory citations")

_ps_engine = HybridIntakeEngine(st, _POLICY_SOP_FIELD_CONFIG, "policy_sop")

if "ps_stage" not in st.session_state:
    st.session_state.ps_stage = "intake"

if st.session_state.ps_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["ps_stage", "ps_intake", "ps_params", "ps_result"]:
            st.session_state.pop(k, None)
        _ps_engine.reset()
        st.rerun()

# ── STAGE: intake (BA-IA-07: HybridIntakeEngine) ─────────────────────────────
if st.session_state.ps_stage == "intake":
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    client_name = project_meta.get("client_name", "") if project_meta else ""
    if not client_name:
        client_name = st.text_input("Client name *", key="ps_client_name_manual")

    st.divider()
    engine_result = _ps_engine.run()

    if engine_result is not None and client_name.strip():
        import uuid as _uuid
        from schemas.case import CaseIntake

        values = engine_result["values"]
        case_id = engagement_id if engagement_id else (
            f"{datetime.now().strftime('%Y%m%d')}-{_uuid.uuid4().hex[:6].upper()}"
        )

        doc_subtype_label = values.get("doc_subtype", "AML / CFT Policy")
        doc_type = "policy" if doc_subtype_label in POLICY_SUBTYPE_LABELS else "sop"
        doc_subtype = _POLICY_SUBTYPE_KEYS.get(doc_subtype_label, "aml_cft_policy")

        gap_analysis_label = values.get("gap_analysis", "New document")
        gap_analysis = "new" if gap_analysis_label == "New document" else "gap"

        intake = CaseIntake(
            case_id=case_id,
            client_name=client_name.strip(),
            industry=values.get("industry", "").strip(),
            primary_jurisdiction=values.get("jurisdiction", "UAE"),
            description=values.get("description", "").strip(),
            workflow="policy_sop",
            language=get_project_language_standard(st),
            created_at=datetime.now(timezone.utc),
            engagement_id=engagement_id or None,
        )
        st.session_state.ps_intake = intake
        st.session_state.ps_params = {
            "doc_type":    doc_type,
            "doc_subtype": doc_subtype,
            "gap_analysis": gap_analysis,
        }
        st.session_state.ps_stage = "ai_questions"
        st.rerun()

# ── STAGE: ai_questions ───────────────────────────────────────────────────────
elif st.session_state.ps_stage == "ai_questions":
    intake = st.session_state.ps_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = f"Client: {intake.client_name}. {intake.description}"
    if render_intake_questions(st, intake.case_id, intake_summary):
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

    report_path = get_final_report_path(intake.case_id)
    if report_path.exists():
        st.download_button(
            label="Download document (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"PolicySOP_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

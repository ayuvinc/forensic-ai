"""Transaction Testing — Streamlit page.

UX-003 shell: Zone A (intake + 2-stage context + doc upload) → Zone B (pipeline) → Zone C (output + download).
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import render_engagement_banner, get_project_language_standard
from streamlit_app.shared.hybrid_intake import HybridIntakeEngine, _TT_FIELD_CONFIG
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir, get_final_report_path

# Label → pipeline key maps
_TT_CONTEXT_KEYS = {
    "Fraud Discovery (does fraud exist?)":            "fraud_discovery",
    "Fraud Quantification (measure the loss)":        "fraud_quantification",
    "Audit / Controls Compliance":                    "audit_compliance",
    "Due Diligence (pre-acquisition financial integrity)": "due_diligence",
    "Regulatory (regulator-mandated testing)":        "regulatory",
}
_TT_TYPOLOGY_KEYS = {
    "Not applicable":          None,
    "Procurement Fraud":       "procurement_fraud",
    "Payroll Fraud":           "payroll_fraud",
    "Expense Fraud":           "expense_fraud",
    "Cash Fraud":              "cash_fraud",
    "Financial Statement Fraud": "financial_stmt_fraud",
    "AML / Suspicious Transactions": "aml",
}
_TT_EVIDENCE_KEYS = {
    "Internal Review":       "internal_review",
    "Regulatory Submission": "regulatory_submission",
    "Court Ready":           "court_ready",
    "Board Pack":            "board_pack",
}

# Kept for running-stage display
ENGAGEMENT_CONTEXTS = {
    "fraud_discovery":     "Fraud Discovery (does fraud exist?)",
    "fraud_quantification": "Fraud Quantification (measure the loss)",
    "audit_compliance":    "Audit / Controls Compliance",
    "due_diligence":       "Due Diligence (pre-acquisition financial integrity)",
    "regulatory":          "Regulatory (regulator-mandated testing)",
}


def _infer_doc_type(filename: str) -> str:
    """Map filename to a valid DocumentEntry doc_type literal (RG-3)."""
    name = Path(filename).stem.lower()
    ext  = Path(filename).suffix.lower().lstrip(".")
    if ext in ("xlsx", "xls", "csv"):
        return "excel_data"
    if ext in ("msg", "eml"):
        return "email"
    keywords = {
        "financial_records":    ("bank", "statement", "transaction", "ledger", "account", "balance"),
        "interview_transcript": ("transcript", "interview", "witness"),
        "engagement_letter":    ("engagement", "retainer", "mandate"),
        "correspondence":       ("letter", "board", "memo", "notice", "annexure", "annex"),
        "corporate_filing":     ("incorporation", "registry", "filing", "moa", "aoa", "certificate"),
        "policy_sop":           ("policy", "procedure", "sop", "guideline"),
        "previous_report":      ("report", "audit", "finding"),
        "email":                ("email",),
    }
    for doc_type, kws in keywords.items():
        if any(kw in name for kw in kws):
            return doc_type
    return "other"


try:
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    from streamlit_app.shared.crash_reporter import write_crash_report
    _crash_path = write_crash_report(__file__, _bootstrap_err)
    st.error("Something went wrong loading this page.")
    st.code(_crash_path, language=None)
    st.caption("Share this file with Claude to diagnose the issue.")
    with st.expander("Show error details"):
        st.text(type(_bootstrap_err).__name__ + ": " + str(_bootstrap_err))
    st.stop()

st.title("Transaction Testing")
st.caption("Fraud quantification, procurement fraud testing, AML transaction analysis, and audit compliance")

_tt_engine = HybridIntakeEngine(st, _TT_FIELD_CONFIG, "transaction_testing")

if "tt_stage" not in st.session_state:
    st.session_state.tt_stage = "intake"

if st.session_state.tt_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["tt_stage", "tt_intake", "tt_params", "tt_result", "tt_reg_results"]:
            st.session_state.pop(k, None)
        _tt_engine.reset()
        st.rerun()

# ── STAGE: intake (BA-IA-07: HybridIntakeEngine) ─────────────────────────────
if st.session_state.tt_stage == "intake":
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    client_name = project_meta.get("client_name", "") if project_meta else ""
    if not client_name:
        client_name = st.text_input("Client name *", key="tt_client_name_manual")

    st.divider()
    engine_result = _tt_engine.run()

    if engine_result is not None and client_name.strip():
        import uuid as _uuid
        from schemas.case import CaseIntake

        values = engine_result["values"]

        # ── Document upload — Zone A (outside engine; file uploader not supported in engine) ──
        uploaded_files = st.file_uploader(
            "Upload case documents (optional)",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "xlsx"],
            key="tt_docs",
        )
        st.warning("Maximum file size is 10MB per document.")
        if uploaded_files and len(uploaded_files) > 10:
            st.warning("Maximum 10 documents per case.")

        if st.button("Run Transaction Testing", type="primary"):
            from tools.document_manager import DocumentManager
            from schemas.documents import DocumentProvenance

            case_id = engagement_id if engagement_id else (
                f"{datetime.now().strftime('%Y%m%d')}-{_uuid.uuid4().hex[:6].upper()}"
            )

            # RT-1: registration on Run click
            reg_results = []
            if uploaded_files:
                cdir = case_dir(case_id)  # RT-2
                dm = DocumentManager(case_id)  # RG-1
                for f in uploaded_files:
                    try:
                        file_bytes = bytes(f.getbuffer())  # FW-1
                        dest = cdir / f.name               # FW-2
                        dest.write_bytes(file_bytes)
                        provenance = DocumentProvenance(
                            collection_method="uploaded_by_consultant",
                            collected_at=datetime.now(timezone.utc),
                            collector_role="consultant",
                            scope_authorized_by=f"case_{case_id}",
                            source_hash=hashlib.sha256(file_bytes).hexdigest(),
                        )
                        dm.register_document(  # RG-2
                            str(dest),
                            folder="uploaded",
                            doc_type=_infer_doc_type(f.name),  # RG-3
                            provenance=provenance,
                        )
                        size_mb = round(f.size / (1024 * 1024), 1)
                        reg_results.append({"name": f.name, "size_mb": size_mb, "ok": True})
                    except Exception as e:  # RG-4: per-file isolation
                        reg_results.append({"name": f.name, "size_mb": 0, "ok": False, "error": str(e)})
                # WI-4: dm NOT passed to workflow — registration only

            intake = CaseIntake(
                case_id=case_id,
                client_name=client_name.strip(),
                industry=values.get("industry", "").strip() if "industry" in values else "",
                primary_jurisdiction=values.get("jurisdiction", "UAE"),
                description=values.get("description", "").strip(),
                workflow="transaction_testing",
                language=get_project_language_standard(st),
                created_at=datetime.now(timezone.utc),
                engagement_id=engagement_id or None,
            )
            st.session_state.tt_reg_results = reg_results
            st.session_state.tt_intake = intake
            st.session_state.tt_params = {
                "engagement_context": _TT_CONTEXT_KEYS.get(
                    values.get("engagement_context", "Fraud Discovery (does fraud exist?)"),
                    "fraud_discovery",
                ),
                "fraud_typology": _TT_TYPOLOGY_KEYS.get(
                    values.get("fraud_typology", "Not applicable"),
                    None,
                ),
                "transaction_types": values.get("transaction_types", "").strip(),
                "date_range":        values.get("date_range", "").strip(),
                "data_inventory":    values.get("data_inventory", "TBD").strip() or "TBD",
                "evidence_standard": _TT_EVIDENCE_KEYS.get(
                    values.get("evidence_standard", "Internal Review"),
                    "internal_review",
                ),
                "sampling":          "full_population",
            }
            st.session_state.tt_stage = "ai_questions"
            st.rerun()

# ── STAGE: ai_questions ───────────────────────────────────────────────────────
elif st.session_state.tt_stage == "ai_questions":
    intake = st.session_state.tt_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = f"Client: {intake.client_name}. {intake.description}"
    if render_intake_questions(st, intake.case_id, intake_summary):
        st.session_state.tt_stage = "running"
        st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.tt_stage == "running":
    intake = st.session_state.tt_intake
    params = st.session_state.tt_params

    with st.expander("Intake Summary", expanded=False):
        st.write(
            f"**Client:** {intake.client_name} | "
            f"**Context:** {ENGAGEMENT_CONTEXTS.get(params['engagement_context'], params['engagement_context'])} | "
            f"**Date range:** {params['date_range']}"
        )

    # ── Document registration results (FS-1) ───────────────────────────────────
    for r in st.session_state.get("tt_reg_results", []):
        if r["ok"]:
            st.caption(f"✓ {r['name']} — {r['size_mb']}MB — registered")
        else:
            st.error(f"Failed to register {r['name']}: {r.get('error', 'unknown error')}")

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

    report_path = get_final_report_path(intake.case_id)
    if report_path.exists():
        docx_path = report_path.with_suffix(".docx")
        col_docx, col_md = st.columns(2)
        if docx_path.exists():
            with col_docx:
                st.download_button(
                    label="Download Word document",
                    data=docx_path.read_bytes(),
                    file_name=f"TT_{intake.client_name}_{intake.case_id}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
        with col_md:
            st.download_button(
                label="Download Markdown backup",
                data=report_path.read_text(encoding="utf-8"),
                file_name=f"TT_{intake.client_name}_{intake.case_id}.md",
                mime="text/markdown",
            )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

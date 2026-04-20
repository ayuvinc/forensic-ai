"""Transaction Testing — Streamlit page.

UX-003 shell: Zone A (intake + 2-stage context + doc upload) → Zone B (pipeline) → Zone C (output + download).
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir, get_final_report_path


def _infer_doc_type(filename: str) -> str:
    """Map file extension to DocumentManager doc_type string (RG-3)."""
    ext = Path(filename).suffix.lower()
    return {"pdf": "pdf", "docx": "word", "txt": "text", "xlsx": "excel"}.get(ext.lstrip("."), "text")

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
        for k in ["tt_stage", "tt_intake", "tt_params", "tt_result", "tt_reg_results"]:
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

        # ── Document upload — Zone A (UX-006, below intake, above Run) ──────────
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
            if not date_range.strip():
                st.error("Required: Transaction date range")
            else:
                # RT-1: registration on Run click
                from tools.document_manager import DocumentManager
                from schemas.documents import DocumentProvenance

                reg_results = []
                if uploaded_files:
                    cdir = case_dir(intake.case_id)  # RT-2
                    dm = DocumentManager(intake.case_id)  # RG-1
                    for f in uploaded_files:
                        try:
                            file_bytes = bytes(f.getbuffer())  # FW-1
                            dest = cdir / f.name               # FW-2
                            dest.write_bytes(file_bytes)
                            provenance = DocumentProvenance(
                                collection_method="uploaded_by_consultant",
                                collected_at=datetime.now(timezone.utc),
                                collector_role="consultant",
                                scope_authorized_by=f"case_{intake.case_id}",
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

                st.session_state.tt_reg_results = reg_results
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
        st.download_button(
            label="Download testing report (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"TT_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

"""Investigation Report — Streamlit page.

UX-003 shell: Zone A (intake + type/audience + doc upload) → Zone B (pipeline) → Zone C (output + download).
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status, PipelineEvent


def _infer_doc_type(filename: str) -> str:
    """Map file extension to DocumentManager doc_type string (RG-3)."""
    ext = Path(filename).suffix.lower()
    return {"pdf": "pdf", "docx": "word", "txt": "text", "xlsx": "excel"}.get(ext.lstrip("."), "text")

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
        for k in ["inv_stage", "inv_intake", "inv_params", "inv_result", "inv_dm", "inv_reg_results"]:
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

        # ── Document upload — Zone A (UX-006, below intake, above Run) ──────────
        uploaded_files = st.file_uploader(
            "Upload case documents (optional)",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "xlsx"],
            key="inv_docs",
        )
        st.warning("Maximum file size is 10MB per document.")
        if uploaded_files and len(uploaded_files) > 10:
            st.warning("Maximum 10 documents per case.")

        if st.button("Run Investigation", type="primary"):
            # RT-1: registration happens here on Run click — not on upload event
            from tools.file_tools import case_dir
            from tools.document_manager import DocumentManager
            from schemas.documents import DocumentProvenance

            dm = None
            reg_results = []
            if uploaded_files:
                cdir = case_dir(intake.case_id)  # RT-2: create folder before DocumentManager init
                dm = DocumentManager(intake.case_id)  # RG-1
                for f in uploaded_files:
                    try:
                        file_bytes = bytes(f.getbuffer())  # FW-1
                        dest = cdir / f.name               # FW-2: path from constant
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

            st.session_state.inv_dm = dm
            st.session_state.inv_reg_results = reg_results
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

    # ── Document registration results (FS-1) ───────────────────────────────────
    for r in st.session_state.get("inv_reg_results", []):
        if r["ok"]:
            st.caption(f"✓ {r['name']} — {r['size_mb']}MB — registered")
        else:
            st.error(f"Failed to register {r['name']}: {r.get('error', 'unknown error')}")

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
            document_manager=st.session_state.get("inv_dm"),  # WI-1
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

    from tools.file_tools import case_dir
    from streamlit_app.shared.done_zone import render_done_zone

    render_done_zone(
        st,
        case_id=intake.case_id,
        client_name=intake.client_name,
        report_path=case_dir(intake.case_id) / "final_report.en.md",
        workflow_label="Investigation Report",
        session_state_keys=["inv_stage", "inv_intake", "inv_params", "inv_result", "inv_dm", "inv_reg_results"],
        stage_key="inv_stage",
        enable_workpaper=True,
    )

"""Investigation Report — Streamlit page.

UX-003 shell: Zone A (intake + type/audience + doc upload) → Zone B (pipeline) → Zone C (output + download).
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import (
    render_engagement_banner,
    get_project_language_standard,
)
from streamlit_app.shared.hybrid_intake import (
    HybridIntakeEngine,
    _INVESTIGATION_FIELD_CONFIG,
)
from streamlit_app.shared.pipeline import run_in_status, PipelineEvent


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

st.title("Investigation Report")
st.caption("Full three-agent pipeline — Asset Misappropriation, Corruption, Cyber Fraud, and more")

INVESTIGATION_TYPES = {
    "asset_misappropriation":  "Asset Misappropriation",
    "financial_statement_fraud": "Financial Statement Fraud",
    "corruption_bribery":      "Corruption & Bribery",
    "cyber_fraud":             "Cyber Fraud / Digital Investigation",
    "procurement_fraud":       "Procurement Fraud",
    "revenue_leakage":         "Revenue Leakage",
    "compliance_investigation": "Compliance Investigation",
    # BA-IA-05: AUP — factual findings only, no conclusions (AICPA/IAASB)
    "agreed_upon_procedures":  "Agreed-Upon Procedures (AUP)",
    # BA-IA-06: Custom — model proposes structure before drafting
    "other_custom":            "Other / Custom",
}

_AUP_MAX_PROCEDURES = 20

AUDIENCES = {
    "management": "Management",
    "board": "Board",
    "legal_proceedings": "Legal Proceedings (Expert Witness)",
    "regulatory_submission": "Regulatory Submission",
}

if "inv_stage" not in st.session_state:
    st.session_state.inv_stage = "intake"

# Sidebar "Start New Case" resets both page state and engine state
_inv_engine = HybridIntakeEngine(st, _INVESTIGATION_FIELD_CONFIG, "investigation_report")

if st.session_state.inv_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["inv_stage", "inv_intake", "inv_params", "inv_result", "inv_dm", "inv_reg_results"]:
            st.session_state.pop(k, None)
        _inv_engine.reset()
        st.rerun()

# ── STAGE: intake (BA-IA-07: HybridIntakeEngine) ──────────────────────────────
if st.session_state.inv_stage == "intake":
    # Client name — from active engagement banner or manual entry
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    client_name = project_meta.get("client_name", "") if project_meta else ""
    if not client_name:
        client_name = st.text_input("Client name *", key="inv_client_name_manual")

    st.divider()

    # HybridIntakeEngine: structured fields (jurisdiction, inv_type, regulators,
    # evidence, audience, industry, description) + optional Remarks conversations.
    engine_result = _inv_engine.run()

    if engine_result is not None and client_name.strip():
        values = engine_result["values"]
        inv_type_label  = values.get("investigation_type", "")
        audience_label  = values.get("audience", "")
        description     = values.get("description", "")
        industry        = values.get("industry", "")
        jurisdiction    = values.get("jurisdiction", "UAE")

        # ── BA-IA-05: AUP procedures list ─────────────────────────────────────
        aup_procedures: list[str] = []
        if inv_type_label == "Agreed-Upon Procedures (AUP)":
            st.info(
                "AUP scope is locked at intake. The report will only cover procedures "
                "listed here — no additional scope items will be added. "
                "AICPA/IAASB agreed-upon procedures standards apply."
            )
            n_procedures = st.number_input(
                "Number of procedures",
                min_value=1,
                max_value=_AUP_MAX_PROCEDURES,
                value=st.session_state.get("inv_aup_count", 3),
                step=1,
                key="inv_aup_count",
            )
            for i in range(int(n_procedures)):
                proc = st.text_input(
                    f"Procedure {i + 1}",
                    key=f"inv_aup_proc_{i}",
                    placeholder="e.g. Obtain and inspect all vendor invoices above AED 50,000 for Q1 2026",
                )
                aup_procedures.append(proc)

        # ── BA-IA-06: Custom investigation — description already in engine ────
        # The description field in the engine captures the narrative. For Custom type
        # we just add the required prefix and show a notice.
        if inv_type_label == "Other / Custom":
            st.info(
                "Custom type: the model will propose a report structure based on your "
                "description above. You will confirm or adjust before drafting begins."
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

        # Validate AUP: at least one non-empty procedure required
        _aup_ready = (
            inv_type_label != "Agreed-Upon Procedures (AUP)"
            or any(p.strip() for p in aup_procedures)
        )
        _run_disabled = not _aup_ready

        if st.button("Run Investigation", type="primary", disabled=_run_disabled):
            import uuid as _uuid
            from tools.file_tools import case_dir
            from tools.document_manager import DocumentManager
            from schemas.documents import DocumentProvenance
            from streamlit_app.shared.intake import get_project_dm
            from schemas.case import CaseIntake

            # Build case_id: use engagement slug when in project context (P9-09a/c)
            case_id = engagement_id if engagement_id else (
                f"{datetime.now().strftime('%Y%m%d')}-{_uuid.uuid4().hex[:6].upper()}"
            )

            # Build description — AUP and Custom prefixes for pipeline detection
            if inv_type_label == "Agreed-Upon Procedures (AUP)":
                filled = [p.strip() for p in aup_procedures if p.strip()]
                procs  = "\n".join(f"{i+1}. {p}" for i, p in enumerate(filled))
                effective_description = f"AUP SCOPE — Procedures agreed with client:\n{procs}"
            elif inv_type_label == "Other / Custom":
                effective_description = (
                    f"CUSTOM INVESTIGATION — Structure to be proposed before drafting:\n{description}"
                )
            else:
                effective_description = description

            intake = CaseIntake(
                case_id=case_id,
                client_name=client_name.strip(),
                industry=industry.strip(),
                primary_jurisdiction=jurisdiction,
                description=effective_description,
                workflow="investigation_report",
                language=get_project_language_standard(st),
                created_at=datetime.now(timezone.utc),
                engagement_id=engagement_id or None,
            )

            # Document registration (RT-1: on Run click, not on upload)
            dm = None
            reg_results = []
            if uploaded_files:
                cdir = case_dir(intake.case_id)  # RT-2
                dm = DocumentManager(intake.case_id)
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
                        dm.register_document(str(dest), folder="uploaded",
                                             doc_type=_infer_doc_type(f.name),
                                             provenance=provenance)  # RG-2/3
                        size_mb = round(f.size / (1024 * 1024), 1)
                        reg_results.append({"name": f.name, "size_mb": size_mb, "ok": True})
                    except Exception as e:  # RG-4
                        reg_results.append({"name": f.name, "size_mb": 0, "ok": False, "error": str(e)})

            if dm is None:
                dm = get_project_dm(st)  # P9-09b

            st.session_state.inv_dm          = dm
            st.session_state.inv_reg_results = reg_results
            st.session_state.inv_intake      = intake
            st.session_state.inv_params      = {
                "investigation_type": inv_type_label,
                "audience":           audience_label,
                "language_standard":  get_project_language_standard(st),
            }
            st.session_state.inv_stage = "ai_questions"
            st.rerun()

# ── STAGE: ai_questions ───────────────────────────────────────────────────────
elif st.session_state.inv_stage == "ai_questions":
    intake = st.session_state.inv_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = (
        f"Workflow: Investigation Report\n"
        f"Investigation type: {st.session_state.get('inv_investigation_type', 'Not specified')}\n"
        f"Audience: {st.session_state.get('inv_audience', 'Not specified')}\n"
        f"Client: {intake.client_name}\n"
        f"Industry: {intake.industry}\n"
        f"Primary jurisdiction: {intake.primary_jurisdiction}\n"
        f"Description: {intake.description}"
    )
    if render_intake_questions(st, intake.case_id, intake_summary):
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
        st.session_state.inv_stage = "error"
        st.session_state.inv_error = str(e)
        st.rerun()

elif st.session_state.inv_stage == "error":
    st.error(f"Pipeline failed: {st.session_state.get('inv_error', 'Unknown error')}")
    if st.button("Start Over"):
        for k in ["inv_stage", "inv_intake", "inv_params", "inv_result", "inv_dm",
                  "inv_reg_results", "inv_error"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.inv_stage == "done":
    intake = st.session_state.inv_intake

    from tools.file_tools import case_dir, get_final_report_path
    from streamlit_app.shared.done_zone import render_done_zone

    render_done_zone(
        st,
        case_id=intake.case_id,
        client_name=intake.client_name,
        report_path=get_final_report_path(intake.case_id),
        workflow_label="Investigation Report",
        session_state_keys=["inv_stage", "inv_intake", "inv_params", "inv_result", "inv_dm", "inv_reg_results"],
        stage_key="inv_stage",
        enable_workpaper=True,
    )

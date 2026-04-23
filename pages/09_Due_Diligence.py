"""Due Diligence — Streamlit page.

UX-003 shell: Zone A (intake + subject fields + doc upload) → Zone B (pipeline) → Zone C (output + download).
Individual and Entity branches via selectbox.
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import render_engagement_banner, get_project_language_standard
from streamlit_app.shared.hybrid_intake import HybridIntakeEngine, _DD_FIELD_CONFIG
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir, get_final_report_path

# Screening level: map engine display string → pipeline key
_DD_DEPTH_MAP = {
    "Standard Phase 1": "standard_phase1",
    "Enhanced Phase 2":  "enhanced_phase2",
}

_DD_PURPOSE_OPTIONS = ["onboarding", "investment", "partnership", "employment", "acquisition", "other"]


def _infer_doc_type(filename: str) -> str:
    """Map file extension to DocumentManager doc_type string (RG-3)."""
    ext = Path(filename).suffix.lower()
    return {"pdf": "pdf", "docx": "word", "txt": "text", "xlsx": "excel"}.get(ext.lstrip("."), "text")

try:
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    st.error(f"Page failed to load: {_bootstrap_err}")
    st.stop()

st.title("Due Diligence")
st.caption("Individual and Entity DD — Standard Phase 1 and Enhanced Phase 2 branches")

if "dd_stage" not in st.session_state:
    st.session_state.dd_stage = "intake"

_dd_engine = HybridIntakeEngine(st, _DD_FIELD_CONFIG, "due_diligence")

if st.session_state.dd_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["dd_stage", "dd_intake", "dd_params", "dd_result", "dd_reg_results"]:
            st.session_state.pop(k, None)
        _dd_engine.reset()
        st.rerun()

# ── STAGE: intake (BA-IA-07: HybridIntakeEngine) ─────────────────────────────
if st.session_state.dd_stage == "intake":
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    client_name = project_meta.get("client_name", "") if project_meta else ""
    if not client_name:
        client_name = st.text_input("Client name *", key="dd_client_name_manual")

    st.divider()
    engine_result = _dd_engine.run()

    if engine_result is not None and client_name.strip():
        import uuid as _uuid
        from schemas.case import CaseIntake

        values = engine_result["values"]

        # FE-05: extended intake fields — stay outside engine per spec (BA-R-06 logic)
        subject_name = st.text_input(
            "Full legal name of subject *",
            placeholder="Individual: full name as on passport  |  Entity: registered legal name",
            key="dd_subject_name",
        )
        dd_purpose = st.selectbox(
            "Purpose of DD",
            _DD_PURPOSE_OPTIONS,
            format_func=lambda v: v.replace("_", " ").title(),
            key="dd_purpose_select",
        )
        subject_count = st.number_input(
            "Number of subjects",
            min_value=1,
            value=1,
            step=1,
            help="How many individuals or entities are being screened?",
        )
        relationship = st.radio(
            "Relationship type",
            ["Unrelated", "Related"],
            horizontal=True,
            help="Related subjects may share beneficial ownership or family ties.",
        )
        template_upload = st.file_uploader(
            "DD template (.docx, optional)",
            type=["docx"],
            key="dd_template_upload",
            help="Upload a firm-specific DD template to override the default.",
        )

        # ── Document upload — Zone A ──────────────────────────────────────────
        uploaded_files = st.file_uploader(
            "Upload case documents (optional)",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "xlsx"],
            key="dd_docs",
        )
        st.warning("Maximum file size is 10MB per document.")
        if uploaded_files and len(uploaded_files) > 10:
            st.warning("Maximum 10 documents per case.")

        if st.button("Run Due Diligence", type="primary", disabled=not subject_name.strip()):
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
                        dm.register_document(
                            str(dest),
                            folder="uploaded",
                            doc_type=_infer_doc_type(f.name),
                            provenance=provenance,
                        )
                        size_mb = round(f.size / (1024 * 1024), 1)
                        reg_results.append({"name": f.name, "size_mb": size_mb, "ok": True})
                    except Exception as e:
                        reg_results.append({"name": f.name, "size_mb": 0, "ok": False, "error": str(e)})

            subject_juris = values.get("subject_jurisdictions", [])
            if isinstance(subject_juris, str):
                subject_juris = [subject_juris]

            # FE-05: report_format routing (BA-R-06)
            report_format = "per_subject" if (subject_count == 1 and relationship == "Unrelated") else "consolidated"

            intake = CaseIntake(
                case_id=case_id,
                client_name=client_name.strip(),
                industry=values.get("industry", "").strip(),
                primary_jurisdiction=values.get("jurisdiction", "UAE"),
                description=f"DD subject: {subject_name.strip()}. {values.get('description', '').strip()}".strip(),
                workflow="due_diligence",
                language=get_project_language_standard(st),
                created_at=datetime.now(timezone.utc),
                engagement_id=engagement_id or None,
            )
            dd_params = {
                "subject_type":      values.get("subject_type", "Individual").lower(),
                "subject_name":      subject_name.strip(),
                "jurisdictions":     subject_juris,
                "dd_purpose":        dd_purpose,
                "screening_level":   _DD_DEPTH_MAP.get(values.get("dd_depth", "Standard Phase 1"), "standard_phase1"),
                "specific_concerns": values.get("description", "").strip(),
                "screening_lists":   ["all"],
                "deliverable_format": "full_report",
                "report_format":     report_format,
                "subject_count":     subject_count,
                "relationship":      relationship,
            }
            if template_upload is not None:
                dd_params["template_filename"] = template_upload.name

            st.session_state.dd_reg_results = reg_results
            st.session_state.dd_intake = intake
            st.session_state.dd_params = dd_params
            st.session_state.dd_stage = "ai_questions"
            st.rerun()

# ── STAGE: ai_questions ───────────────────────────────────────────────────────
elif st.session_state.dd_stage == "ai_questions":
    intake = st.session_state.dd_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = f"Client: {intake.client_name}. {intake.description}"
    if render_intake_questions(st, intake.case_id, intake_summary):
        st.session_state.dd_stage = "running"
        st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.dd_stage == "running":
    intake = st.session_state.dd_intake
    params = st.session_state.dd_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Subject:** {params['subject_name']} ({params['subject_type']}) | **Level:** {params['screening_level'].replace('_', ' ').title()}")

    # ── Document registration results (FS-1) ───────────────────────────────────
    for r in st.session_state.get("dd_reg_results", []):
        if r["ok"]:
            st.caption(f"✓ {r['name']} — {r['size_mb']}MB — registered")
        else:
            st.error(f"Failed to register {r['name']}: {r.get('error', 'unknown error')}")

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

    from streamlit_app.shared.done_zone import render_done_zone

    render_done_zone(
        st,
        case_id=intake.case_id,
        client_name=intake.client_name,
        report_path=get_final_report_path(intake.case_id),
        workflow_label="Due Diligence",
        session_state_keys=["dd_stage", "dd_intake", "dd_params", "dd_result", "dd_reg_results"],
        stage_key="dd_stage",
    )

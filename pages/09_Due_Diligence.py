"""Due Diligence — Streamlit page.

UX-003 shell: Zone A (intake + subject fields + doc upload) → Zone B (pipeline) → Zone C (output + download).
Individual and Entity branches via selectbox.
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import dd_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir, get_final_report_path


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

if st.session_state.dd_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["dd_stage", "dd_intake", "dd_params", "dd_result", "dd_reg_results"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.dd_stage == "intake":
    # Merged single-form intake (UX-F-02: eliminates two-phase render)
    result = dd_intake_form(st)

    if result is not None:
        intake, dd_params = result

        # FE-05: extended intake fields
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

        # ── Document upload — Zone A (below intake form, above pipeline start) ─
        uploaded_files = st.file_uploader(
            "Upload case documents (optional)",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "xlsx"],
            key="dd_docs",
        )
        st.warning("Maximum file size is 10MB per document.")
        if uploaded_files and len(uploaded_files) > 10:
            st.warning("Maximum 10 documents per case.")

        # RT-1: registration on pipeline start
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
            # WI-3: dm NOT passed to workflow — registration only

        # FE-05: routing based on subject_count + relationship (per BA-FE-02)
        if subject_count == 1 and relationship == "Unrelated":
            dd_params["report_format"] = "per_subject"
        else:
            dd_params["report_format"] = "consolidated"

        dd_params["subject_count"] = subject_count
        dd_params["relationship"] = relationship
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

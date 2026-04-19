"""Due Diligence — Streamlit page.

UX-003 shell: Zone A (intake + subject fields + doc upload) → Zone B (pipeline) → Zone C (output + download).
Individual and Entity branches via selectbox.
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir


def _infer_doc_type(filename: str) -> str:
    """Map file extension to DocumentManager doc_type string (RG-3)."""
    ext = Path(filename).suffix.lower()
    return {"pdf": "pdf", "docx": "word", "txt": "text", "xlsx": "excel"}.get(ext.lstrip("."), "text")

session = bootstrap(st)

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
    intake = generic_intake_form(st, "due_diligence", "Due Diligence — Intake")

    if intake is not None:
        subject_type = st.selectbox("Subject type", ["individual", "entity"], format_func=str.title)
        subject_name = st.text_input(
            "Full legal name of subject",
            placeholder="Individual: full name as on passport  |  Entity: registered legal name",
        )
        jurisdictions_raw = st.text_input(
            "Operating jurisdictions (comma-separated)",
            value=intake.primary_jurisdiction,
        )
        dd_purpose_options = ["onboarding", "investment", "partnership", "employment", "acquisition", "other"] if subject_type == "individual" else ["acquisition", "investment", "vendor_onboarding", "joint_venture", "partnership", "other"]
        dd_purpose = st.selectbox("Purpose of DD", dd_purpose_options, format_func=lambda v: v.replace("_", " ").title())
        screening_level = st.selectbox(
            "Screening level",
            ["standard_phase1", "enhanced_phase2"],
            format_func=lambda v: "Standard Phase 1" if v == "standard_phase1" else "Enhanced Phase 2",
        )
        specific_concerns = st.text_area("Specific concerns or red flags (optional)", height=80)

        # ── Document upload — Zone A (UX-006, below intake, above Run) ──────────
        uploaded_files = st.file_uploader(
            "Upload case documents (optional)",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "xlsx"],
            key="dd_docs",
        )
        st.warning("Maximum file size is 10MB per document.")
        if uploaded_files and len(uploaded_files) > 10:
            st.warning("Maximum 10 documents per case.")

        if st.button("Run Due Diligence", type="primary"):
            if not subject_name.strip():
                st.error("Required: Subject name")
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
                    # WI-3: dm NOT passed to workflow — registration only

                jurisdictions = [j.strip() for j in jurisdictions_raw.split(",") if j.strip()]
                st.session_state.dd_reg_results = reg_results
                st.session_state.dd_intake = intake
                st.session_state.dd_params = {
                    "subject_type": subject_type,
                    "subject_name": subject_name.strip(),
                    "jurisdictions": jurisdictions,
                    "dd_purpose": dd_purpose,
                    "screening_level": screening_level,
                    "specific_concerns": specific_concerns.strip(),
                    "screening_lists": ["all"],
                    "deliverable_format": "full_report",
                }
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
    result = st.session_state.dd_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Due Diligence report complete — Case ID: `{intake.case_id}`")

    report_path = case_dir(intake.case_id) / "final_report.en.md"
    if report_path.exists():
        st.download_button(
            label="Download DD report (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"DD_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

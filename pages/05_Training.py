"""Training Material Generator — Streamlit page.

UX-003 shell: Zone A (intake + topic/audience) → Zone B (pipeline) → Zone C (output + download).
"""

import streamlit as st
from datetime import datetime, timezone
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import render_engagement_banner, get_project_language_standard
from streamlit_app.shared.hybrid_intake import HybridIntakeEngine, _TRAINING_FIELD_CONFIG
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir, get_final_report_path

# Label → pipeline key maps
_TR_TOPIC_KEYS = {
    "AML Awareness":                "aml_awareness",
    "Fraud Awareness":              "fraud_awareness",
    "Bribery & Corruption Awareness": "bribery_corruption_awareness",
    "Data Privacy":                 "data_privacy",
    "Whistleblowing Procedures":    "whistleblowing_procedures",
    "KYC Procedures":               "kyc_procedures",
}
_TR_AUDIENCE_KEYS = {
    "All Staff":         "all_staff",
    "Finance Team":      "finance_team",
    "Senior Management": "senior_management",
    "Board / Directors": "board_directors",
    "Compliance Team":   "compliance_team",
    "Front Line Staff":  "front_line_staff",
}

# Kept for running-stage display
TRAINING_TOPICS = {v: k_label for k_label, v in _TR_TOPIC_KEYS.items()}
TARGET_AUDIENCES = {v: k_label for k_label, v in _TR_AUDIENCE_KEYS.items()}

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

st.title("Training Material")
st.caption("Generate role-specific AML, fraud awareness, and compliance training modules")

_tr_engine = HybridIntakeEngine(st, _TRAINING_FIELD_CONFIG, "training_material")

if "tr_stage" not in st.session_state:
    st.session_state.tr_stage = "intake"

if st.session_state.tr_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["tr_stage", "tr_intake", "tr_params", "tr_result"]:
            st.session_state.pop(k, None)
        _tr_engine.reset()
        st.rerun()

# ── STAGE: intake (BA-IA-07: HybridIntakeEngine) ─────────────────────────────
if st.session_state.tr_stage == "intake":
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    client_name = project_meta.get("client_name", "") if project_meta else ""
    if not client_name:
        client_name = st.text_input("Client name *", key="tr_client_name_manual")
    project_name = st.text_input(
        "Project name *", key="tr_project_name_manual",
        placeholder="e.g. ABC AML Training 2024",
        help="Used as the folder name for all outputs from this engagement.",
    )

    st.divider()
    engine_result = _tr_engine.run()

    if engine_result is not None and client_name.strip():
        from schemas.case import CaseIntake
        from tools.file_tools import slugify_project_name

        if not project_name.strip():
            st.error("Project name is required.")
            st.stop()

        values = engine_result["values"]
        case_id = engagement_id if engagement_id else slugify_project_name(project_name)

        # Duration: "60 min" → 60; "Custom" → 60 default
        duration_str = values.get("duration", "60 min")
        if duration_str == "Custom":
            duration = 60
        else:
            try:
                duration = int(duration_str.replace(" min", ""))
            except ValueError:
                duration = 60

        intake = CaseIntake(
            case_id=case_id,
            project_name=project_name.strip(),
            client_name=client_name.strip(),
            industry=values.get("industry", "").strip(),
            primary_jurisdiction=values.get("jurisdiction", "UAE"),
            description=values.get("description", "").strip(),
            workflow="training_material",
            language=get_project_language_standard(st),
            created_at=datetime.now(timezone.utc),
            engagement_id=engagement_id or None,
        )
        st.session_state.tr_intake = intake
        st.session_state.tr_params = {
            "topic":              _TR_TOPIC_KEYS.get(values.get("topic", "AML Awareness"), "aml_awareness"),
            "target_audience":    _TR_AUDIENCE_KEYS.get(values.get("target_audience", "All Staff"), "all_staff"),
            "duration":           duration,
            "include_quiz":       values.get("include_quiz", "Yes") == "Yes",
            "include_case_study": values.get("include_case_study", "Yes") == "Yes",
        }
        st.session_state.tr_stage = "ai_questions"
        st.rerun()

# ── STAGE: ai_questions ───────────────────────────────────────────────────────
elif st.session_state.tr_stage == "ai_questions":
    intake = st.session_state.tr_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = f"Client: {intake.client_name}. {intake.description}"
    if render_intake_questions(st, intake.case_id, intake_summary):
        st.session_state.tr_stage = "running"
        st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.tr_stage == "running":
    intake = st.session_state.tr_intake
    params = st.session_state.tr_params

    with st.expander("Intake Summary", expanded=False):
        st.write(
            f"**Client:** {intake.client_name} | "
            f"**Topic:** {TRAINING_TOPICS.get(params['topic'], params['topic'])} | "
            f"**Audience:** {TARGET_AUDIENCES.get(params['target_audience'], params['target_audience'])}"
        )

    # Sprint-FOLDER-01: pre-create case folder so it's visible on disk before pipeline runs
    from tools.file_tools import write_state as _write_state
    _cdir = case_dir(intake.case_id)
    if not (_cdir / "state.json").exists():
        _write_state(intake.case_id, {
            "case_id":    intake.case_id,
            "workflow":   "training_material",
            "status":     "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        })

    from workflows.training_material import run_training_material_workflow

    try:
        result = run_in_status(
            st,
            "Generating training material...",
            run_training_material_workflow,
            intake,
            headless_params=params,
        )
        st.session_state.tr_result = result
        st.session_state.tr_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.tr_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.tr_stage == "done":
    intake = st.session_state.tr_intake
    result = st.session_state.tr_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Training material complete — Case ID: `{intake.case_id}`")

    report_path = get_final_report_path(intake.case_id)
    if report_path.exists():
        docx_path = report_path.with_suffix(".docx")
        col_docx, col_md = st.columns(2)
        if docx_path.exists():
            with col_docx:
                st.download_button(
                    label="Download Word document",
                    data=docx_path.read_bytes(),
                    file_name=f"Training_{intake.client_name}_{intake.case_id}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
        with col_md:
            st.download_button(
                label="Download Markdown backup",
                data=report_path.read_text(encoding="utf-8"),
                file_name=f"Training_{intake.client_name}_{intake.case_id}.md",
                mime="text/markdown",
            )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

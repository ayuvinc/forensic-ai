"""Sanctions Screening — Streamlit page.

UX-003 shell + Sanctions-specific override:
- knowledge_only mode: st.error warning + acknowledgement checkbox required BEFORE intake form.
- Run button disabled until checkbox ticked (if knowledge_only).
"""

import streamlit as st
import config
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status, PipelineEvent
from tools.file_tools import case_dir

session = bootstrap(st)

st.title("Sanctions Screening")
st.caption("OFAC, UN, EU, UK OFSI, and UAE local sanctions list screening")

# ── P8-08i: knowledge_only gate (UX-003 Sanctions override) ──────────────────
knowledge_only = config.RESEARCH_MODE != "live"
acknowledged = True  # default: live mode, no gate

if knowledge_only:
    st.error(
        "**SANCTIONS SCREENING — LIVE DATA DISABLED**\n\n"
        "This output is based on model knowledge only. "
        "No live OFAC / UN / EU / UK OFSI / UAE sanctions screening will be conducted.\n\n"
        "**This result CANNOT be used as a sanctions clearance.**\n\n"
        "To run a live screen: set `RESEARCH_MODE=live` in `.env` with a valid TAVILY_API_KEY."
    )
    acknowledged = st.checkbox(
        "I understand this is not a live screening — proceed anyway.",
        key="sanctions_acknowledged",
        value=st.session_state.get("sanctions_acknowledged", False),
    )

if "san_stage" not in st.session_state:
    st.session_state.san_stage = "intake"

if st.session_state.san_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["san_stage", "san_intake", "san_params", "san_result", "sanctions_acknowledged"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.san_stage == "intake":
    intake = generic_intake_form(st, "sanctions_screening", "Sanctions Screening — Intake")

    if intake is not None:
        subject_name = st.text_input(
            "Name of individual or entity to screen",
            placeholder="Full legal name",
        )
        subject_type = st.selectbox("Subject type", ["individual", "entity"], format_func=str.title)
        nationalities_raw = st.text_input(
            "Nationality / jurisdiction of incorporation (comma-separated)",
            value=intake.primary_jurisdiction,
        )
        aliases_raw = st.text_input("Known aliases or alternate name spellings (comma-separated, optional)")
        dob_or_reg = st.text_input("Date of birth or company reg number (optional — improves match accuracy)")
        purpose = st.selectbox(
            "Purpose of screening",
            ["onboarding", "transaction", "periodic_review", "acquisition", "regulatory", "other"],
            format_func=lambda v: v.replace("_", " ").title(),
        )
        output_format = st.selectbox(
            "Output format",
            ["full_report", "clearance_memo"],
            format_func=lambda v: "Full Report" if v == "full_report" else "Clearance Memo",
        )

        # Run button is disabled until knowledge_only is acknowledged
        run_disabled = knowledge_only and not acknowledged
        if st.button("Run Sanctions Screen", type="primary", disabled=run_disabled):
            if not subject_name.strip():
                st.error("Required: Subject name")
            else:
                nationalities = [n.strip() for n in nationalities_raw.split(",") if n.strip()]
                aliases = [a.strip() for a in aliases_raw.split(",") if a.strip()] if aliases_raw else []
                st.session_state.san_intake = intake
                st.session_state.san_params = {
                    "subject_name": subject_name.strip(),
                    "subject_type": subject_type,
                    "nationalities": nationalities,
                    "aliases": aliases,
                    "dob_or_reg": dob_or_reg.strip(),
                    "selected_lists": "all",
                    "screen_associates": False,
                    "purpose": purpose,
                    "output_format": output_format,
                    "specific_concerns": "",
                }
                st.session_state.san_stage = "running"
                st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.san_stage == "running":
    intake = st.session_state.san_intake
    params = st.session_state.san_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Subject:** {params['subject_name']} ({params['subject_type']}) | **Lists:** {params['selected_lists']}")

    if knowledge_only:
        warn = PipelineEvent(
            severity="WARNING",
            message="Running in Knowledge Only mode — no live sanctions database queried. Output is not a compliance clearance.",
            agent="sanctions_page",
        )
        st.warning(f"[{warn.agent}] {warn.message}")

    from workflows.sanctions_screening import run_sanctions_screening_workflow

    try:
        result = run_in_status(
            st,
            "Running sanctions screening...",
            run_sanctions_screening_workflow,
            intake,
            session.registry,
            session.hook_engine,
            headless_params=params,
        )
        st.session_state.san_result = result
        st.session_state.san_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.san_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.san_stage == "done":
    intake = st.session_state.san_intake
    result = st.session_state.san_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Sanctions screening complete — Case ID: `{intake.case_id}`")

    if knowledge_only:
        st.warning("Reminder: This output was generated in Knowledge Only mode and is NOT a live sanctions clearance.")

    report_path = case_dir(intake.case_id) / "final_report.en.md"
    if report_path.exists():
        st.download_button(
            label="Download screening report (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"Sanctions_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

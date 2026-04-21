"""Client Proposal Generator — Streamlit page.

UX-003 shell + Proposal-specific: after success, checkbox to chain to PPT Pack (UX-D-01).
"""

import streamlit as st
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import generic_intake_form
from streamlit_app.shared.pipeline import run_in_status
from tools.file_tools import case_dir, get_final_report_path

try:
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    st.error(f"Page failed to load: {_bootstrap_err}")
    st.stop()

st.title("Client Proposal")
st.caption("Generate a full 7-section forensic consulting proposal with team selection and fee structure")

# UX-F-07: pre-flight firm profile check — warn if profile is incomplete
_firm_json = __import__("config", fromlist=["FIRM_PROFILE_DIR"]).FIRM_PROFILE_DIR / "firm.json"
if _firm_json.exists():
    import json as _json
    _profile = _json.loads(_firm_json.read_text(encoding="utf-8"))
    _missing = [f for f, v in [
        ("Firm Name", _profile.get("firm_name", "").strip()),
        ("Pricing Model", _profile.get("pricing_model", "").strip()),
        ("Terms & Conditions", _profile.get("terms_and_conditions", "").strip()),
    ] if not v]
    if _missing:
        st.warning(
            f"Firm profile incomplete — missing: {', '.join(_missing)}. "
            "Go to **Settings** to fill in these fields before generating a proposal."
        )
else:
    st.warning("Firm profile not set up. Go to **Settings** to configure it before generating a proposal.")

if "prop_stage" not in st.session_state:
    st.session_state.prop_stage = "intake"

if st.session_state.prop_stage != "intake":
    if st.sidebar.button("Start New Case"):
        for k in ["prop_stage", "prop_intake", "prop_params", "prop_result"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.prop_stage == "intake":
    intake = generic_intake_form(st, "client_proposal", "Client Proposal — Intake")

    if intake is not None:
        prospect_name = st.text_input(
            "Prospect / client name (if different from above)",
            value=intake.client_name,
        )
        contact_person = st.text_input("Contact person at prospect (optional)")
        proposal_scope = st.text_area(
            "Specific scope to address in proposal",
            value=intake.description,
            height=100,
        )
        fee_notes = st.text_input(
            "Custom fee notes (leave blank to use default pricing model)",
            value="",
        )

        if st.button("Generate Proposal", type="primary"):
            st.session_state.prop_intake = intake
            st.session_state.prop_params = {
                "prospect_name": prospect_name.strip() or intake.client_name,
                "contact_person": contact_person.strip(),
                "proposal_scope": proposal_scope.strip() or intake.description,
                "fee_notes": fee_notes.strip(),
            }
            st.session_state.prop_stage = "ai_questions"
            st.rerun()

# ── STAGE: ai_questions ───────────────────────────────────────────────────────
elif st.session_state.prop_stage == "ai_questions":
    intake = st.session_state.prop_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = f"Client: {intake.client_name}. {intake.description}"
    if render_intake_questions(st, intake.case_id, intake_summary):
        st.session_state.prop_stage = "running"
        st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.prop_stage == "running":
    intake = st.session_state.prop_intake
    params = st.session_state.prop_params

    with st.expander("Intake Summary", expanded=False):
        st.write(f"**Prospect:** {params['prospect_name']} | **Contact:** {params.get('contact_person', '—')}")

    from workflows.client_proposal import run_client_proposal_workflow

    try:
        result = run_in_status(
            st,
            "Drafting proposal...",
            run_client_proposal_workflow,
            intake,
            session.registry,
            session.hook_engine,
            headless_params=params,
        )
        st.session_state.prop_result = result
        st.session_state.prop_stage = "done"
        st.rerun()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        if st.button("Start Over"):
            st.session_state.prop_stage = "intake"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.prop_stage == "done":
    intake = st.session_state.prop_intake
    result = st.session_state.prop_result

    if not result:
        st.warning("No output was generated. Check the pipeline log and try again.")
    else:
        st.success(f"Proposal complete — Case ID: `{intake.case_id}`")

    report_path = get_final_report_path(intake.case_id)
    if report_path.exists():
        st.download_button(
            label="Download proposal (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"Proposal_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    st.markdown(f"**Case ID:** `{intake.case_id}`")

    # UX-003 Proposal-specific: chain to PPT Pack
    st.divider()
    chain_to_ppt = st.checkbox("Also generate PPT prompt pack for this engagement?")
    if chain_to_ppt:
        st.info("Navigate to **PPT Pack** in the sidebar and use Case ID: `" + intake.case_id + "` with the same client name.")

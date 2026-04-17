"""FRM Risk Register — Streamlit page (fixes FE-07).

Three-stage workflow managed via st.session_state["frm_stage"]:
  intake    → user fills company profile + selects modules
  running   → pipeline runs in st.status with live log (FE-07 fix: no spinner collision)
  reviewing → each RiskItem shown as st.expander card with A/F/R selectbox
  done      → finalized report + download button

This page calls run_frm_pipeline() and run_frm_finalize() directly, bypassing
the CLI-only _frm_approve_flag_rewrite_loop. The review loop here covers ALL
modules (not just Module 2 as in CLI) — this aligns with BA-002 Step 5.
"""

import streamlit as st
import config
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import frm_intake_form
from streamlit_app.shared.pipeline import run_in_status, PipelineEvent

# ── Session bootstrap ─────────────────────────────────────────────────────────
session = bootstrap(st)

st.title("FRM Risk Register")
st.caption("Fraud Risk Management — multi-module assessment pipeline")

# ── Stage initialisation ──────────────────────────────────────────────────────
if "frm_stage" not in st.session_state:
    st.session_state.frm_stage = "intake"

# Reset button — available on all stages except intake
if st.session_state.frm_stage != "intake":
    if st.sidebar.button("Start new FRM case"):
        for key in ["frm_stage", "frm_intake", "frm_modules", "frm_result", "frm_reviewed"]:
            st.session_state.pop(key, None)
        st.rerun()

# ── STAGE: intake ─────────────────────────────────────────────────────────────
if st.session_state.frm_stage == "intake":
    result = frm_intake_form(st)
    if result is not None:
        intake, selected_modules = result
        st.session_state.frm_intake = intake
        st.session_state.frm_modules = selected_modules
        st.session_state.frm_stage = "running"
        st.rerun()

# ── STAGE: running ────────────────────────────────────────────────────────────
elif st.session_state.frm_stage == "running":
    intake = st.session_state.frm_intake
    selected_modules = st.session_state.frm_modules

    st.info(
        f"Running pipeline for **{intake.client_name}** — "
        f"{len(selected_modules)} module(s)"
    )

    from workflows.frm_risk_register import run_frm_pipeline

    # Emit WARNING before pipeline starts if running in degraded research mode
    if config.RESEARCH_MODE == "knowledge_only":
        warn = PipelineEvent(
            severity="WARNING",
            message="Running in Knowledge Only mode — no live regulatory data. Citations will be limited.",
            agent="frm_page",
        )
        st.warning(f"[{warn.agent}] {warn.message}")

    try:
        risk_items, citations, completed_modules, exec_summary = run_in_status(
            st,
            "Running FRM pipeline...",
            run_frm_pipeline,
            intake,
            selected_modules,
            session.registry,
            session.hook_engine,
        )

        # Zero items is a CRITICAL pipeline outcome — surface clearly before advancing
        if not risk_items:
            crit = PipelineEvent(
                severity="CRITICAL",
                message="Pipeline returned 0 risk items. Check intake data or switch to live research mode.",
                agent="frm_page",
            )
            st.error(f"[{crit.agent}] {crit.message}")
            st.session_state.frm_stage = "reviewing"  # advance so empty-state UX renders
        else:
            st.session_state.frm_stage = "reviewing"

        st.session_state.frm_result = {
            "risk_items": risk_items,
            "citations": citations,
            "completed_modules": completed_modules,
            "exec_summary": exec_summary,
        }
        # Initialise review decisions: default all to "approve"
        st.session_state.frm_reviewed = {r.risk_id: {"action": "approve", "note": ""} for r in risk_items}
        st.rerun()
    except Exception:
        st.session_state.frm_stage = "intake"

# ── STAGE: reviewing ──────────────────────────────────────────────────────────
elif st.session_state.frm_stage == "reviewing":
    result = st.session_state.frm_result
    risk_items = result["risk_items"]
    reviewed = st.session_state.frm_reviewed

    st.subheader(f"Review {len(risk_items)} Risk Item(s)")
    st.caption(
        "Review applies to all modules (aligns with BA-002 Step 5). "
        "Approve, Flag with note, or Rewrite via Haiku."
    )

    if not risk_items:
        st.warning("No risk items were generated. Check the pipeline log and try again.")
        if st.button("Back to intake"):
            st.session_state.frm_stage = "intake"
            st.rerun()
    else:
        # Render each risk item as an expander card
        for risk in risk_items:
            rating_label = "HIGH" if risk.risk_rating >= 16 else ("MEDIUM" if risk.risk_rating >= 9 else "LOW")
            with st.expander(f"{risk.risk_id} — {risk.title} [{rating_label}: {risk.risk_rating}/25]"):
                st.markdown(f"**Category:** {risk.category}")
                st.markdown(f"**Likelihood:** {risk.likelihood} | **Impact:** {risk.impact} | **Rating:** {risk.risk_rating}/25")
                st.markdown(f"**Description:** {risk.description}")
                if risk.recommendations:
                    st.markdown("**Recommendations:** " + "; ".join(risk.recommendations[:2]))

                action = st.selectbox(
                    "Action",
                    ["approve", "flag", "rewrite"],
                    key=f"action_{risk.risk_id}",
                    index=["approve", "flag", "rewrite"].index(reviewed[risk.risk_id]["action"]),
                )
                reviewed[risk.risk_id]["action"] = action

                if action == "flag":
                    note = st.text_input("Flag note (shown in report)", key=f"note_{risk.risk_id}",
                                         value=reviewed[risk.risk_id].get("note", ""))
                    reviewed[risk.risk_id]["note"] = note

                elif action == "rewrite":
                    instructions = st.text_input(
                        "Rewrite instructions", key=f"rewrite_{risk.risk_id}",
                        value=reviewed[risk.risk_id].get("note", ""),
                    )
                    reviewed[risk.risk_id]["note"] = instructions

        st.session_state.frm_reviewed = reviewed

        st.divider()
        if st.button("Finalize Risk Register", type="primary"):
            st.session_state.frm_stage = "done"
            st.rerun()

# ── STAGE: done ───────────────────────────────────────────────────────────────
elif st.session_state.frm_stage == "done":
    from workflows.frm_risk_register import run_frm_finalize, _rewrite_risk_item
    from schemas.artifacts import RiskItem

    result = st.session_state.frm_result
    reviewed = st.session_state.frm_reviewed
    intake = st.session_state.frm_intake
    risk_items: list[RiskItem] = result["risk_items"]

    # Apply review decisions to items
    finalized: list[RiskItem] = []
    for risk in risk_items:
        decision = reviewed.get(risk.risk_id, {"action": "approve", "note": ""})
        action = decision["action"]
        note = decision.get("note", "")

        if action == "approve":
            finalized.append(risk)
        elif action == "flag":
            flagged = risk.model_copy(update={
                "title": f"[FLAGGED] {risk.title}",
                "description": f"{risk.description}\n\nCONSULTANT FLAG: {note}",
            })
            finalized.append(flagged)
        elif action == "rewrite" and note:
            # Single-turn Haiku rewrite
            from agents.junior_analyst.agent import JuniorAnalyst
            junior = JuniorAnalyst(session.registry, session.hook_engine, None, "frm_risk_register")
            rewritten = _rewrite_risk_item(risk, note, intake, junior)
            finalized.append(rewritten)
        else:
            finalized.append(risk)  # no instructions — keep original

    with st.spinner("Finalizing and writing report..."):
        deliverable = run_frm_finalize(
            intake,
            finalized,
            result["citations"],
            result["completed_modules"],
            result["exec_summary"],
        )

    st.success(f"FRM Risk Register complete — {len(finalized)} risks across {len(result['completed_modules'])} module(s)")

    # Download button for the markdown report
    from tools.file_tools import case_dir
    report_path = case_dir(intake.case_id) / "final_report.en.md"
    if report_path.exists():
        st.download_button(
            label="Download final_report.en.md",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"FRM_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )

    st.markdown(f"**Case ID:** `{intake.case_id}`")
    st.markdown(f"**Location:** `cases/{intake.case_id}/`")

    # Show executive summary inline
    if deliverable.executive_summary:
        with st.expander("Executive Summary"):
            st.markdown(deliverable.executive_summary)

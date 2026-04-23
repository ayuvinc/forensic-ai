"""FRM Risk Register — Streamlit page (fixes FE-07).

Stage flow managed via st.session_state["frm_stage"]:
  intake   → user fills company profile + selects modules (frm_intake_form owns the Run button)
  confirm  → document upload + "Run FRM Pipeline" button (Zone A, UX-006)
  running  → pipeline runs in st.status with live log (FE-07 fix: no spinner collision)
  reviewing → each RiskItem shown as st.expander card with A/F/R selectbox
  done     → finalized report + download button

This page calls run_frm_pipeline() and run_frm_finalize() directly, bypassing
the CLI-only _frm_approve_flag_rewrite_loop. The review loop here covers ALL
modules (not just Module 2 as in CLI) — this aligns with BA-002 Step 5.
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
import config
from streamlit_app.shared.session import bootstrap
from streamlit_app.shared.intake import render_engagement_banner, get_project_language_standard
from streamlit_app.shared.hybrid_intake import (
    HybridIntakeEngine,
    _FRM_FIELD_CONFIG,
    FRM_MODULE_DEPENDENCIES,
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


def _render_ai_review_badges(st, case_id: str, risk_items) -> None:
    """Render P9-08e AI review support-level badges per risk item (green/amber/red).

    Loads ai_review_{date}.json from D_Working_Papers/. If not found, shows nothing.
    Badge click expands to show evidence_cited and logic_gaps.
    """
    import json as _json
    from pathlib import Path as _Path
    from tools.file_tools import case_dir

    # Find today's or most recent ai_review file
    cdir = case_dir(case_id)
    wp_dir = cdir / "D_Working_Papers"
    if not wp_dir.exists():
        return

    review_files = sorted(wp_dir.glob("ai_review_*.json"), reverse=True)
    if not review_files:
        return

    try:
        data = _json.loads(review_files[0].read_text(encoding="utf-8"))
    except Exception:
        return

    annotations_by_id = {a["finding_id"]: a for a in data.get("annotations", [])}
    if not annotations_by_id:
        return

    _BADGE_COLORS = {
        "supported":           ("🟢", "SUPPORTED"),
        "partially_supported": ("🟡", "PARTIAL"),
        "unsupported":         ("🔴", "UNSUPPORTED"),
    }

    st.subheader("AI Evidence Review")
    st.caption("Support level per risk item — based on citations in the pipeline output.")

    for risk in risk_items:
        ann = annotations_by_id.get(risk.risk_id)
        if not ann:
            continue
        icon, label = _BADGE_COLORS.get(ann["support_level"], ("⚪", "UNKNOWN"))
        with st.expander(f"{icon} {risk.risk_id} — {risk.title} [{label}]"):
            if ann.get("evidence_cited"):
                st.markdown("**Evidence cited:**")
                for e in ann["evidence_cited"]:
                    st.markdown(f"- {e}")
            if ann.get("logic_gaps"):
                st.markdown("**Logic gaps:**")
                for g in ann["logic_gaps"]:
                    st.markdown(f"- {g}")
            if ann.get("rewritten_text"):
                st.markdown("**AI-suggested rewrite:**")
                st.markdown(ann["rewritten_text"])

# ── Session bootstrap ─────────────────────────────────────────────────────────
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

st.title("FRM Risk Register")
st.caption("Fraud Risk Management — multi-module assessment pipeline")

# ── Stage initialisation ──────────────────────────────────────────────────────
if "frm_stage" not in st.session_state:
    st.session_state.frm_stage = "intake"

# Engine instantiated once per page load; namespaced to "frm" in session_state
_frm_engine = HybridIntakeEngine(st, _FRM_FIELD_CONFIG, "frm")

# Reset button — available on all stages except intake
if st.session_state.frm_stage != "intake":
    if st.sidebar.button("Start new FRM case"):
        for key in ["frm_stage", "frm_intake", "frm_modules", "frm_result", "frm_reviewed", "frm_dm", "frm_reg_results"]:
            st.session_state.pop(key, None)
        _frm_engine.reset()
        st.rerun()

# ── STAGE: intake (BA-IA-07: HybridIntakeEngine) ─────────────────────────────
if st.session_state.frm_stage == "intake":
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    client_name = project_meta.get("client_name", "") if project_meta else ""
    if not client_name:
        client_name = st.text_input("Client name *", key="frm_client_name_manual")

    st.divider()

    engine_result = _frm_engine.run()

    if engine_result is not None and client_name.strip():
        import uuid as _uuid
        from datetime import datetime, timezone
        from schemas.case import CaseIntake

        values = engine_result["values"]

        # Build selected_modules list from 8 individual Yes/No radio fields (D1)
        selected_modules = [n for n in range(1, 9) if values.get(f"module_{n}") == "Yes"]
        if not selected_modules:
            st.error("Select at least one module.")
            st.stop()

        # Module dependency enforcement: auto-add required modules (mirrors frm_intake_form logic)
        selected_set = set(selected_modules)
        missing_deps: set[int] = set()
        for mod, deps in FRM_MODULE_DEPENDENCIES.items():
            if mod in selected_set:
                for dep in deps:
                    if dep not in selected_set:
                        missing_deps.add(dep)
        if missing_deps:
            auto_added = sorted(missing_deps)
            selected_modules = sorted(selected_set | missing_deps)
            st.warning(f"Module(s) {auto_added} added automatically — required by the selected modules.")

        case_id = engagement_id if engagement_id else (
            f"{datetime.now().strftime('%Y%m%d')}-{_uuid.uuid4().hex[:6].upper()}"
        )
        intake = CaseIntake(
            case_id=case_id,
            client_name=client_name.strip(),
            industry=values.get("industry", "").strip(),
            primary_jurisdiction=values.get("jurisdiction", "UAE"),
            description=values.get("description", "").strip(),
            company_size=values.get("company_size"),
            workflow="frm_risk_register",
            language=get_project_language_standard(st),
            created_at=datetime.now(timezone.utc),
            engagement_id=engagement_id or None,
        )
        st.session_state.frm_intake = intake
        st.session_state.frm_modules = selected_modules
        st.session_state.frm_stage = "confirm"
        st.rerun()

# ── STAGE: confirm — document upload + final Run button ───────────────────────
elif st.session_state.frm_stage == "confirm":
    intake = st.session_state.frm_intake
    st.info(
        f"Ready to run FRM for **{intake.client_name}**. "
        "Upload any supporting documents below, then click Run."
    )

    uploaded_files = st.file_uploader(
        "Upload case documents (optional)",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "xlsx"],
        key="frm_docs",
    )
    st.warning("Maximum file size is 10MB per document.")
    if uploaded_files and len(uploaded_files) > 10:
        st.warning("Maximum 10 documents per case.")

    if st.button("Run FRM Pipeline", type="primary"):
        # RT-1: registration happens on Run click
        from tools.file_tools import case_dir
        from tools.document_manager import DocumentManager
        from schemas.documents import DocumentProvenance

        dm = None
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

        # P9-09b: fall back to project DM when no files uploaded but engagement active
        if dm is None:
            from streamlit_app.shared.intake import get_project_dm
            dm = get_project_dm(st)

        st.session_state.frm_dm = dm
        st.session_state.frm_reg_results = reg_results

        # P9-UI-02: write initial state.json with engagement_id before pipeline runs
        # so mark_deliverable_written() preserves it when it reads and rewrites state
        engagement_id = st.session_state.get("active_project") or ""
        if engagement_id:
            from tools.file_tools import write_state
            from datetime import datetime, timezone
            write_state(intake.case_id, {
                "case_id":       intake.case_id,
                "workflow":      "frm_risk_register",
                "status":        "intake_created",
                "last_updated":  datetime.now(timezone.utc).isoformat(),
                "client_name":   intake.client_name,
                "engagement_id": engagement_id,
            })

        st.session_state.frm_stage = "ai_questions"
        st.rerun()

# ── STAGE: ai_questions ───────────────────────────────────────────────────────
elif st.session_state.frm_stage == "ai_questions":
    intake = st.session_state.frm_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = f"Client: {intake.client_name}. {intake.description}"
    if render_intake_questions(st, intake.case_id, intake_summary):
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

    # ── Document registration results (FS-1) ───────────────────────────────────
    for r in st.session_state.get("frm_reg_results", []):
        if r["ok"]:
            st.caption(f"✓ {r['name']} — {r['size_mb']}MB — registered")
        else:
            st.error(f"Failed to register {r['name']}: {r.get('error', 'unknown error')}")

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
            document_manager=st.session_state.get("frm_dm"),  # WI-2
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

    rewrite_count = sum(1 for d in reviewed.values() if d.get("action") == "rewrite")
    spinner_text = (
        f"Applying {rewrite_count} rewrite(s) and assembling report..."
        if rewrite_count else "Assembling report..."
    )

    # Build pipeline context so run_frm_finalize can pass language_standard + ai_review_enabled
    finalize_context = {
        "case_id": intake.case_id,
        "language_standard": session.get("default_language_standard", "acfe"),
        "ai_review_enabled": True,
    }

    with st.spinner(spinner_text):
        deliverable = run_frm_finalize(
            intake,
            finalized,
            result["citations"],
            result["completed_modules"],
            result["exec_summary"],
            context=finalize_context,
        )

    # FRM-specific: executive summary expander shown above the standard done zone
    if deliverable.executive_summary:
        with st.expander("Executive Summary", expanded=True):
            st.markdown(deliverable.executive_summary)

    # P9-08e: AI review badges — one per risk item showing support level
    _render_ai_review_badges(st, intake.case_id, finalized)

    from tools.file_tools import case_dir, get_final_report_path
    from streamlit_app.shared.done_zone import render_done_zone

    # FE-03: build xlsx risk register if not already written
    _cdir = case_dir(intake.case_id)
    _final_dir = _cdir / "F_Final"
    _xlsx_path = _final_dir / f"frm_risk_register_{intake.case_id}.xlsx"
    if not _xlsx_path.exists():
        try:
            from tools.frm_excel_builder import FRMExcelBuilder
            _final_dir.mkdir(parents=True, exist_ok=True)
            FRMExcelBuilder().build(finalized, _xlsx_path)
        except Exception:
            pass

    if _xlsx_path.exists():
        st.download_button(
            label="Download Risk Register (.xlsx)",
            data=_xlsx_path.read_bytes(),
            file_name=_xlsx_path.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"frm_xlsx_dl_{intake.case_id}",
        )

    render_done_zone(
        st,
        case_id=intake.case_id,
        client_name=intake.client_name,
        report_path=get_final_report_path(intake.case_id),
        workflow_label="FRM Risk Register",
        session_state_keys=["frm_stage", "frm_intake", "frm_modules", "frm_result", "frm_reviewed", "frm_dm", "frm_reg_results"],
        stage_key="frm_stage",
        enable_workpaper=True,
    )

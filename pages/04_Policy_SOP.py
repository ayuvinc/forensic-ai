"""Policy / SOP Co-Build — Streamlit page (Sprint-IA-04, BA-IA-09).

Stage machine: intake → ai_questions → [custom_scoping] → structure_proposal
               → section_loop → done

The page is driven entirely by st.session_state; the orchestrator functions in
workflows/policy_sop_cobuild.py are pure (no Streamlit dependencies).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from schemas.case import CaseIntake
from schemas.policy_sop_cobuild import CoBuildSection, CoBuildState
from streamlit_app.shared.hybrid_intake import (
    HybridIntakeEngine,
    POLICY_SUBTYPE_LABELS,
    _POLICY_SOP_FIELD_CONFIG,
)
from streamlit_app.shared.intake import get_project_language_standard, render_engagement_banner
from streamlit_app.shared.session import bootstrap
from tools.file_tools import (
    append_audit_event,
    case_dir,
    get_final_report_path,
    is_af_project,
    write_artifact,
)

# Label → pipeline key map
_POLICY_SUBTYPE_KEYS = {
    "AML / CFT Policy":                    "aml_cft_policy",
    "Fraud Prevention Policy":             "fraud_prevention_policy",
    "Whistleblower Policy":                "whistleblower_policy",
    "Procurement Policy":                  "procurement_policy",
    "Conflict of Interest Policy":         "conflict_of_interest_policy",
    "Data Privacy Policy":                 "data_privacy_policy",
    "Transaction Monitoring SOP":          "transaction_monitoring_sop",
    "KYC / Due Diligence SOP":             "kyc_due_diligence_sop",
    "Fraud Investigation SOP":             "fraud_investigation_sop",
    "Sanctions Screening SOP":             "sanctions_screening_sop",
    "Suspicious Activity Reporting SOP":   "suspicious_activity_reporting_sop",
}

# Custom scoping questions (BA-IA-09)
_CUSTOM_SCOPE_QUESTIONS = [
    ("doc_name",      "What is the full name of this document?"),
    ("applies_to",    "Who does it apply to? (entity types, roles, geographies)"),
    ("frameworks",    "Which regulations, standards, or frameworks should it reference?"),
    ("existing_doc",  "Does an existing version already exist? (Yes / No + notes)"),
    ("primary_risk",  "What is the primary risk or gap this document addresses?"),
]

# ── helpers (defined at module level — must be before the stage machine) ───────

def _cobuild_progress_path(case_id: str) -> Path:
    cdir = case_dir(case_id)
    if is_af_project(case_id):
        return cdir / "E_Drafts" / "cobuild_progress.json"
    return cdir / "cobuild_progress.json"


def _save_progress(case_id: str, state: CoBuildState) -> None:
    """Atomically write cobuild_progress.json for resume-after-refresh support."""
    target = _cobuild_progress_path(case_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, target)


def _intake_from_snapshot(snap: dict) -> CaseIntake:
    return CaseIntake(**snap)


def _record_section_event(case_id: str, section: CoBuildSection, event_type: str) -> None:
    """Append a per-section audit event to audit_log.jsonl."""
    append_audit_event(case_id, {
        "event": event_type,
        "section_title": section.section_title,
        "action": section.status,
        "agent": "consultant",
    })


def _try_gap_analysis(
    intake: CaseIntake,
    params: dict,
    sections: list[str],
    co_build: CoBuildState,
) -> None:
    """Pre-populate sections from an uploaded existing document. Modifies co_build in place.

    Best-effort — any failure falls through silently so the user gets blank drafts.
    """
    try:
        from tools.document_manager import DocumentManager
        from workflows.policy_sop_cobuild import identify_gaps

        dm = DocumentManager(intake.case_id)
        if not dm.has_documents():
            return
        index = dm.get_index()
        doc_texts = "\n\n".join(
            dm._read_full(doc.doc_id)
            for doc in index.documents
            if not doc.is_duplicate
        )
        if not doc_texts.strip():
            return
        with st.spinner("Analysing existing document for gaps..."):
            gap_map = identify_gaps(intake, params, doc_texts, sections)
        for section in co_build.sections:
            existing = gap_map.get(section.section_title)
            if existing:
                section.body = existing
                section.status = "approved"
                section.action_note = "Pre-filled from uploaded document — verify before finalising."
    except Exception:
        pass


def _reset_all_state(engine: HybridIntakeEngine) -> None:
    """Clear all ps_* session state keys and reset the intake engine."""
    for k in list(st.session_state.keys()):
        if k.startswith("ps_"):
            st.session_state.pop(k, None)
    engine.reset()


# ── bootstrap ─────────────────────────────────────────────────────────────────

try:
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    st.error(f"Page failed to load: {_bootstrap_err}")
    st.stop()

st.title("Policy / SOP Co-Build")
st.caption(
    "Build AML/CFT policies, SOPs, and governance documents section by section "
    "with AI-assisted drafting and regulatory citations."
)

_ps_engine = HybridIntakeEngine(st, _POLICY_SOP_FIELD_CONFIG, "policy_sop")

# ── session state defaults ────────────────────────────────────────────────────

if "ps_stage" not in st.session_state:
    st.session_state.ps_stage = "intake"
if "ps_custom_q_idx" not in st.session_state:
    st.session_state.ps_custom_q_idx = 0
if "ps_custom_answers" not in st.session_state:
    st.session_state.ps_custom_answers = {}
if "ps_show_regen" not in st.session_state:
    st.session_state.ps_show_regen = False

# ── resume check: reload saved progress after page refresh ────────────────────

_engagement_id = st.session_state.get("active_project", "")
if _engagement_id and st.session_state.ps_stage == "intake":
    _prog_path = _cobuild_progress_path(_engagement_id)
    if _prog_path.exists():
        try:
            _saved = CoBuildState.model_validate_json(_prog_path.read_text())
            if _saved.structure_confirmed and _saved.intake_snapshot:
                st.info(
                    "A co-build session was previously started for this engagement. "
                    "Resume where you left off?"
                )
                _c1, _c2 = st.columns(2)
                if _c1.button("Resume co-build", type="primary"):
                    st.session_state.ps_co_build = _saved.model_dump()
                    st.session_state.ps_intake = _intake_from_snapshot(_saved.intake_snapshot)
                    st.session_state.ps_params = {
                        "doc_type":    _saved.doc_type,
                        "doc_subtype": _saved.doc_subtype,
                        "gap_analysis": _saved.gap_analysis,
                    }
                    st.session_state.ps_stage = "section_loop"
                    st.rerun()
                if _c2.button("Start new document"):
                    _prog_path.unlink(missing_ok=True)
                    st.rerun()
                st.stop()
        except Exception:
            pass  # Corrupt progress file — ignore and show intake form

# ── sidebar reset ─────────────────────────────────────────────────────────────

if st.session_state.ps_stage != "intake":
    if st.sidebar.button("Start New Document"):
        _reset_all_state(_ps_engine)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE: intake
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.ps_stage == "intake":
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    client_name = project_meta.get("client_name", "") if project_meta else ""
    if not client_name:
        client_name = st.text_input("Client name *", key="ps_client_name_manual")

    st.divider()
    engine_result = _ps_engine.run()

    if engine_result is not None and client_name.strip():
        import uuid as _uuid

        values = engine_result["values"]
        case_id = engagement_id if engagement_id else (
            f"{datetime.now().strftime('%Y%m%d')}-{_uuid.uuid4().hex[:6].upper()}"
        )

        doc_subtype_label = values.get("doc_subtype", "AML / CFT Policy")
        doc_type = "policy" if doc_subtype_label in POLICY_SUBTYPE_LABELS else "sop"
        doc_subtype = _POLICY_SUBTYPE_KEYS.get(doc_subtype_label, "aml_cft_policy")
        gap_analysis = "new" if values.get("gap_analysis", "New document") == "New document" else "gap"

        intake = CaseIntake(
            case_id=case_id,
            client_name=client_name.strip(),
            industry=values.get("industry", "").strip(),
            primary_jurisdiction=values.get("jurisdiction", "UAE"),
            description=values.get("description", "").strip(),
            workflow="policy_sop",
            language=get_project_language_standard(st),
            created_at=datetime.now(timezone.utc),
            engagement_id=engagement_id or None,
        )
        st.session_state.ps_intake = intake
        st.session_state.ps_params = {
            "doc_type":    doc_type,
            "doc_subtype": doc_subtype,
            "gap_analysis": gap_analysis,
        }
        st.session_state.ps_stage = "ai_questions"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE: ai_questions
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.ps_stage == "ai_questions":
    intake = st.session_state.ps_intake
    from streamlit_app.shared.aic import render_intake_questions
    intake_summary = f"Client: {intake.client_name}. {intake.description}"
    if render_intake_questions(st, intake.case_id, intake_summary):
        aic_log_key = f"aic_qa_{intake.case_id}"
        aic_pairs = st.session_state.get(aic_log_key, [])
        aic_context = "\n".join(
            f"Q: {p['q']}\nA: {p['a']}" for p in aic_pairs if isinstance(p, dict)
        )
        st.session_state.ps_aic_context = aic_context
        next_stage = (
            "custom_scoping"
            if st.session_state.ps_params.get("doc_subtype") == "custom"
            else "structure_proposal"
        )
        st.session_state.ps_stage = next_stage
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE: custom_scoping  (custom doc type only — BA-IA-09)
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.ps_stage == "custom_scoping":
    intake = st.session_state.ps_intake
    q_idx = st.session_state.ps_custom_q_idx
    total_q = len(_CUSTOM_SCOPE_QUESTIONS)

    st.subheader("Custom Document Scoping")
    st.caption(f"Question {q_idx + 1} of {total_q}")
    st.progress(q_idx / total_q)

    field_key, question_text = _CUSTOM_SCOPE_QUESTIONS[q_idx]

    with st.form(f"custom_scope_q_{q_idx}"):
        answer = st.text_area(question_text, height=80)
        submitted = st.form_submit_button("Next →")

    if submitted:
        if not answer.strip():
            st.warning("Please provide an answer before continuing.")
        else:
            st.session_state.ps_custom_answers[field_key] = answer.strip()
            if q_idx + 1 >= total_q:
                write_artifact(
                    intake.case_id,
                    "custom_scope",
                    "scoping",
                    st.session_state.ps_custom_answers,
                )
                st.session_state.ps_stage = "structure_proposal"
                st.session_state.ps_custom_q_idx = 0
            else:
                st.session_state.ps_custom_q_idx = q_idx + 1
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE: structure_proposal
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.ps_stage == "structure_proposal":
    intake = st.session_state.ps_intake
    params = st.session_state.ps_params

    st.subheader("Proposed Document Structure")
    st.caption(
        "Review and edit the section list. Reorder, add, or remove sections. "
        "Once confirmed, the AI drafts each section for your review."
    )

    if "ps_proposed_sections" not in st.session_state:
        with st.spinner("Proposing document structure..."):
            from workflows.policy_sop_cobuild import propose_structure
            try:
                titles = propose_structure(
                    intake,
                    params,
                    aic_context=st.session_state.get("ps_aic_context", ""),
                    custom_scope=st.session_state.get("ps_custom_answers") or None,
                )
            except Exception as e:
                st.error(f"Could not generate structure: {e}")
                st.stop()
        st.session_state.ps_proposed_sections = titles
        st.rerun()

    sections: list[str] = st.session_state.ps_proposed_sections
    sections_to_remove: list[int] = []

    st.markdown("**Sections:**")
    for i, title in enumerate(sections):
        col_up, col_dn, col_title, col_rm = st.columns([0.06, 0.06, 0.76, 0.12])
        with col_up:
            if st.button("↑", key=f"up_{i}", disabled=(i == 0)):
                sections[i - 1], sections[i] = sections[i], sections[i - 1]
                st.session_state.ps_proposed_sections = sections
                st.rerun()
        with col_dn:
            if st.button("↓", key=f"dn_{i}", disabled=(i == len(sections) - 1)):
                sections[i], sections[i + 1] = sections[i + 1], sections[i]
                st.session_state.ps_proposed_sections = sections
                st.rerun()
        with col_title:
            st.write(f"{i + 1}. {title}")
        with col_rm:
            if st.button("✕", key=f"rm_{i}"):
                sections_to_remove.append(i)

    if sections_to_remove:
        st.session_state.ps_proposed_sections = [
            t for j, t in enumerate(sections) if j not in sections_to_remove
        ]
        st.rerun()

    st.divider()

    new_title = st.text_input(
        "Add a section:",
        placeholder="e.g. Disciplinary Consequences",
        key="ps_add_section_input",
    )
    if st.button("+ Add Section") and new_title.strip():
        st.session_state.ps_proposed_sections = sections + [new_title.strip()]
        st.rerun()

    st.divider()

    if len(sections) < 2:
        st.warning("Please include at least 2 sections before confirming.")
    elif st.button("Confirm Section Structure →", type="primary"):
        co_build = CoBuildState(
            sections=[CoBuildSection(section_title=t) for t in sections],
            current_idx=0,
            doc_type=params["doc_type"],
            doc_subtype=params["doc_subtype"],
            gap_analysis=params["gap_analysis"],
            custom_scope=st.session_state.get("ps_custom_answers") or None,
            structure_confirmed=True,
            aic_context=st.session_state.get("ps_aic_context", ""),
            intake_snapshot=intake.model_dump(mode="json"),
        )
        if params["gap_analysis"] == "gap":
            _try_gap_analysis(intake, params, sections, co_build)
        st.session_state.ps_co_build = co_build.model_dump()
        _save_progress(intake.case_id, co_build)
        st.session_state.ps_stage = "section_loop"
        st.session_state.pop("ps_proposed_sections", None)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE: section_loop
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.ps_stage == "section_loop":
    intake = st.session_state.ps_intake
    co_build = CoBuildState.model_validate(st.session_state.ps_co_build)

    total = len(co_build.sections)
    idx = co_build.current_idx

    if idx >= total:
        st.session_state.ps_stage = "done"
        st.rerun()
    else:
        section = co_build.sections[idx]

        done_count = sum(1 for s in co_build.sections if s.status != "pending")
        st.progress(done_count / total)
        st.caption(f"Section {idx + 1} of {total}")
        st.subheader(section.section_title)

        # Draft on first visit if body is empty
        if not section.body and section.status == "pending":
            with st.spinner(f"Drafting section: {section.section_title}..."):
                from workflows.policy_sop_cobuild import draft_section
                try:
                    prior_bodies = [s.body for s in co_build.sections[:idx] if s.body]
                    section.body = draft_section(
                        section_title=section.section_title,
                        sections_list=[s.section_title for s in co_build.sections],
                        prior_approved_bodies=prior_bodies,
                        doc_type=co_build.doc_type,
                        doc_subtype=co_build.doc_subtype,
                        intake=intake,
                    )
                    co_build.sections[idx] = section
                    st.session_state.ps_co_build = co_build.model_dump()
                except Exception as e:
                    st.error(f"Could not draft section: {e}")
                    st.stop()
            st.rerun()

        if section.action_note:
            st.caption(f"ℹ {section.action_note}")

        edited_body = st.text_area(
            "Section content",
            value=section.body,
            height=320,
            key=f"section_body_{idx}",
            label_visibility="collapsed",
        )

        col_approve, col_edit, col_regen = st.columns(3)

        with col_approve:
            if st.button("✓ Approve", type="primary", use_container_width=True):
                section.body = edited_body
                section.status = "approved"
                _record_section_event(intake.case_id, section, "section_approved")
                co_build.sections[idx] = section
                co_build.current_idx = idx + 1
                st.session_state.ps_co_build = co_build.model_dump()
                _save_progress(intake.case_id, co_build)
                st.session_state.ps_show_regen = False
                st.rerun()

        with col_edit:
            if st.button("✎ Edit & Save", use_container_width=True):
                section.body = edited_body
                section.status = "edited"
                _record_section_event(intake.case_id, section, "section_edited")
                co_build.sections[idx] = section
                co_build.current_idx = idx + 1
                st.session_state.ps_co_build = co_build.model_dump()
                _save_progress(intake.case_id, co_build)
                st.session_state.ps_show_regen = False
                st.rerun()

        with col_regen:
            if st.button("↺ Regenerate", use_container_width=True):
                st.session_state.ps_show_regen = not st.session_state.ps_show_regen
                st.rerun()

        if st.session_state.ps_show_regen:
            st.divider()
            regen_instructions = st.text_area(
                "Revision instructions (max 500 characters):",
                max_chars=500,
                height=80,
                key=f"regen_instructions_{idx}",
            )
            if st.button("Submit revision request", type="primary"):
                if not regen_instructions.strip():
                    st.warning("Please describe what to change before submitting.")
                else:
                    with st.spinner("Revising section..."):
                        from workflows.policy_sop_cobuild import revise_section
                        try:
                            new_body = revise_section(
                                section_title=section.section_title,
                                current_body=section.body,
                                instructions=regen_instructions,
                                doc_type=co_build.doc_type,
                                doc_subtype=co_build.doc_subtype,
                                intake=intake,
                            )
                        except Exception as e:
                            st.error(f"Revision failed: {e}")
                            st.stop()
                    section.body = new_body
                    section.status = "regenerated"
                    _record_section_event(intake.case_id, section, "section_regenerated")
                    co_build.sections[idx] = section
                    co_build.current_idx = idx + 1
                    st.session_state.ps_co_build = co_build.model_dump()
                    _save_progress(intake.case_id, co_build)
                    st.session_state.ps_show_regen = False
                    st.rerun()

        approved_prev = [s for s in co_build.sections[:idx] if s.status != "pending"]
        if approved_prev:
            with st.expander(f"Approved sections ({len(approved_prev)})", expanded=False):
                for prev in approved_prev:
                    st.markdown(f"**{prev.section_title}**")
                    st.markdown(prev.body)
                    st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE: done
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.ps_stage == "done":
    intake = st.session_state.ps_intake
    co_build_data = st.session_state.get("ps_co_build")

    if co_build_data and not st.session_state.get("ps_assembled"):
        co_build = CoBuildState.model_validate(co_build_data)
        with st.spinner("Assembling final document..."):
            from workflows.policy_sop_cobuild import assemble_and_write
            try:
                st.session_state.ps_result = assemble_and_write(co_build, intake)
                st.session_state.ps_assembled = True
            except Exception as e:
                st.error(f"Assembly failed: {e}")
                if st.button("Retry"):
                    st.session_state.ps_assembled = False
                    st.rerun()
                st.stop()
        st.rerun()

    st.success(f"Document complete — Case ID: `{intake.case_id}`")

    report_path = get_final_report_path(intake.case_id)
    if report_path.exists():
        st.download_button(
            label="Download document (.md)",
            data=report_path.read_text(encoding="utf-8"),
            file_name=f"PolicySOP_{intake.client_name}_{intake.case_id}.md",
            mime="text/markdown",
        )
    else:
        st.warning("Report file not found. Check the pipeline log.")

    st.markdown(f"**Case ID:** `{intake.case_id}`")

    if co_build_data:
        co_build = CoBuildState.model_validate(co_build_data)
        action_counts = {"approved": 0, "edited": 0, "regenerated": 0}
        for s in co_build.sections:
            if s.status in action_counts:
                action_counts[s.status] += 1
        st.caption(
            f"{len(co_build.sections)} sections — "
            f"{action_counts['approved']} approved, "
            f"{action_counts['edited']} edited, "
            f"{action_counts['regenerated']} regenerated"
        )

    if st.button("Start Another Document", type="primary"):
        _reset_all_state(_ps_engine)
        st.rerun()

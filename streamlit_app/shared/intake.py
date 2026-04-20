"""Streamlit intake form helpers.

Each helper returns a validated Pydantic object (or tuple) or None if the
form has not been submitted yet. Pages call these before running any pipeline.

Also exports template_selector() — a collapsed expander rendered between
the intake form and the Run button so Maher can choose a report template
per engagement without navigating to Settings (TPL-04, UX-019).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import uuid


# ── Engagement context helper (P9-UI-02) ─────────────────────────────────────

def _load_active_project_meta(st) -> Optional[dict]:
    """Return index entry for the active engagement, or None if not set."""
    slug = st.session_state.get("active_project")
    if not slug:
        return None
    try:
        from config import CASES_DIR
        index_path = CASES_DIR / "index.json"
        if not index_path.exists():
            return None
        entries = json.loads(index_path.read_text(encoding="utf-8"))
        for e in entries:
            if e.get("case_id") == slug or e.get("engagement_id") == slug:
                return e
    except Exception:
        pass
    return None


def render_engagement_banner(st) -> Optional[dict]:
    """Show a "Continuing engagement" info banner if active_project is set.

    Returns the project metadata dict, or None if no active project.
    Call this at the TOP of any intake form that should respect active engagements.
    """
    meta = _load_active_project_meta(st)
    if meta:
        project_name = meta.get("project_name") or meta.get("case_id", "")
        client_name  = meta.get("client_name", "")
        st.info(
            f"**Continuing engagement:** {project_name}  \n"
            f"**Client:** {client_name}  \n"
            "Client name and language standard are pre-filled from this engagement."
        )
    return meta


# ── Label maps ─────────────────────────────────────────────────────────────────

_SUBMIT_LABELS: dict[str, str] = {
    "engagement_scoping":    "Begin Scoping",
    "investigation_report":  "Run Investigation",
    "persona_review":        "Run Persona Review",
    "policy_sop":            "Generate Policy / SOP",
    "training_material":     "Generate Training Material",
    "frm_risk_register":     "Run FRM Pipeline",
    "client_proposal":       "Draft Proposal",
    "proposal_deck":         "Build PPT Pack",
    "due_diligence":         "Run Due Diligence",
    "sanctions_screening":   "Run Sanctions Screening",
    "transaction_testing":   "Run Transaction Testing",
}

_DESCRIPTION_PLACEHOLDERS: dict[str, str] = {
    "engagement_scoping":    "Describe the client situation — what concerns prompted this engagement?",
    "investigation_report":  "Summarise the allegation or incident: who, what, when, suspected amounts",
    "persona_review":        "Paste the report or document to review",
    "policy_sop":            "Describe the policy area, regulatory context, and any existing framework",
    "training_material":     "Describe the training topic, target audience, and learning objectives",
    "frm_risk_register":     "Describe known concerns, existing controls, or scope limitations",
    "client_proposal":       "Describe the engagement scope, timeline, and client objectives",
    "proposal_deck":         "Describe the deck objective and key messages for the audience",
    "due_diligence":         "Describe the purpose of the DD and any known red flags",
    "sanctions_screening":   "Describe the screening context and any prior results",
    "transaction_testing":   "Describe the testing population, period, and objectives",
}


def generic_intake_form(st, workflow_id: str, title: str):
    """Multi-field intake form that returns a CaseIntake or None.

    Covers common fields shared across all workflows.
    Returns None until the user submits.
    submit_label is derived from workflow_id (e.g. "Run Investigation").

    P9-UI-02: when st.session_state.active_project is set, shows engagement
    banner, pre-fills client_name, and locks the field (read-only).
    """
    from schemas.case import CaseIntake

    st.subheader(title)

    # P9-UI-02: engagement context
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    prefill_client = project_meta.get("client_name", "") if project_meta else ""

    submit_label = _SUBMIT_LABELS.get(workflow_id, "Start")
    placeholder  = _DESCRIPTION_PLACEHOLDERS.get(workflow_id, "Describe the engagement scope")

    with st.form(key=f"intake_{workflow_id}"):
        # P9-UI-02: lock client_name when coming from an active engagement
        if project_meta:
            st.text_input(
                "Client name",
                value=prefill_client,
                disabled=True,
                key=f"client_locked_{workflow_id}",
            )
            client_name = prefill_client
        else:
            client_name = st.text_input("Client name")

        industry              = st.text_input("Industry / sector")
        primary_jurisdiction  = st.text_input("Primary jurisdiction", value="UAE")
        description           = st.text_area("Engagement description / scope", placeholder=placeholder)
        language              = st.selectbox("Report language", ["en", "ar"], index=0)
        submitted             = st.form_submit_button(submit_label)

    if not submitted:
        return None

    missing = [f for f, v in [
        ("Client name", client_name),
        ("Industry", industry),
        ("Engagement description", description),
    ] if not v.strip()]

    if missing:
        st.error(f"Required: {', '.join(missing)}")
        return None

    case_id = (
        f"{__import__('datetime').datetime.now().strftime('%Y%m%d')}"
        f"-{uuid.uuid4().hex[:6].upper()}"
    )

    return CaseIntake(
        case_id=case_id,
        client_name=client_name.strip(),
        industry=industry.strip(),
        primary_jurisdiction=primary_jurisdiction.strip(),
        description=description.strip(),
        workflow=workflow_id,
        language=language,
        created_at=datetime.now(timezone.utc),
        engagement_id=engagement_id or None,
    )


def frm_intake_form(st) -> Optional[tuple]:
    """FRM-specific intake form: company profile + reactive module multiselect.

    Module multiselect lives OUTSIDE the form so on_change fires immediately —
    Module 2 is auto-added when a dependent module (3, 4, 7) is selected, and
    an inline st.info() is shown WITHOUT clearing the form (UX-F-02).

    Returns (CaseIntake, selected_modules: list[int]) or None.
    """
    from schemas.case import CaseIntake
    from workflows.frm_risk_register import FRM_MODULES

    _DEPENDENT_ON_2 = {3, 4, 7}

    st.subheader("FRM Risk Register — Intake")

    # P9-UI-02: engagement context
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    prefill_client = project_meta.get("client_name", "") if project_meta else ""

    # ── Module selector (outside form for reactive on_change) ─────────────────
    module_options = {f"Module {k}: {v}": k for k, v in FRM_MODULES.items()}
    all_labels = list(module_options.keys())
    default_labels = [lbl for lbl, k in module_options.items() if k in (1, 2)]

    def _on_module_change():
        """Auto-add Module 2 when a dependent module is selected."""
        selected = st.session_state.get("frm_modules_selection", [])
        selected_nums = {module_options[lbl] for lbl in selected}
        if selected_nums & _DEPENDENT_ON_2:
            mod2_label = next(lbl for lbl, k in module_options.items() if k == 2)
            if mod2_label not in selected:
                st.session_state["frm_modules_selection"] = list(selected) + [mod2_label]
                st.session_state["frm_module2_auto_added"] = True

    st.markdown("**Modules to assess** (Modules 3, 4, and 7 require Module 2)")
    selected_labels = st.multiselect(
        "Select modules",
        options=all_labels,
        default=default_labels,
        key="frm_modules_selection",
        on_change=_on_module_change,
    )

    if st.session_state.pop("frm_module2_auto_added", False):
        st.info("Module 2 added automatically — required by the selected module(s).")

    # ── Remaining fields in a standard form ───────────────────────────────────
    with st.form(key="frm_intake_fields"):
        # P9-UI-02: lock client_name when coming from an active engagement
        if project_meta:
            st.text_input(
                "Client name",
                value=prefill_client,
                disabled=True,
                key="frm_client_locked",
            )
            client_name = prefill_client
        else:
            client_name = st.text_input("Client name")
        industry             = st.text_input("Industry / sector")
        primary_jurisdiction = st.text_input("Primary jurisdiction", value="UAE")
        employee_count       = st.text_input("Approximate employee count", value="")
        description          = st.text_area(
            "Engagement scope / known concerns",
            placeholder=_DESCRIPTION_PLACEHOLDERS["frm_risk_register"],
        )
        language  = st.selectbox("Report language", ["en", "ar"], index=0)
        submitted = st.form_submit_button("Run FRM Pipeline")

    if not submitted:
        return None

    selected_modules = sorted([module_options[lbl] for lbl in selected_labels])

    if not selected_modules:
        st.error("Select at least one module.")
        return None

    # Dependency enforcement after submit (belt-and-suspenders)
    selected_set = set(selected_modules)
    if selected_set & _DEPENDENT_ON_2 and 2 not in selected_set:
        st.warning("Module 2 is required by the selected module(s). Adding it automatically.")
        selected_modules = sorted(selected_set | {2})

    missing = [f for f, v in [("Client name", client_name), ("Industry", industry)] if not v.strip()]
    if missing:
        st.error(f"Required: {', '.join(missing)}")
        return None

    case_id = (
        f"{__import__('datetime').datetime.now().strftime('%Y%m%d')}"
        f"-{uuid.uuid4().hex[:6].upper()}"
    )

    scope = description.strip()
    if employee_count.strip():
        scope = f"Employees: ~{employee_count.strip()}. {scope}"

    intake = CaseIntake(
        case_id=case_id,
        client_name=client_name.strip(),
        industry=industry.strip(),
        primary_jurisdiction=primary_jurisdiction.strip(),
        description=scope,
        workflow="frm_risk_register",
        language=language,
        created_at=datetime.now(timezone.utc),
        engagement_id=engagement_id or None,
    )

    return intake, selected_modules


def dd_intake_form(st) -> Optional[tuple]:
    """Merged Due Diligence intake form — all fields in a single st.form.

    Eliminates the two-phase render (generic form → DD-specific fields)
    by combining all fields upfront (UX-F-02).

    Returns (CaseIntake, dd_params: dict) or None.
    """
    from schemas.case import CaseIntake

    st.subheader("Due Diligence — Intake")

    # P9-UI-02: engagement context
    project_meta = render_engagement_banner(st)
    engagement_id = st.session_state.get("active_project", "")
    prefill_client = project_meta.get("client_name", "") if project_meta else ""

    with st.form(key="dd_intake_form"):
        # Common fields
        if project_meta:
            st.text_input(
                "Client name",
                value=prefill_client,
                disabled=True,
                key="dd_client_locked",
            )
            client_name = prefill_client
        else:
            client_name = st.text_input("Client name")
        industry             = st.text_input("Industry / sector")
        primary_jurisdiction = st.text_input("Primary jurisdiction", value="UAE")

        st.divider()

        # DD-specific fields
        subject_type  = st.selectbox("Subject type", ["individual", "entity"], format_func=str.title)
        subject_name  = st.text_input(
            "Full legal name of subject",
            placeholder="Individual: full name as on passport  |  Entity: registered legal name",
        )
        jurisdictions_raw = st.text_input("Operating jurisdictions (comma-separated)", value="UAE")

        dd_purpose_options = [
            "onboarding", "investment", "partnership", "employment", "acquisition", "other"
        ]
        dd_purpose = st.selectbox(
            "Purpose of DD",
            dd_purpose_options,
            format_func=lambda v: v.replace("_", " ").title(),
        )
        screening_level = st.selectbox(
            "Screening level",
            ["standard_phase1", "enhanced_phase2"],
            format_func=lambda v: "Standard Phase 1" if v == "standard_phase1" else "Enhanced Phase 2",
        )
        specific_concerns = st.text_area(
            "Specific concerns or red flags (optional)",
            height=80,
            placeholder=_DESCRIPTION_PLACEHOLDERS["due_diligence"],
        )
        language  = st.selectbox("Report language", ["en", "ar"], index=0)
        submitted = st.form_submit_button("Run Due Diligence")

    if not submitted:
        return None

    missing = [f for f, v in [
        ("Client name", client_name),
        ("Industry", industry),
        ("Subject name", subject_name),
    ] if not v.strip()]
    if missing:
        st.error(f"Required: {', '.join(missing)}")
        return None

    case_id = (
        f"{__import__('datetime').datetime.now().strftime('%Y%m%d')}"
        f"-{uuid.uuid4().hex[:6].upper()}"
    )

    jurisdictions = [j.strip() for j in jurisdictions_raw.split(",") if j.strip()]

    intake = CaseIntake(
        case_id=case_id,
        client_name=client_name.strip(),
        industry=industry.strip(),
        primary_jurisdiction=primary_jurisdiction.strip(),
        description=f"DD subject: {subject_name.strip()}. {specific_concerns.strip()}".strip(),
        workflow="due_diligence",
        language=language,
        created_at=datetime.now(timezone.utc),
        engagement_id=engagement_id or None,
    )

    dd_params = {
        "subject_type":    subject_type,
        "subject_name":    subject_name.strip(),
        "jurisdictions":   jurisdictions,
        "dd_purpose":      dd_purpose,
        "screening_level": screening_level,
        "specific_concerns": specific_concerns.strip(),
        "screening_lists": ["all"],
        "deliverable_format": "full_report",
    }

    return intake, dd_params


# ── Template selector (TPL-04, UX-019) ────────────────────────────────────────

def template_selector(st, workflow_type: str) -> Optional[Path]:
    """Collapsed expander for per-engagement template selection.

    Renders between the intake form and Run button.
    Persists selection in st.session_state["report_template_path"] and
    st.session_state["report_template_bytes"].

    Returns the selected template Path, or None for plain Word output.
    The Run button on the calling page should be disabled while option (b)
    is selected but no file has been uploaded — checked via
    template_selector_ready(st) helper.
    """
    from tools.template_manager import TemplateManager

    tm = TemplateManager()
    registry = tm.list_templates()
    wf_entry = registry.get(workflow_type, {})
    custom_name = wf_entry.get("custom")

    # Resolve display name for saved custom template
    custom_label = f"Use saved template: {custom_name}" if custom_name else None

    options = []
    if custom_label:
        options.append(("saved", custom_label))
    options.append(("upload", "Upload for this engagement only"))
    options.append(("none",   "Plain Word output (no template)"))

    # Default selection: saved if available, else none
    default_idx = 0 if custom_label else (len(options) - 1)

    with st.expander("Report template", expanded=False):
        sel_key = f"tpl_sel_{workflow_type}"
        selected = st.radio(
            "Template source",
            options=[o[0] for o in options],
            format_func=lambda k: dict(options)[k],
            index=default_idx,
            key=sel_key,
            label_visibility="collapsed",
        )

        uploaded_bytes: Optional[bytes] = None
        if selected == "upload":
            up = st.file_uploader(
                "Upload .docx template",
                type=["docx"],
                key=f"tpl_file_{workflow_type}",
            )
            if up:
                uploaded_bytes = up.read()
                st.caption(f"Selected: `{up.name}` (one-time, this engagement only)")
            else:
                st.caption("No file uploaded — Run button will be disabled until a file is chosen or you select a different option.")

        if selected == "saved" and custom_name:
            st.caption(f"Template: `{custom_name}` (from Settings)")
        elif selected == "none":
            st.caption("Plain Word output — no branded template applied.")

    # Persist to session state so calling page can read the choice at run time
    if selected == "saved" and custom_name:
        try:
            resolved = tm.resolve(workflow_type)
            st.session_state["report_template_path"]  = resolved
            st.session_state["report_template_bytes"] = None
        except Exception:
            st.session_state["report_template_path"]  = None
            st.session_state["report_template_bytes"] = None
    elif selected == "upload":
        st.session_state["report_template_path"]  = None
        st.session_state["report_template_bytes"] = uploaded_bytes
    else:
        st.session_state["report_template_path"]  = None
        st.session_state["report_template_bytes"] = None

    return st.session_state.get("report_template_path")


def template_selector_ready(st, workflow_type: str) -> bool:
    """Return True unless 'upload' is selected but no file has been provided."""
    sel_key = f"tpl_sel_{workflow_type}"
    if st.session_state.get(sel_key) == "upload":
        return bool(st.session_state.get("report_template_bytes"))
    return True

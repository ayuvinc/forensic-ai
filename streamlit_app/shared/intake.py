"""Streamlit intake form helpers.

Each helper returns a validated Pydantic object (or tuple) or None if the
form has not been submitted yet. Pages call these before running any pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import uuid


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
    """
    from schemas.case import CaseIntake

    st.subheader(title)

    submit_label = _SUBMIT_LABELS.get(workflow_id, "Start")
    placeholder  = _DESCRIPTION_PLACEHOLDERS.get(workflow_id, "Describe the engagement scope")

    with st.form(key=f"intake_{workflow_id}"):
        client_name           = st.text_input("Client name")
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
        client_name          = st.text_input("Client name")
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

    with st.form(key="dd_intake_form"):
        # Common fields
        client_name          = st.text_input("Client name")
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

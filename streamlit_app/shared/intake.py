"""Streamlit intake form helpers.

Each helper returns a validated Pydantic object or None if the form has not
been submitted yet. Pages call these before running any pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import uuid


def generic_intake_form(st, workflow_id: str, title: str):
    """Multi-field intake form that returns a CaseIntake or None.

    Covers the common fields shared across all workflows.
    Returns None until the user submits.
    """
    from schemas.case import CaseIntake

    st.subheader(title)

    with st.form(key=f"intake_{workflow_id}"):
        client_name = st.text_input("Client name")
        industry = st.text_input("Industry / sector")
        primary_jurisdiction = st.text_input("Primary jurisdiction", value="UAE")
        description = st.text_area("Engagement description / scope")
        language = st.selectbox("Report language", ["en", "ar"], index=0)
        submitted = st.form_submit_button("Start")

    if not submitted:
        return None

    # Validate required fields
    missing = [f for f, v in [
        ("Client name", client_name),
        ("Industry", industry),
        ("Engagement description", description),
    ] if not v.strip()]

    if missing:
        st.error(f"Required: {', '.join(missing)}")
        return None

    case_id = f"{__import__('datetime').datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

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
    """FRM-specific intake form: company profile + module multiselect.

    Returns (CaseIntake, selected_modules: list[int]) or None.
    Validates module dependencies before returning — shows st.warning on violation.
    """
    from schemas.case import CaseIntake
    from workflows.frm_risk_register import FRM_MODULES, _validate_module_order

    st.subheader("FRM Risk Register — Intake")

    with st.form(key="frm_intake_form"):
        client_name = st.text_input("Client name")
        industry = st.text_input("Industry / sector")
        primary_jurisdiction = st.text_input("Primary jurisdiction", value="UAE")
        employee_count = st.text_input("Approximate employee count", value="")
        description = st.text_area("Engagement scope / known concerns")
        language = st.selectbox("Report language", ["en", "ar"], index=0)

        st.markdown("**Modules to assess** (Module 2 is required by 3, 4, and 7)")
        module_options = {f"Module {k}: {v}": k for k, v in FRM_MODULES.items()}
        selected_labels = st.multiselect(
            "Select modules",
            options=list(module_options.keys()),
            default=[f"Module {k}: {v}" for k, v in FRM_MODULES.items() if k in (1, 2)],
        )
        submitted = st.form_submit_button("Run Pipeline")

    if not submitted:
        return None

    selected_modules = sorted([module_options[lbl] for lbl in selected_labels])

    if not selected_modules:
        st.error("Select at least one module.")
        return None

    # Validate module dependencies — show warning, do not proceed
    try:
        _validate_module_order(selected_modules)
    except ValueError as e:
        st.warning(f"Module dependency error: {e}")
        return None

    missing = [f for f, v in [("Client name", client_name), ("Industry", industry)] if not v.strip()]
    if missing:
        st.error(f"Required: {', '.join(missing)}")
        return None

    case_id = f"{__import__('datetime').datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

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

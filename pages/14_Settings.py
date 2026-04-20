"""Settings — Streamlit page (TPL-03, UX-017, UX-018).

4-tab layout: Firm Profile | Pricing | Team & T&C | Report Templates.
Completeness indicator (5 chips) rendered above tabs.
"""
from __future__ import annotations

import json
import os
import time

import streamlit as st

from config import FIRM_PROFILE_DIR
from streamlit_app.shared.session import bootstrap
from tools.template_manager import TemplateManager

session = bootstrap(st)

_FIRM_JSON      = FIRM_PROFILE_DIR / "firm.json"
_CURRENCIES     = ["AED", "USD", "SAR", "EUR", "GBP"]
_PRICING_MODELS = ["T&M", "Lump Sum", "Retainer"]

_WORKFLOW_LABELS = {
    "investigation_report": "Investigation Report",
    "due_diligence":        "Due Diligence",
    "frm_risk_register":    "FRM Risk Register",
    "transaction_testing":  "Transaction Testing",
    "sanctions_screening":  "Sanctions Screening",
    "client_proposal":      "Client Proposal",
}


# ── I/O helpers ───────────────────────────────────────────────────────────────

def _load_profile() -> tuple[dict, bool]:
    if not _FIRM_JSON.exists():
        return {}, False
    try:
        return json.loads(_FIRM_JSON.read_text(encoding="utf-8")), False
    except json.JSONDecodeError:
        return {}, True


def _save_profile(data: dict, changed_keys: list[str] | None = None) -> str | None:
    # Read existing before overwriting so we can log old_value vs new_value (ACT-02)
    old_data, _ = _load_profile()
    try:
        FIRM_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _FIRM_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, _FIRM_JSON)
        # ACT-02: log settings change with before/after values for changed keys
        try:
            from tools.activity_logger import logger as _act_logger
            keys = changed_keys or list(data.keys())
            _act_logger.log(
                category="SETTINGS",
                action="settings_saved",
                actor="consultant",
                detail={
                    "changed_keys": keys,
                    "old_value": {k: old_data.get(k) for k in keys},
                    "new_value": {k: data.get(k) for k in keys},
                },
            )
        except Exception:
            pass
        return None
    except Exception as exc:
        return str(exc)


# ── Session state ─────────────────────────────────────────────────────────────
if "settings_error" not in st.session_state:
    st.session_state.settings_error = None
if "settings_saved" not in st.session_state:
    st.session_state.settings_saved = False

# ── Page header ───────────────────────────────────────────────────────────────
st.title("Settings")
st.caption("Firm profile, pricing, team credentials, and report templates.")

with st.spinner("Loading firm profile..."):
    profile, corrupt = _load_profile()

if corrupt:
    st.warning("Firm profile could not be loaded. Editing will overwrite the existing file.")
elif not _FIRM_JSON.exists():
    st.warning("Firm profile not yet set up. Fill in the fields below to create it.")

if st.session_state.settings_saved:
    placeholder = st.empty()
    placeholder.success("Settings saved.")
    time.sleep(2)
    placeholder.empty()
    st.session_state.settings_saved = False

# ── Completeness chips (5 items, above tabs — UX-017) ─────────────────────────
def _chip(label: str, ok: bool) -> str:
    return f"{'🟢' if ok else '⚪'} {label}"

_tm = TemplateManager()
_tpl_registry = _tm.list_templates()
_has_any_template = any(v.get("custom") or v.get("base") for v in _tpl_registry.values())

_completeness = [
    ("Firm Profile", bool(profile.get("firm_name", "").strip())),
    ("Pricing",      bool(profile.get("pricing_model"))),
    ("Team",         bool(profile.get("team_members"))),
    ("T&C",          bool(profile.get("terms_and_conditions", "").strip())),
    ("Templates",    _has_any_template),
]
filled = sum(1 for _, ok in _completeness if ok)
total  = len(_completeness)

badge_cols = st.columns(total + 1)
with badge_cols[0]:
    if filled == total:
        st.success(f"{filled}/{total} complete")
    elif filled >= 3:
        st.warning(f"{filled}/{total} complete")
    else:
        st.error(f"{filled}/{total} complete")
for i, (label, ok) in enumerate(_completeness):
    with badge_cols[i + 1]:
        st.markdown(_chip(label, ok))

st.divider()

# ── 4-tab layout (UX-018) ─────────────────────────────────────────────────────
tab_profile, tab_pricing, tab_team, tab_templates = st.tabs(
    ["Firm Profile", "Pricing", "Team & T&C", "Report Templates"]
)


# ── TAB 1: Firm Profile ───────────────────────────────────────────────────────
with tab_profile:
    firm_name = st.text_input(
        "Firm Name *",
        value=profile.get("firm_name", ""),
        placeholder="e.g. GoodWork Forensic Consulting",
    )
    logo_path = st.text_input(
        "Logo Path",
        value=profile.get("logo_path") or "",
        placeholder="assets/logo.png",
        help="Path to logo file relative to repo root.",
    )
    default_lang = st.selectbox(
        "Default Language Standard",
        options=["acfe", "expert_witness", "regulatory", "board_pack"],
        format_func=lambda k: {
            "acfe":           "ACFE Internal Review",
            "expert_witness": "Expert Witness",
            "regulatory":     "Regulatory Submission",
            "board_pack":     "Board Pack",
        }[k],
        index=["acfe", "expert_witness", "regulatory", "board_pack"].index(
            profile.get("default_language_standard", "acfe")
        ),
    )
    if st.button("Save Firm Profile", type="primary", disabled=not firm_name.strip(), key="save_profile"):
        data = {**profile}
        data["firm_name"] = firm_name.strip()
        data["logo_path"] = logo_path.strip() or None
        data["default_language_standard"] = default_lang
        err = _save_profile(data)
        if err:
            st.session_state.settings_error = err
        else:
            st.session_state.settings_saved = True
            st.rerun()


# ── TAB 2: Pricing ────────────────────────────────────────────────────────────
with tab_pricing:
    saved_currency = profile.get("currency", "AED")
    currency = st.selectbox(
        "Default Currency",
        _CURRENCIES,
        index=_CURRENCIES.index(saved_currency) if saved_currency in _CURRENCIES else 0,
    )
    saved_pricing = profile.get("pricing_model", "T&M")
    pricing_model = st.selectbox(
        "Pricing Model",
        _PRICING_MODELS,
        index=_PRICING_MODELS.index(saved_pricing) if saved_pricing in _PRICING_MODELS else 0,
    )
    day_rate = hour_rate = ""
    if pricing_model == "T&M":
        day_rate  = st.text_input("T&M Day Rate",  value=profile.get("day_rate", ""),  placeholder="5000")
        hour_rate = st.text_input("T&M Hour Rate", value=profile.get("hour_rate", ""), placeholder="750")

    if st.button("Save Pricing", type="primary", key="save_pricing"):
        data = {**profile}
        data["currency"]      = currency
        data["pricing_model"] = pricing_model
        if pricing_model == "T&M":
            data["day_rate"]  = day_rate.strip()
            data["hour_rate"] = hour_rate.strip()
        err = _save_profile(data)
        if err:
            st.session_state.settings_error = err
        else:
            st.session_state.settings_saved = True
            st.rerun()


# ── TAB 3: Team & T&C ────────────────────────────────────────────────────────
with tab_team:
    terms_and_conditions = st.text_area(
        "Standard Terms & Conditions",
        value=profile.get("terms_and_conditions", ""),
        height=300,
        placeholder="Paste your standard T&C text here — included in all proposals.",
        help="Injected into the T&C section of every client proposal.",
    )
    st.caption("Team member management coming in Sprint-SETUP.")

    if st.button("Save T&C", type="primary", key="save_tc"):
        data = {**profile}
        data["terms_and_conditions"] = terms_and_conditions.strip()
        err = _save_profile(data)
        if err:
            st.session_state.settings_error = err
        else:
            st.session_state.settings_saved = True
            st.rerun()


# ── TAB 4: Report Templates ───────────────────────────────────────────────────
with tab_templates:
    from streamlit_app.shared.template_selector import render_template_selector

    st.caption("Select a template for each workflow. Uploaded templates are saved to firm_profile/templates/.")

    _SELECTOR_WORKFLOWS = [
        ("frm_risk_register",   "FRM Risk Register"),
        ("investigation_report","Investigation Report"),
        ("due_diligence",       "Due Diligence"),
        ("transaction_testing", "Transaction Testing"),
        ("sanctions_screening", "Sanctions Screening"),
        ("client_proposal",     "Client Proposal"),
    ]

    for wf_id, wf_label in _SELECTOR_WORKFLOWS:
        st.markdown(f"**{wf_label}**")
        render_template_selector(wf_id)
        st.divider()


# ── Error banner ──────────────────────────────────────────────────────────────
if st.session_state.settings_error:
    st.error(f"Save failed: {st.session_state.settings_error}")
    if st.button("Dismiss", key="dismiss_err"):
        st.session_state.settings_error = None

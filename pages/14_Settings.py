"""Settings — Streamlit page (UX-005).

Reads and writes firm_profile/firm.json.
session.py._load_firm_name() reads this exact file for the firm name shown in the
Streamlit sidebar header — saving here keeps the header in sync on next page load.

Does NOT touch firm_profile/firm_profile.json (CLI setup_wizard) or
firm_profile/pricing_model.json (CLI proposal flow) — those remain CLI-only.
"""

from __future__ import annotations

import json
import os
import time

import streamlit as st

from config import FIRM_PROFILE_DIR
from streamlit_app.shared.session import bootstrap

session = bootstrap(st)

_FIRM_JSON  = FIRM_PROFILE_DIR / "firm.json"
_CURRENCIES     = ["AED", "USD", "SAR"]
_PRICING_MODELS = ["T&M", "Lump Sum", "Retainer"]


def _load_profile() -> tuple[dict, bool]:
    """Read firm_profile/firm.json.

    Returns (data, corrupt).
    - data={}    when file is absent (normal first-run) or corrupt.
    - corrupt=True only when file exists but is invalid JSON.
    """
    if not _FIRM_JSON.exists():
        return {}, False
    try:
        return json.loads(_FIRM_JSON.read_text(encoding="utf-8")), False
    except json.JSONDecodeError:
        return {}, True


def _save_profile(data: dict) -> str | None:
    """Atomically write firm_profile/firm.json.

    Uses .tmp → os.replace() so a process kill mid-write leaves a .tmp file,
    never a corrupt firm.json.
    Returns None on success, error string on failure.
    """
    try:
        FIRM_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _FIRM_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, _FIRM_JSON)
        return None
    except Exception as exc:
        return str(exc)


# ── Session state ─────────────────────────────────────────────────────────────
# Tracks save outcome across Streamlit reruns triggered by button clicks.
if "settings_error" not in st.session_state:
    st.session_state.settings_error = None
if "settings_saved" not in st.session_state:
    st.session_state.settings_saved = False

# ── Page header ───────────────────────────────────────────────────────────────
st.title("Settings")
st.caption("Firm profile — used on all reports, proposals, and deliverables.")

# Load firm profile with spinner (UX-005 loading state)
with st.spinner("Loading firm profile..."):
    profile, corrupt = _load_profile()

# File-state banners — shown before the form so user knows what to expect
if corrupt:
    st.warning(
        "Firm profile could not be loaded. Editing will overwrite the existing file."
    )
elif not _FIRM_JSON.exists():
    st.warning("Firm profile not yet set up. Fill in the fields below to create it.")

# ── Success banner ────────────────────────────────────────────────────────────
# Rendered before the form so it appears at the top of the page (UX-005 success state).
# settings_saved is set to True after a successful save + st.rerun(), cleared here.
if st.session_state.settings_saved:
    placeholder = st.empty()
    placeholder.success("Firm profile saved.")
    time.sleep(3)
    placeholder.empty()
    st.session_state.settings_saved = False

# ── Profile completeness indicator (UX-F-07) ─────────────────────────────────
_completeness_items = [
    ("Firm Name",          bool(profile.get("firm_name", "").strip())),
    ("Logo",               bool(profile.get("logo_path"))),
    ("Currency",           bool(profile.get("currency"))),
    ("Pricing Model",      bool(profile.get("pricing_model"))),
    ("Terms & Conditions", bool(profile.get("terms_and_conditions", "").strip())),
]
filled = sum(1 for _, ok in _completeness_items if ok)
total  = len(_completeness_items)
pct    = filled / total

if pct == 1.0:
    st.success(f"Profile complete ({filled}/{total})")
elif pct >= 0.6:
    st.warning(f"Profile {filled}/{total} complete — fill in remaining fields for best results")
else:
    st.error(f"Profile {filled}/{total} complete — proposals may be incomplete")

with st.expander("Completeness checklist", expanded=False):
    for label, ok in _completeness_items:
        st.write(f"{'✓' if ok else '○'} {label}")

st.divider()

# ── Form fields ───────────────────────────────────────────────────────────────

firm_name = st.text_input(
    "Firm Name *",
    value=profile.get("firm_name", ""),
    placeholder="e.g. GoodWork Forensic Consulting",
)

logo_path = st.text_input(
    "Logo Path",
    value=profile.get("logo_path") or "",
    placeholder="assets/logo.png",
    help="Path to your logo file relative to the repo root (e.g. assets/logo.png).",
)

saved_currency = profile.get("currency", "AED")
currency = st.selectbox(
    "Default Currency",
    options=_CURRENCIES,
    index=_CURRENCIES.index(saved_currency) if saved_currency in _CURRENCIES else 0,
)

saved_pricing = profile.get("pricing_model", "T&M")
pricing_model = st.selectbox(
    "Pricing Model",
    options=_PRICING_MODELS,
    index=_PRICING_MODELS.index(saved_pricing) if saved_pricing in _PRICING_MODELS else 0,
)

# T&M rate fields — conditionally rendered; hidden for Lump Sum and Retainer (UX-005)
day_rate  = ""
hour_rate = ""
if pricing_model == "T&M":
    day_rate = st.text_input(
        "T&M Day Rate",
        value=profile.get("day_rate", ""),
        placeholder="e.g. 5000",
    )
    hour_rate = st.text_input(
        "T&M Hour Rate",
        value=profile.get("hour_rate", ""),
        placeholder="e.g. 750",
    )

terms_and_conditions = st.text_area(
    "Standard Terms & Conditions",
    value=profile.get("terms_and_conditions", ""),
    height=150,
    placeholder="Paste your standard T&C text here — included in all proposals.",
    help="Injected into the T&C section of every client proposal.",
)

st.divider()

# ── Save button — disabled when Firm Name is empty (UX-005) ──────────────────
if st.button("Save", type="primary", disabled=not firm_name.strip(), key="save_btn"):
    data: dict = {
        "firm_name":           firm_name.strip(),
        "logo_path":           logo_path.strip() or None,
        "currency":            currency,
        "pricing_model":       pricing_model,
        "terms_and_conditions": terms_and_conditions.strip(),
    }
    if pricing_model == "T&M":
        data["day_rate"]  = day_rate.strip()
        data["hour_rate"] = hour_rate.strip()

    err = _save_profile(data)

    if err:
        st.session_state.settings_error = err
    else:
        st.session_state.settings_error = None
        st.session_state.settings_saved = True
        # Reload page so form shows saved values and success banner fires (UX-005)
        st.rerun()

# ── Error banner — persists until user retries ────────────────────────────────
if st.session_state.settings_error:
    st.error(f"Save failed: {st.session_state.settings_error}")
    if st.button("Try Again", key="retry_save"):
        # Clear the error; the button click itself triggers a Streamlit rerun.
        # Widget values are preserved by Streamlit's internal state — user input is not lost.
        st.session_state.settings_error = None

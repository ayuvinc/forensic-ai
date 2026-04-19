"""00_Setup.py — First-run setup wizard (BA-SETUP-01).

5-step guided setup for Maher's first install.  Called automatically by
bootstrap() when check_readiness() returns ready=False.  Can also be opened
manually from the sidebar if Maher wants to update keys or profile.

Steps:
  1. API keys  (ANTHROPIC required, TAVILY optional)
  2. Firm profile  (name required)
  3. Team  (at least one member required)
  4. Pricing model  (required)
  5. Review + complete
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import streamlit as st

# Bootstrap injects CSS only — no readiness redirect on this page (would loop)
from streamlit_app.shared.session import _CSS  # CSS-only injection
st.markdown(_CSS, unsafe_allow_html=True)

_BASE = Path(__file__).parent.parent
_FIRM_PROFILE_DIR = _BASE / "firm_profile"
_ENV_PATH         = _BASE / ".env"

# ── Constants ─────────────────────────────────────────────────────────────────
_STEPS = ["API Keys", "Firm Profile", "Team", "Pricing", "Review & Complete"]
_PRICING_MODELS = ["T&M (Time & Materials)", "Lump Sum", "Retainer", "Hybrid"]
_CURRENCIES     = ["AED", "USD", "SAR", "GBP", "EUR"]

# ── Session state defaults ─────────────────────────────────────────────────────
if "setup_step" not in st.session_state:
    st.session_state.setup_step = 1
if "setup_error" not in st.session_state:
    st.session_state.setup_error = None
if "setup_test_result" not in st.session_state:
    st.session_state.setup_test_result = None  # None | "ok" | "fail:message"

# ── Page header ────────────────────────────────────────────────────────────────
st.title("GoodWork Setup")
st.caption("Complete all steps to unlock the app. This takes about 5 minutes.")

# ── Progress bar ───────────────────────────────────────────────────────────────
current_step = st.session_state.setup_step
step_labels  = " → ".join(
    f"**{s}**" if i + 1 == current_step else s
    for i, s in enumerate(_STEPS)
)
st.markdown(step_labels)
st.progress((current_step - 1) / len(_STEPS))
st.divider()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def _read_env() -> dict[str, str]:
    """Parse the current .env file into a dict."""
    result: dict[str, str] = {}
    if not _ENV_PATH.exists():
        return result
    for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def _write_env(values: dict[str, str]) -> None:
    """Write key=value pairs to .env, preserving unrelated existing keys."""
    existing = _read_env()
    existing.update(values)
    lines = [f"{k}={v}" for k, v in existing.items() if v]
    _atomic_write(_ENV_PATH, "\n".join(lines) + "\n")


def _test_anthropic_key(key: str) -> tuple[bool, str]:
    """Quick connectivity check — sends a minimal API request."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        # Cheapest possible call: 1-token completion
        client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1,
            messages=[{"role": "user", "content": "hi"}],
        )
        return True, "Connected successfully."
    except Exception as exc:
        return False, str(exc)


def _load_team() -> list[dict]:
    path = _FIRM_PROFILE_DIR / "team.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _load_json(filename: str) -> dict:
    path = _FIRM_PROFILE_DIR / filename
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — API Keys
# ═══════════════════════════════════════════════════════════════════════════════
if current_step == 1:
    st.subheader("Step 1 — API Keys")
    st.markdown(
        "The app needs an **Anthropic API key** to run the AI pipeline. "
        "A Tavily key is optional — the app works without it in knowledge-only mode."
    )

    existing_env = _read_env()

    anthropic_key = st.text_input(
        "Anthropic API Key *",
        value=existing_env.get("ANTHROPIC_API_KEY", ""),
        type="password",
        placeholder="sk-ant-...",
        help="Get yours at console.anthropic.com → API Keys.",
    )
    tavily_key = st.text_input(
        "Tavily API Key (optional)",
        value=existing_env.get("TAVILY_API_KEY", ""),
        type="password",
        placeholder="tvly-...",
        help="Optional — enables live web/regulatory research. app.tavily.com → free tier.",
    )

    # Test connection button
    col_test, col_next = st.columns([1, 3])
    with col_test:
        if st.button("Test Connection", key="test_key"):
            if not anthropic_key.strip():
                st.session_state.setup_test_result = "fail:Enter your Anthropic key first."
            else:
                with st.spinner("Testing..."):
                    ok, msg = _test_anthropic_key(anthropic_key.strip())
                st.session_state.setup_test_result = "ok" if ok else f"fail:{msg}"
            st.rerun()

    # Show test result
    if st.session_state.setup_test_result == "ok":
        st.success("API key is valid.")
    elif st.session_state.setup_test_result and st.session_state.setup_test_result.startswith("fail:"):
        st.error(st.session_state.setup_test_result[5:])

    with col_next:
        if st.button("Save & Continue →", key="step1_next", type="primary"):
            if not anthropic_key.strip():
                st.error("Anthropic API Key is required.")
            else:
                _write_env({
                    "ANTHROPIC_API_KEY": anthropic_key.strip(),
                    "TAVILY_API_KEY":    tavily_key.strip(),
                })
                st.session_state.setup_test_result = None
                st.session_state.setup_step = 2
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Firm Profile
# ═══════════════════════════════════════════════════════════════════════════════
elif current_step == 2:
    st.subheader("Step 2 — Firm Profile")
    st.markdown("This appears on every report cover page and deliverable.")

    existing = _load_json("firm.json")

    firm_name = st.text_input(
        "Firm Name *",
        value=existing.get("firm_name", ""),
        placeholder="e.g. GoodWork Forensic Consulting",
    )
    tagline = st.text_input(
        "Tagline (optional)",
        value=existing.get("tagline", ""),
        placeholder="e.g. Independent. Rigorous. Trusted.",
    )
    logo_path = st.text_input(
        "Logo file path (optional)",
        value=existing.get("logo_path", "") or "",
        placeholder="e.g. firm_profile/logo.png",
        help="Absolute or repo-relative path to a PNG/JPG logo.",
    )
    website = st.text_input(
        "Website (optional)",
        value=existing.get("website", "") or "",
        placeholder="e.g. www.thegoodwork.online",
    )

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("← Back", key="step2_back"):
            st.session_state.setup_step = 1
            st.rerun()
    with col_next:
        if st.button("Save & Continue →", key="step2_next", type="primary"):
            if not firm_name.strip():
                st.error("Firm Name is required.")
            else:
                profile = {
                    "firm_name":  firm_name.strip(),
                    "tagline":    tagline.strip() or None,
                    "logo_path":  logo_path.strip() or None,
                    "website":    website.strip() or None,
                }
                _atomic_write(
                    _FIRM_PROFILE_DIR / "firm.json",
                    json.dumps(profile, indent=2),
                )
                st.session_state.setup_step = 3
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Team Members
# ═══════════════════════════════════════════════════════════════════════════════
elif current_step == 3:
    st.subheader("Step 3 — Team Members")
    st.markdown(
        "Add at least one team member. "
        "These appear in proposals under Team & Credentials."
    )

    # Load current team into session state for live editing
    if "setup_team" not in st.session_state:
        st.session_state.setup_team = _load_team() or []

    team: list[dict] = st.session_state.setup_team

    # Render existing members
    for i, member in enumerate(team):
        with st.expander(f"{member.get('name', 'Member')} — {member.get('role', '')}", expanded=False):
            col_del = st.columns([4, 1])
            with col_del[1]:
                if st.button("Remove", key=f"remove_{i}"):
                    team.pop(i)
                    st.session_state.setup_team = team
                    st.rerun()

    st.divider()
    st.markdown("**Add a team member**")

    with st.form("add_member_form", clear_on_submit=True):
        m_name = st.text_input("Name *", placeholder="e.g. Maher Al-Farsi")
        m_role = st.text_input("Role / Title *", placeholder="e.g. Senior Forensic Consultant")
        m_bio  = st.text_area(
            "Short bio (1–3 sentences)",
            placeholder="Relevant qualifications and experience for proposals.",
            height=80,
        )
        submitted = st.form_submit_button("Add Member")
        if submitted:
            if not m_name.strip() or not m_role.strip():
                st.error("Name and Role are required.")
            else:
                team.append({"name": m_name.strip(), "role": m_role.strip(), "bio": m_bio.strip()})
                st.session_state.setup_team = team
                st.rerun()

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("← Back", key="step3_back"):
            st.session_state.setup_step = 2
            st.rerun()
    with col_next:
        if st.button("Save & Continue →", key="step3_next", type="primary"):
            if not team:
                st.error("At least one team member is required.")
            else:
                _atomic_write(
                    _FIRM_PROFILE_DIR / "team.json",
                    json.dumps(team, indent=2),
                )
                st.session_state.setup_step = 4
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Pricing Model
# ═══════════════════════════════════════════════════════════════════════════════
elif current_step == 4:
    st.subheader("Step 4 — Pricing Model")
    st.markdown(
        "Used in proposals. You can update this any time from **Settings**."
    )

    existing = _load_json("pricing_model.json")

    pricing_type = st.selectbox(
        "Default pricing model *",
        options=_PRICING_MODELS,
        index=_PRICING_MODELS.index(existing.get("model", "T&M (Time & Materials)"))
        if existing.get("model") in _PRICING_MODELS else 0,
    )
    currency = st.selectbox(
        "Default currency *",
        options=_CURRENCIES,
        index=_CURRENCIES.index(existing.get("currency", "AED"))
        if existing.get("currency") in _CURRENCIES else 0,
    )

    # T&M rate fields only when relevant
    show_rates = "T&M" in pricing_type
    daily_rate = None
    if show_rates:
        daily_rate = st.number_input(
            "Standard daily rate",
            min_value=0,
            value=int(existing.get("daily_rate", 0)),
            step=500,
            help="Leave 0 to set per-proposal.",
        )

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("← Back", key="step4_back"):
            st.session_state.setup_step = 3
            st.rerun()
    with col_next:
        if st.button("Save & Continue →", key="step4_next", type="primary"):
            pricing = {
                "model":      pricing_type,
                "currency":   currency,
                "daily_rate": daily_rate if show_rates else None,
            }
            _atomic_write(
                _FIRM_PROFILE_DIR / "pricing_model.json",
                json.dumps(pricing, indent=2),
            )
            st.session_state.setup_step = 5
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Review & Complete
# ═══════════════════════════════════════════════════════════════════════════════
elif current_step == 5:
    st.subheader("Step 5 — Review & Complete")

    from streamlit_app.shared.readiness import check_readiness
    result = check_readiness()

    if result.ready:
        st.success("All setup checks passed. You are ready to use GoodWork.")

        firm   = _load_json("firm.json")
        team   = _load_team()
        pricing = _load_json("pricing_model.json")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Firm**")
            st.write(firm.get("firm_name", "—"))
            if firm.get("website"):
                st.write(firm["website"])
        with col2:
            st.markdown("**Team members**")
            for m in team:
                st.write(f"• {m.get('name')} — {m.get('role')}")

        st.markdown("**Pricing**")
        st.write(
            f"{pricing.get('model')} · {pricing.get('currency')}"
            + (f" · {pricing.get('daily_rate'):,}/day" if pricing.get("daily_rate") else "")
        )

        col_back, col_launch = st.columns(2)
        with col_back:
            if st.button("← Edit", key="step5_back"):
                st.session_state.setup_step = 4
                st.rerun()
        with col_launch:
            if st.button("Launch GoodWork →", key="step5_complete", type="primary"):
                import config
                config.reload()
                # Clear setup-specific session state
                for key in ["setup_step", "setup_team", "setup_test_result", "setup_error"]:
                    st.session_state.pop(key, None)
                st.switch_page("app.py")
    else:
        st.error("Setup incomplete. The following items are still missing:")
        for item in result.missing:
            st.markdown(f"- {item}")
        if st.button("← Back to fix", key="step5_fix"):
            # Jump back to step 1 so all fields are accessible
            st.session_state.setup_step = 1
            st.rerun()

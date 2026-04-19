"""Streamlit session bootstrap.

Call bootstrap(st) at the top of every page before any other logic.
It is idempotent — safe to call on every page load without re-initialising
already-set state.
"""

from __future__ import annotations


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

* { font-family: 'Montserrat', 'Helvetica Neue', Arial, sans-serif !important; }

[data-testid="stSidebar"] { padding-top: 1rem; }

/* Button colors are now set via .streamlit/config.toml primaryColor — no CSS override needed */

.severity-critical { border-left: 4px solid #D50032; background: #FFF0F2; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 8px; }
.severity-warning  { border-left: 4px solid #B8860B; background: #FFFBEA; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 8px; }
.severity-info     { border-left: 4px solid #0088CB; background: #F0F8FF; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 8px; }

.case-id-chip {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 12px;
  background: #F5F2F0;
  border: 1px solid #D5D5D5;
  border-radius: 4px;
  padding: 2px 8px;
  color: #4F4F4E;
}

h2, h3 { color: #282827; font-weight: 600 !important; border-bottom: 2px solid #D50032; padding-bottom: 8px; }
</style>
"""


def bootstrap(st) -> dict:
    """Initialise registry, hook_engine, firm_name, and design system in st.session_state.

    Returns the session state dict for convenience.

    On every call (even after bootstrapped=True), checks app readiness and
    redirects to 00_Setup.py if any required artifact is missing.  The redirect
    is skipped when the current page IS 00_Setup.py (avoids an infinite loop).
    """
    # Readiness gate — runs on every page load, not just first boot
    _maybe_redirect_to_setup(st)

    if "bootstrapped" in st.session_state:
        return st.session_state

    # Inject design system CSS (Montserrat + brand tokens)
    st.markdown(_CSS, unsafe_allow_html=True)

    import config
    from core.hook_engine import HookEngine
    from core.tool_registry import ToolRegistry
    from hooks.pre_hooks import validate_input, normalize_language, sanitize_pii, attach_case_metadata
    from hooks.post_hooks import (
        validate_schema, persist_artifact, append_audit_event_hook as audit_hook,
        extract_citations, render_markdown,
    )

    hook_engine = HookEngine()
    hook_engine.register_pre("validate_input", validate_input)
    hook_engine.register_pre("normalize_language", normalize_language)
    hook_engine.register_pre("sanitize_pii", sanitize_pii)
    hook_engine.register_pre("attach_case_metadata", attach_case_metadata)
    hook_engine.register_post("validate_schema", validate_schema)
    hook_engine.register_post("persist_artifact", persist_artifact)
    hook_engine.register_post("append_audit_event", audit_hook)
    hook_engine.register_post("extract_citations", extract_citations)
    hook_engine.register_post("render_markdown", render_markdown)

    registry = ToolRegistry()

    # Firm name — from firm_profile if set up, else placeholder
    firm_name = getattr(config, "FIRM_NAME", None) or _load_firm_name()

    st.session_state.bootstrapped = True
    st.session_state.registry = registry
    st.session_state.hook_engine = hook_engine
    st.session_state.firm_name = firm_name
    st.session_state.research_mode = getattr(config, "RESEARCH_MODE", "knowledge_only")

    # Sidebar section guide — shown below auto-nav links
    _SIDEBAR_GUIDE = """
<div style="margin-top:1.5rem;padding-top:0.75rem;border-top:1px solid #E0DEDD;">
  <p style="font-size:10px;font-weight:700;color:#9B9B9A;letter-spacing:0.08em;margin:0 0 4px 0;">INVESTIGATION</p>
  <p style="font-size:10px;color:#9B9B9A;margin:0 0 10px 8px;line-height:1.5;">Scope · Investigation · Persona Review</p>
  <p style="font-size:10px;font-weight:700;color:#9B9B9A;letter-spacing:0.08em;margin:0 0 4px 0;">COMPLIANCE</p>
  <p style="font-size:10px;color:#9B9B9A;margin:0 0 10px 8px;line-height:1.5;">Policy SOP · Training · FRM</p>
  <p style="font-size:10px;font-weight:700;color:#9B9B9A;letter-spacing:0.08em;margin:0 0 4px 0;">BUSINESS</p>
  <p style="font-size:10px;color:#9B9B9A;margin:0 0 10px 8px;line-height:1.5;">Proposal · PPT Pack</p>
  <p style="font-size:10px;font-weight:700;color:#9B9B9A;letter-spacing:0.08em;margin:0 0 4px 0;">INTELLIGENCE</p>
  <p style="font-size:10px;color:#9B9B9A;margin:0 0 10px 8px;line-height:1.5;">Due Diligence · Sanctions · TT</p>
  <p style="font-size:10px;font-weight:700;color:#9B9B9A;letter-spacing:0.08em;margin:0 0 4px 0;">UTILITIES</p>
  <p style="font-size:10px;color:#9B9B9A;margin:0 0 10px 8px;line-height:1.5;">Case Tracker · Team · Settings</p>
</div>
"""
    st.sidebar.markdown(_SIDEBAR_GUIDE, unsafe_allow_html=True)

    # Sidebar footer — firm identity + today's date
    import datetime
    today = datetime.date.today().strftime("%d %b %Y")
    st.sidebar.caption(f"GoodWork Forensic AI · {today}")

    return st.session_state


def _load_firm_name() -> str:
    """Read firm name from firm_profile/firm.json if it exists."""
    import json
    from pathlib import Path

    profile_path = Path("firm_profile/firm.json")
    if profile_path.exists():
        try:
            return json.loads(profile_path.read_text())["firm_name"]
        except (KeyError, json.JSONDecodeError):
            pass
    return "GoodWork Forensic Consulting"


def _maybe_redirect_to_setup(st) -> None:
    """Redirect to 00_Setup.py if the app is not fully configured.

    Skipped on the setup page itself (avoids infinite redirect loop).
    Uses get_script_run_ctx to detect the current page path without importing
    Streamlit internals that may change across versions — falls back gracefully
    if the context is unavailable.
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx is not None:
            page_path = getattr(ctx, "page_script_hash", "") or ""
            # Also check the actual script path if available
            script_path = getattr(ctx, "script_path", "") or ""
            if "00_Setup" in script_path or "00_Setup" in page_path:
                return  # Already on setup page — do not redirect
    except Exception:
        pass  # If context unavailable, allow redirect check to proceed

    from streamlit_app.shared.readiness import check_readiness
    result = check_readiness()
    if not result.ready:
        st.switch_page("pages/00_Setup.py")

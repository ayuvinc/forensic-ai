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

.stButton > button[kind="primary"] {
  background-color: #D50032 !important;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.stButton > button[kind="primary"]:hover { background-color: #761E2F !important; }

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

h2 { color: #282827; font-weight: 600 !important; border-bottom: 2px solid #D50032; padding-bottom: 8px; }
</style>
"""


def bootstrap(st) -> dict:
    """Initialise registry, hook_engine, firm_name, and design system in st.session_state.

    Returns the session state dict for convenience.
    """
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

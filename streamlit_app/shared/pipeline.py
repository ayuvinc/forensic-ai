"""Pipeline runner for Streamlit pages.

run_in_status() wraps any workflow function in a st.status block with
severity-tagged live log entries and a progress bar.

Each PipelineEvent renders as:
  CRITICAL → branded left-border div (severity-critical CSS class)
  WARNING  → branded left-border div (severity-warning CSS class)
  INFO     → st.info()

Agent internal IDs are mapped to user-facing labels via _AGENT_LABELS.
Events are stored in st.session_state["pipeline_log_events"] so the
failure expander can display them if the pipeline errors.

Progress bar:
  total_steps defaults to 3 (Junior → PM → Partner).
  Each on_progress call increments the step counter by 1.
  Callers can pass total_steps=N for workflows with more steps (e.g. FRM).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any, Literal, Union


@dataclass
class PipelineEvent:
    """A severity-tagged pipeline log entry.

    severity must be one of CRITICAL / WARNING / INFO — validated at construction.
    Severity is an enum-like constant, never sourced from user input.
    """

    severity: Literal["CRITICAL", "WARNING", "INFO"]
    message: str
    agent: str

    _VALID_SEVERITIES = frozenset({"CRITICAL", "WARNING", "INFO"})

    def __post_init__(self) -> None:
        if self.severity not in self._VALID_SEVERITIES:
            raise ValueError(
                f"PipelineEvent severity must be CRITICAL, WARNING, or INFO — got '{self.severity}'"
            )


# Maps internal agent role keys to user-facing labels (UX-F-03 / UX-009)
_AGENT_LABELS: dict[str, str] = {
    "junior_analyst": "Consultant (Draft)",
    "junior":         "Consultant (Draft)",
    "pm_review":      "Consultant (Review)",
    "pm":             "Consultant (Review)",
    "partner":        "Consultant (Sign-off)",
    "frm_page":       "FRM",
    "pipeline":       "Pipeline",
}


def _map_agent_label(agent: str) -> str:
    """Return user-facing label for an internal agent identifier."""
    return _AGENT_LABELS.get(agent, agent)


def _render_event(st, event: PipelineEvent) -> None:
    """Render a PipelineEvent using branded severity CSS classes.

    CRITICAL and WARNING use left-border accent divs (defined in session._CSS).
    INFO uses a plain st.info() — no custom styling needed.
    The CSS classes are injected once by bootstrap() via session._CSS.
    Agent identifiers are mapped to user-facing labels before rendering.
    """
    import html as _html
    label_text = _map_agent_label(event.agent)
    label = f"[{label_text}] {_html.escape(event.message)}"
    if event.severity == "CRITICAL":
        st.markdown(
            f'<div class="severity-critical">{label}</div>',
            unsafe_allow_html=True,
        )
    elif event.severity == "WARNING":
        st.markdown(
            f'<div class="severity-warning">{label}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"[{_map_agent_label(event.agent)}] {event.message}")


def run_in_status(
    st,
    label: str,
    fn: Callable,
    *args,
    total_steps: int = 3,
    _engagement_id: str = "",
    _case_id: str = "",
    **kwargs,
) -> Any:
    """Call fn(*args, on_progress=<callback>, **kwargs) inside st.status.

    Adds a st.progress() bar above the status block that increments on each
    on_progress call and reaches 100% when the pipeline completes.

    The on_progress callback accepts PipelineEvent or plain str.
    Plain strings are auto-wrapped as PipelineEvent(severity='INFO', agent='pipeline').

    Events are stored in st.session_state["pipeline_log_events"] so that
    a failure expander can replay them after a pipeline error.

    Returns whatever fn returns, or raises on exception.
    """
    # Initialise log buffer in session state (persists across reruns for failure display)
    st.session_state["pipeline_log_events"] = []
    st.caption("Estimated time: 2–4 minutes depending on module count and research mode.")

    # ACT-02: log pipeline start
    try:
        from tools.activity_logger import logger as _act_logger
        _act_logger.log(
            category="PIPELINE",
            action="pipeline_start",
            actor="system",
            engagement_id=_engagement_id or st.session_state.get("active_project", ""),
            case_id=_case_id,
            detail={"label": label},
        )
    except Exception:
        pass

    # Progress bar — sits above the status block (UX-F-03)
    progress_bar = st.progress(0)
    step_count = [0]

    def _advance_progress() -> None:
        step_count[0] += 1
        pct = min(step_count[0] / max(total_steps, 1), 1.0)
        progress_bar.progress(pct)

    result = None

    with st.status(label, expanded=True) as status:

        def on_progress(event: Union[PipelineEvent, str]) -> None:
            if isinstance(event, str):
                event = PipelineEvent(severity="INFO", message=event, agent="pipeline")
            # Store event for failure log
            st.session_state["pipeline_log_events"].append(event)
            _render_event(st, event)
            _advance_progress()

        try:
            result = fn(*args, on_progress=on_progress, **kwargs)
            progress_bar.progress(1.0)
            status.update(label=f"{label} — complete", state="complete")
            # ACT-02: log pipeline complete
            try:
                from tools.activity_logger import logger as _act_logger
                _act_logger.log(
                    category="PIPELINE",
                    action="pipeline_complete",
                    actor="system",
                    engagement_id=_engagement_id or st.session_state.get("active_project", ""),
                    case_id=_case_id,
                    detail={"label": label, "steps": step_count[0]},
                )
            except Exception:
                pass
        except Exception as e:
            status.update(label=f"{label} — failed", state="error")
            from streamlit_app.shared.crash_reporter import write_crash_report
            _crash_path = write_crash_report("pipeline:" + label, e)
            st.error("Something went wrong during the pipeline run.")
            st.code(_crash_path, language=None)
            st.caption("Share this file with Claude to diagnose the issue.")
            with st.expander("Show error details"):
                st.text(type(e).__name__ + ": " + str(e))
            # ACT-02: log pipeline error
            try:
                from tools.activity_logger import logger as _act_logger
                _act_logger.log(
                    category="PIPELINE",
                    action="pipeline_error",
                    actor="system",
                    engagement_id=_engagement_id or st.session_state.get("active_project", ""),
                    case_id=_case_id,
                    detail={"label": label, "error": str(e)},
                    status="error",
                )
            except Exception:
                pass
            # Show failure log expander so Maher can inspect without opening terminal
            log_events = st.session_state.get("pipeline_log_events", [])
            if log_events:
                with st.expander("View pipeline log"):
                    for ev in log_events[-20:]:  # last 20 events
                        _render_event(st, ev)
            raise

    return result

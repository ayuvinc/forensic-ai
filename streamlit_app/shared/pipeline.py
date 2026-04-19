"""Pipeline runner for Streamlit pages.

run_in_status() wraps any workflow function in a st.status block with
severity-tagged live log entries. Each PipelineEvent renders as:
  CRITICAL → st.error()   (pipeline failure, empty results)
  WARNING  → st.warning() (degraded mode, data quality gaps)
  INFO     → st.info()    (normal agent progress)

Callers may pass plain strings to on_progress; they are auto-wrapped as INFO.
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


def _render_event(st, event: PipelineEvent) -> None:
    """Render a PipelineEvent using branded severity CSS classes.

    CRITICAL and WARNING use left-border accent divs (defined in session._CSS).
    INFO uses a plain st.info() — no custom styling needed.
    The CSS classes are injected once by bootstrap() via session._CSS.
    """
    import html as _html
    label = f"[{event.agent}] {_html.escape(event.message)}"
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
        st.info(f"[{event.agent}] {event.message}")


def run_in_status(st, label: str, fn: Callable, *args, **kwargs) -> Any:
    """Call fn(*args, on_progress=<callback>, **kwargs) inside st.status.

    The on_progress callback accepts PipelineEvent or plain str.
    Plain strings are auto-wrapped as PipelineEvent(severity='INFO', agent='pipeline').

    Each event renders immediately as st.error / st.warning / st.info inside the
    status block. Returns whatever fn returns, or raises on exception.
    """
    result = None

    with st.status(label, expanded=True) as status:

        def on_progress(event: Union[PipelineEvent, str]) -> None:
            # Auto-wrap plain strings from legacy pipeline callers
            if isinstance(event, str):
                event = PipelineEvent(severity="INFO", message=event, agent="pipeline")
            _render_event(st, event)

        try:
            result = fn(*args, on_progress=on_progress, **kwargs)
            status.update(label=f"{label} — complete", state="complete")
        except Exception as e:
            status.update(label=f"{label} — failed", state="error")
            st.error(f"Pipeline error: {e}")
            raise

    return result

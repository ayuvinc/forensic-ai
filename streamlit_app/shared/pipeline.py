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

import random
from dataclasses import dataclass
from typing import Callable, Any, Literal, Union

# Rotating forensic insights shown while the pipeline runs — no API needed.
_FORENSIC_TIPS: list[str] = [
    "**Benford's Law:** In naturally occurring datasets ~30% of leading digits are 1. Significant deviations often reveal fabricated figures in expense or revenue records.",
    "**Round-number bias:** Genuine transactions cluster at exact round amounts less than 5% of the time. Fabricated ones cluster at 40–60% — a primary red flag in expense fraud testing.",
    "**Just-below-threshold pattern:** Transactions consistently landing just under approval or reporting limits are a core indicator in procurement and expense fraud.",
    "**Fraud triangle:** Pressure, opportunity, and rationalisation predict over 85% of internal fraud cases. Controls that remove opportunity are the most cost-effective intervention.",
    "**ACFE benchmark:** Organisations lose an estimated 5% of revenue to fraud annually. The median case loss is $117,000 — and the median duration before detection is 12 months.",
    "**Ghost employee detection:** Duplicate NIC/TIN numbers, salary paid to dormant accounts, and addresses matching active employees are primary indicators in payroll fraud.",
    "**AML layering:** The layering phase — structuring deposits, wire transfers, and shell company interposition — is the most technically complex step in money laundering.",
    "**Vendor master review:** Duplicate bank accounts, P.O. Box-only addresses, and vendor addresses matching employee addresses are highest-yield fraud detection procedures.",
    "**Digital metadata:** File creation timestamps, access logs, and email headers are often more evidential than content — they can directly contradict a stated timeline.",
    "**Chain of custody:** Forensic evidence handling requires every transfer to be logged with time, handler, and purpose. Gaps in custody can render evidence inadmissible.",
    "**UAE AML law:** Federal Law No. 20 of 2018 requires goAML reporting within 30 days of a suspicious transaction. Delayed reporting is itself a compliance risk.",
    "**Cognitive load technique:** Asking subjects to recall events in reverse chronological order significantly increases cognitive load for fabricated accounts — a validated interview method.",
    "**IFRS 15 risk:** Revenue recognition is a common earnings manipulation target. Channel stuffing, bill-and-hold arrangements, and side letters are primary schemes.",
    "**Sanctions fuzzy matching:** Name-matching algorithms must handle aliases, transliterations, and date-of-birth variations. Tuning thresholds affects both false positives and misses.",
    "**FATF 40 Recommendations:** These form the international AML standard. Jurisdictions are assessed via Mutual Evaluation Reports — published findings can directly affect client risk ratings.",
    "**Asset tracing:** Cross-border recovery relies on MLATs (Mutual Legal Assistance Treaties). International information requests average 6–18 months — plan litigation timelines accordingly.",
    "**Shell company indicators:** Nominee directors, bearer shares, and registered-agent-only addresses are common concealment structures in asset misappropriation cases.",
    "**Expert witness standard:** The forensic accountant's duty is to the court, not the client. Independence is a prerequisite for any finding relied upon in legal proceedings.",
    "**Early detection impact:** Cases detected within the first 6 months have median losses 60% lower than cases running over 24 months. Control monitoring frequency directly affects outcome.",
    "**COSO control framework:** Segregation of duties, physical access controls, and independent reconciliations are the three most cost-effective preventive controls for small-entity fraud risk.",
]


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

    # Show a random forensic insight while the pipeline runs — no API needed
    tip = random.choice(_FORENSIC_TIPS)
    st.info(f"While you wait — **Forensic insight:** {tip}")

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

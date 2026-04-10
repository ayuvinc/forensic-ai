"""Pipeline runner for Streamlit pages.

run_in_status() wraps any workflow function in a st.status block with a live
scrolling log. Progress updates appear in the browser immediately as the
pipeline runs — no threading or polling required (Streamlit pushes via WebSocket).
"""

from __future__ import annotations

from typing import Callable, Any


def run_in_status(st, label: str, fn: Callable, *args, **kwargs) -> Any:
    """Call fn(*args, on_progress=<callback>, **kwargs) inside st.status.

    The on_progress callback appends to a rolling log displayed in st.empty().
    Caller should NOT pass on_progress in kwargs — it is injected here.

    Returns whatever fn returns, or raises on exception (displayed as st.error).
    """
    result = None
    log: list[str] = []

    with st.status(label, expanded=True) as status:
        log_area = st.empty()

        def on_progress(msg: str) -> None:
            log.append(msg)
            # Show last 15 lines so the area doesn't grow unboundedly
            log_area.text("\n".join(log[-15:]))

        try:
            result = fn(*args, on_progress=on_progress, **kwargs)
            status.update(label=f"{label} — complete", state="complete")
        except Exception as e:
            status.update(label=f"{label} — failed", state="error")
            st.error(f"Pipeline error: {e}")
            raise

    return result

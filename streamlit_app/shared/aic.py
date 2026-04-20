"""Smart Intake Completion (AIC) — shared Streamlit components.

AIC-01: Post-intake Haiku pass — up to 3 follow-up questions after intake submit.
AIC-02: Pre-final-run Sonnet pass — 3–5 warning cards; Run button locked until all acknowledged.

Usage:

    # AIC-01 — call after intake form submit, before pipeline stage
    from streamlit_app.shared.aic import render_intake_questions
    proceed = render_intake_questions(st, case_id, intake_summary)

    # AIC-02 — call when user switches to Final Run mode
    from streamlit_app.shared.aic import render_prefinalrun_review
    all_acknowledged = render_prefinalrun_review(st, case_id)
    if all_acknowledged:
        st.button("Run Pipeline")
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anthropic

import config
from tools.file_tools import case_dir

# ── AIC-01 ─────────────────────────────────────────────────────────────────────

_AIC01_SYSTEM = """You are an expert forensic consulting assistant helping to complete an intake form.

The consultant has just submitted a case intake. Your job is to identify the 3 most important
follow-up questions that would meaningfully improve the quality of the final deliverable.

Focus on gaps that would cause the pipeline to produce generic output:
- Missing scope constraints (date ranges, entity list, transaction types)
- Unclear engagement objectives
- Ambiguous client context (sector, jurisdiction, regulatory exposure)
- Missing red flags or known issues the consultant may not have mentioned

Output as JSON:
{
  "questions": [
    {"id": "q1", "question": "...", "why_important": "..."},
    {"id": "q2", "question": "...", "why_important": "..."},
    {"id": "q3", "question": "...", "why_important": "..."}
  ]
}

Output ONLY valid JSON — no preamble, no explanation."""


def render_intake_questions(
    st,
    case_id: str,
    intake_summary: str,
) -> bool:
    """Render AIC-01: post-intake follow-up questions via Haiku.

    Returns True when the consultant has answered or skipped all questions and
    it is safe to proceed to the pipeline.

    Uses st.session_state keyed by case_id to persist state across reruns.
    """
    _state_key   = f"aic01_state_{case_id}"
    _answers_key = f"aic01_answers_{case_id}"

    # States: "generating" | "asking" | "done" | "skipped"
    if _state_key not in st.session_state:
        st.session_state[_state_key]   = "generating"
        st.session_state[_answers_key] = {}

    state = st.session_state[_state_key]

    if state in ("done", "skipped"):
        return True

    if state == "generating":
        with st.spinner("Checking for follow-up questions..."):
            questions = _generate_followup_questions(intake_summary)
        if not questions:
            st.session_state[_state_key] = "done"
            return True
        st.session_state["aic01_questions"] = questions
        st.session_state[_state_key] = "asking"
        st.rerun()

    # state == "asking"
    questions: list[dict] = st.session_state.get("aic01_questions", [])
    answers: dict = st.session_state[_answers_key]

    st.markdown("### Follow-up Questions")
    st.caption("These questions help improve the quality of the final deliverable.")

    for q in questions:
        qid = q["id"]
        st.markdown(f"**{q['question']}**")
        st.caption(f"Why this matters: {q['why_important']}")
        answer = st.text_area(
            "Your answer (leave blank to skip this question)",
            key=f"aic01_ans_{case_id}_{qid}",
            value=answers.get(qid, ""),
        )
        answers[qid] = answer

    st.session_state[_answers_key] = answers

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Save & Continue", key=f"aic01_save_{case_id}"):
            _save_intake_qa(case_id, questions, answers)
            st.session_state[_state_key] = "done"
            st.rerun()
    with col2:
        if st.button("Skip for now", key=f"aic01_skip_{case_id}"):
            st.session_state[_state_key] = "skipped"
            st.rerun()

    return False


def _generate_followup_questions(intake_summary: str) -> list[dict]:
    """Call Haiku to generate follow-up questions. Returns [] on any failure."""
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model=config.HAIKU,
            max_tokens=512,
            system=_AIC01_SYSTEM,
            messages=[
                {"role": "user", "content": f"Intake summary:\n\n{intake_summary[:4000]}"}
            ],
        )
        raw = resp.content[0].text.strip()
        data = json.loads(raw)
        return data.get("questions", [])
    except Exception:
        return []


def _save_intake_qa(case_id: str, questions: list[dict], answers: dict) -> None:
    """Persist intake Q&A to D_Working_Papers/intake_qa.json."""
    cdir = case_dir(case_id)
    wp_dir = cdir / "D_Working_Papers"
    wp_dir.mkdir(parents=True, exist_ok=True)

    qa_path = wp_dir / "intake_qa.json"
    record = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "qa": [
            {
                "question":      q["question"],
                "why_important": q["why_important"],
                "answer":        answers.get(q["id"], ""),
            }
            for q in questions
        ],
    }
    tmp = qa_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, indent=2), encoding="utf-8")
    os.replace(tmp, qa_path)


# ── AIC-02 ─────────────────────────────────────────────────────────────────────

_AIC02_SYSTEM = """You are a senior forensic consultant doing a pre-run review before a final pipeline run.

Analyse the accumulated case materials and identify 3–5 specific concerns that could affect deliverable quality.

Each concern should be actionable — either the consultant can resolve it now, or they should consciously
decide to proceed without addressing it.

Focus on:
- Scope gaps (missing documents, date ranges not covered)
- Potential conflicts between registered facts and red flags
- High-risk assumptions in the intake that lack documentary support
- Regulatory or jurisdictional issues worth flagging before the pipeline commits

Output as JSON:
{
  "cards": [
    {
      "id": "w1",
      "title": "...",
      "detail": "...",
      "severity": "high|medium|low",
      "suggested_action": "..."
    }
  ]
}

Output ONLY valid JSON — no preamble, no explanation."""


def render_prefinalrun_review(
    st,
    case_id: str,
    materials_summary: str,
) -> bool:
    """Render AIC-02: pre-final-run warning cards via Sonnet.

    Returns True only when ALL cards have been acknowledged (resolved or proceeded-anyway).
    The Run Pipeline button must not appear until this returns True.
    """
    _state_key = f"aic02_state_{case_id}"
    _ack_key   = f"aic02_ack_{case_id}"

    # States: "generating" | "reviewing" | "done"
    if _state_key not in st.session_state:
        st.session_state[_state_key] = "generating"
        st.session_state[_ack_key]   = {}

    state = st.session_state[_state_key]

    if state == "done":
        return True

    if state == "generating":
        with st.spinner("Running pre-run review..."):
            cards = _generate_warning_cards(materials_summary)
        if not cards:
            st.session_state[_state_key] = "done"
            return True
        st.session_state["aic02_cards"] = cards
        st.session_state[_state_key] = "reviewing"
        st.rerun()

    # state == "reviewing"
    cards: list[dict] = st.session_state.get("aic02_cards", [])
    ack:   dict       = st.session_state[_ack_key]

    st.markdown("### Pre-Run Review")
    st.caption("Acknowledge each concern before the pipeline can run.")

    all_acked = True
    for card in cards:
        cid      = card["id"]
        severity = card.get("severity", "medium")
        cls      = {"high": "severity-critical", "medium": "severity-warning", "low": "severity-info"}.get(severity, "severity-info")

        st.markdown(
            f'<div class="{cls}"><strong>{card["title"]}</strong><br/>'
            f'{card["detail"]}<br/><em>Suggested: {card.get("suggested_action","")}</em></div>',
            unsafe_allow_html=True,
        )

        if ack.get(cid):
            st.success(f"Acknowledged: {ack[cid]}")
        else:
            all_acked = False
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Resolve (I'll address this)", key=f"aic02_resolve_{case_id}_{cid}"):
                    ack[cid] = "resolved"
                    st.session_state[_ack_key] = ack
                    st.rerun()
            with col2:
                if st.button("Proceed anyway", key=f"aic02_proceed_{case_id}_{cid}"):
                    ack[cid] = "proceeded_anyway"
                    st.session_state[_ack_key] = ack
                    st.rerun()

    if all_acked and cards:
        _save_prefinalrun_review(case_id, cards, ack)
        st.session_state[_state_key] = "done"
        return True

    return False


def _generate_warning_cards(materials_summary: str) -> list[dict]:
    """Call Sonnet to generate pre-run warning cards. Returns [] on failure."""
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model=config.SONNET,
            max_tokens=1024,
            system=_AIC02_SYSTEM,
            messages=[
                {"role": "user", "content": f"Accumulated case materials:\n\n{materials_summary[:6000]}"}
            ],
        )
        raw = resp.content[0].text.strip()
        data = json.loads(raw)
        return data.get("cards", [])
    except Exception:
        return []


def _save_prefinalrun_review(case_id: str, cards: list[dict], ack: dict) -> None:
    """Persist pre-final-run review results to D_Working_Papers/prefinalrun_review.json."""
    cdir = case_dir(case_id)
    wp_dir = cdir / "D_Working_Papers"
    wp_dir.mkdir(parents=True, exist_ok=True)

    review_path = wp_dir / "prefinalrun_review.json"
    record = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "cards": [
            {
                "title":            c["title"],
                "detail":           c["detail"],
                "severity":         c.get("severity", "medium"),
                "suggested_action": c.get("suggested_action", ""),
                "acknowledgement":  ack.get(c["id"], "unacknowledged"),
            }
            for c in cards
        ],
    }
    tmp = review_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, indent=2), encoding="utf-8")
    os.replace(tmp, review_path)

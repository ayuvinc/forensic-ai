"""Hybrid intake engine for structured field + Remarks-triggered conversation.

BA-IA-07: replaces fully conversational intake with a two-phase model:
  Phase 1 — Structured fields (dropdowns, multiselect, radio, text) with optional
             Remarks cells per field.
  Phase 2 — For any non-empty Remarks (> 10 chars): fire one targeted AI conversation
             (max 2 rounds) to refine the scope note.
  Phase 3 — Confirmation panel; Maher confirms or edits.
  Phase 4 — Returns final field values for CaseIntake construction.

Engine is workflow-agnostic. Each workflow page provides a list[WorkflowFieldConfig]
that declares which fields to render and which have Remarks cells.

Session state keys are namespaced by workflow_id to prevent cross-page collisions.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

import streamlit as st


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class WorkflowFieldConfig:
    """Declares one structured field in a hybrid intake form.

    field_type controls the Streamlit widget rendered:
      selectbox   — st.selectbox with options list
      multiselect — st.multiselect with options list
      radio       — st.radio with options list
      text        — st.text_input (single line)
      textarea    — st.text_area (multi-line narrative)

    has_remarks: if True, an optional Remarks expander appears below the widget.
    remarks_placeholder: hint text inside the Remarks text_area.
    """
    id: str
    label: str
    field_type: Literal["selectbox", "multiselect", "radio", "text", "textarea"]
    options: list[str] = field(default_factory=list)
    required: bool = True
    has_remarks: bool = False
    remarks_placeholder: str = ""
    help_text: str = ""


@dataclass
class RemarksResult:
    """Holds one field's original value, remarks text, conversation history, and refined value."""
    field_id: str
    field_label: str
    original_value: str
    remarks: str
    conversation: list[dict]   # [{"role": "assistant"|"user", "content": "..."}]
    refined_value: str         # original_value + AI-derived nuance, or original if no conversation


# ── HybridIntakeEngine ────────────────────────────────────────────────────────

class HybridIntakeEngine:
    """Multi-step intake engine that renders structured fields + optional Remarks conversations.

    Usage in a Streamlit page:
        engine = HybridIntakeEngine(st, _MY_FIELD_CONFIG, "investigation_report")
        result = engine.run()
        if result is not None:
            # intake is locked; build CaseIntake from result["values"]
            ...

    engine.run() returns None until the user completes confirmation.
    Once confirmed, returns {"values": dict[field_id, Any], "refined": list[RemarksResult]}.
    """

    _STEP_FIELDS       = "fields"
    _STEP_REMARKS      = "remarks"
    _STEP_CONFIRMATION = "confirmation"
    _STEP_DONE         = "done"

    def __init__(
        self,
        st_module: Any,
        fields: list[WorkflowFieldConfig],
        workflow_id: str,
    ) -> None:
        self._st  = st_module
        self._fields = fields
        self._wid = workflow_id
        self._key = f"hybrid_intake_{workflow_id}"   # session_state namespace

    # ── Public interface ──────────────────────────────────────────────────────

    def run(self) -> Optional[dict]:
        """Drive the step machine. Returns result dict when done, else None."""
        step = self._st.session_state.get(f"{self._key}_step", self._STEP_FIELDS)

        if step == self._STEP_FIELDS:
            self._render_structured_fields()
        elif step == self._STEP_REMARKS:
            self._render_remarks_conversation()
        elif step == self._STEP_CONFIRMATION:
            done = self._render_confirmation()
            if done:
                return self._build_result()
        elif step == self._STEP_DONE:
            return self._build_result()

        return None

    def reset(self) -> None:
        """Clear all engine session state for this workflow. Call on page re-entry."""
        keys_to_clear = [k for k in self._st.session_state if k.startswith(self._key)]
        for k in keys_to_clear:
            del self._st.session_state[k]

    # ── Step 1: Structured fields ─────────────────────────────────────────────

    def _render_structured_fields(self) -> None:
        values: dict[str, Any] = {}
        remarks: dict[str, str] = {}

        for cfg in self._fields:
            values[cfg.id] = self._render_widget(cfg)
            if cfg.has_remarks:
                with self._st.expander(f"Remarks for '{cfg.label}' (optional)", expanded=False):
                    remarks[cfg.id] = self._st.text_area(
                        "Add context or edge-case notes here",
                        key=f"{self._key}_rem_{cfg.id}",
                        placeholder=cfg.remarks_placeholder or "Optional — leave blank to skip",
                        max_chars=500,
                        label_visibility="collapsed",
                    )
            else:
                remarks[cfg.id] = ""

        self._st.divider()
        missing = [
            cfg.label for cfg in self._fields
            if cfg.required and not self._value_present(values.get(cfg.id))
        ]
        if missing:
            self._st.caption(f"Required fields: {', '.join(missing)}")

        if self._st.button("Continue", type="primary", disabled=bool(missing), key=f"{self._key}_continue"):
            self._st.session_state[f"{self._key}_values"]  = values
            self._st.session_state[f"{self._key}_remarks"] = remarks

            pending = self._scan_remarks(remarks)
            self._st.session_state[f"{self._key}_pending_remarks"] = [
                {"field_id": r.field_id, "field_label": r.field_label,
                 "original_value": r.original_value, "remarks": r.remarks,
                 "conversation": [], "refined_value": r.original_value}
                for r in pending
            ]
            self._st.session_state[f"{self._key}_remarks_idx"] = 0
            self._st.session_state[f"{self._key}_step"] = (
                self._STEP_REMARKS if pending else self._STEP_CONFIRMATION
            )
            self._st.rerun()

    def _render_widget(self, cfg: WorkflowFieldConfig) -> Any:
        key = f"{self._key}_fld_{cfg.id}"
        if cfg.field_type == "selectbox":
            return self._st.selectbox(cfg.label, cfg.options, key=key, help=cfg.help_text)
        if cfg.field_type == "multiselect":
            return self._st.multiselect(cfg.label, cfg.options, key=key, help=cfg.help_text)
        if cfg.field_type == "radio":
            return self._st.radio(cfg.label, cfg.options, key=key, horizontal=True, help=cfg.help_text)
        if cfg.field_type == "text":
            return self._st.text_input(cfg.label, key=key, help=cfg.help_text)
        if cfg.field_type == "textarea":
            return self._st.text_area(cfg.label, key=key, help=cfg.help_text)
        return None

    @staticmethod
    def _value_present(v: Any) -> bool:
        if v is None:
            return False
        if isinstance(v, list):
            return len(v) > 0
        if isinstance(v, str):
            return bool(v.strip())
        return True

    # ── Step 2: Remarks conversations ─────────────────────────────────────────

    def _scan_remarks(self, remarks: dict[str, str]) -> list[RemarksResult]:
        values = self._st.session_state.get(f"{self._key}_values", {})
        pending = []
        for cfg in self._fields:
            rem = remarks.get(cfg.id, "")
            if len(rem.strip()) > 10:
                pending.append(RemarksResult(
                    field_id=cfg.id,
                    field_label=cfg.label,
                    original_value=str(values.get(cfg.id, "")),
                    remarks=rem.strip(),
                    conversation=[],
                    refined_value=str(values.get(cfg.id, "")),
                ))
        return pending

    def _render_remarks_conversation(self) -> None:
        """Show one Remarks conversation at a time; advance to next when done."""
        pending = self._st.session_state.get(f"{self._key}_pending_remarks", [])
        idx = self._st.session_state.get(f"{self._key}_remarks_idx", 0)

        if idx >= len(pending):
            self._st.session_state[f"{self._key}_step"] = self._STEP_CONFIRMATION
            self._st.rerun()
            return

        rr = pending[idx]
        self._st.subheader(f"Clarifying: {rr['field_label']}")
        self._st.caption(f"Field value: **{rr['original_value']}**")
        self._st.info(f"You noted: *{rr['remarks']}*")

        conv = rr.get("conversation", [])
        rounds_done = sum(1 for m in conv if m["role"] == "user")

        # Show prior conversation
        for msg in conv:
            with self._st.chat_message(msg["role"]):
                self._st.write(msg["content"])

        # Fire AI question if we haven't yet for this round
        if len(conv) == 0 or (conv[-1]["role"] == "user" and rounds_done < 2):
            if len(conv) == 0:
                ai_question = self._get_ai_question(rr)
                conv.append({"role": "assistant", "content": ai_question})
                pending[idx]["conversation"] = conv
                self._st.session_state[f"{self._key}_pending_remarks"] = pending
                self._st.rerun()

        # User response input
        if conv and conv[-1]["role"] == "assistant" and rounds_done < 2:
            user_reply = self._st.text_input(
                "Your response",
                key=f"{self._key}_rem_reply_{idx}_{rounds_done}",
            )
            if self._st.button("Submit", key=f"{self._key}_rem_submit_{idx}_{rounds_done}") and user_reply.strip():
                conv.append({"role": "user", "content": user_reply.strip()})
                # Build refined value from original + conversation
                refined = f"{rr['original_value']} [clarification: {user_reply.strip()}]"
                pending[idx]["refined_value"] = refined
                pending[idx]["conversation"]  = conv
                self._st.session_state[f"{self._key}_pending_remarks"] = pending

                # Move to next remark or confirmation
                self._st.session_state[f"{self._key}_remarks_idx"] = idx + 1
                self._st.rerun()
        elif rounds_done >= 2 or (conv and conv[-1]["role"] == "user"):
            # Max rounds reached or last message was user — advance
            if self._st.button("Continue to next", key=f"{self._key}_rem_next_{idx}"):
                self._st.session_state[f"{self._key}_remarks_idx"] = idx + 1
                self._st.rerun()

    def _get_ai_question(self, rr: dict) -> str:
        """Call Claude (Haiku) for a clarifying question about the remark.

        Falls back gracefully in knowledge_only mode or on API failure.
        """
        research_mode = os.environ.get("RESEARCH_MODE", "knowledge_only")
        if research_mode == "knowledge_only":
            # No API call in demo/test mode — use a generic clarifying prompt
            return (
                f"You noted '{rr['remarks']}' regarding **{rr['field_label']}**. "
                f"Could you clarify: what specific aspect is most important for the scope of this engagement?"
            )

        try:
            import anthropic
            from config import HAIKU
            client = anthropic.Anthropic()
            system = (
                "You are assisting with intake clarification for a forensic consulting engagement. "
                "Ask exactly ONE targeted question — no preamble, no lists — to clarify the remark. "
                "Keep the question under 2 sentences."
            )
            user_msg = (
                f"Field: {rr['field_label']}\n"
                f"Selected value: {rr['original_value']}\n"
                f"Consultant remark: {rr['remarks']}\n\n"
                "Ask one targeted clarifying question."
            )
            response = client.messages.create(
                model=HAIKU,
                max_tokens=200,
                system=system,
                messages=[{"role": "user", "content": user_msg}],
            )
            return response.content[0].text.strip()
        except Exception:
            # Any API failure falls back to generic question
            return (
                f"You noted '{rr['remarks']}' regarding **{rr['field_label']}**. "
                f"Could you clarify the specific scope implication for this engagement?"
            )

    # ── Step 3: Confirmation ──────────────────────────────────────────────────

    def _render_confirmation(self) -> bool:
        """Show intake summary; return True when user confirms."""
        self._st.subheader("Confirm intake")
        self._st.caption("Review all values before the pipeline runs. Click **Edit** to go back.")

        values  = self._st.session_state.get(f"{self._key}_values", {})
        pending = self._st.session_state.get(f"{self._key}_pending_remarks", [])
        refined = {r["field_id"]: r["refined_value"] for r in pending}

        for cfg in self._fields:
            display_val = refined.get(cfg.id) or str(values.get(cfg.id, "—"))
            self._st.markdown(f"**{cfg.label}:** {display_val}")

        self._st.divider()
        col_confirm, col_edit = self._st.columns(2)
        with col_confirm:
            if self._st.button("Confirm intake", type="primary", key=f"{self._key}_confirm"):
                self._st.session_state[f"{self._key}_step"] = self._STEP_DONE
                return True
        with col_edit:
            if self._st.button("Edit", key=f"{self._key}_edit"):
                self._st.session_state[f"{self._key}_step"] = self._STEP_FIELDS
                self._st.rerun()
        return False

    # ── Result builder ────────────────────────────────────────────────────────

    def _build_result(self) -> dict:
        values  = self._st.session_state.get(f"{self._key}_values", {})
        pending = self._st.session_state.get(f"{self._key}_pending_remarks", [])
        refined_list = [
            RemarksResult(
                field_id=r["field_id"],
                field_label=r["field_label"],
                original_value=r["original_value"],
                remarks=r["remarks"],
                conversation=r["conversation"],
                refined_value=r["refined_value"],
            )
            for r in pending
        ]
        # Apply refined values on top of original values
        effective = dict(values)
        for r in refined_list:
            effective[r.field_id] = r.refined_value
        return {"values": effective, "refined": refined_list}


# ── Investigation field config (BA-IA-07) ─────────────────────────────────────

INVESTIGATION_TYPES_ORDERED = [
    "Asset Misappropriation",
    "Financial Statement Fraud",
    "Corruption & Bribery",
    "Cyber Fraud / Digital Investigation",
    "Procurement Fraud",
    "Revenue Leakage",
    "Compliance Investigation",
    "Agreed-Upon Procedures (AUP)",
    "Other / Custom",
]

INVESTIGATION_AUDIENCES = [
    "Management",
    "Board",
    "Legal Proceedings (Expert Witness)",
    "Regulatory Submission",
    "Multiple Audiences",
]

INVESTIGATION_REGULATORS = [
    "CBUAE", "DFSA", "ADGM / FSRA", "SCA", "None",
    "Multiple regulators", "Unknown / under investigation",
]

INVESTIGATION_EVIDENCE = [
    "Financial records",
    "Contracts / invoices",
    "Email / communications",
    "Interview transcripts",
    "Digital / system data",
    "Bank statements",
    "None available",
]

INVESTIGATION_JURISDICTIONS = [
    "UAE", "Saudi Arabia", "India", "UK", "USA", "Other", "Multiple jurisdictions",
]

_INVESTIGATION_FIELD_CONFIG: list[WorkflowFieldConfig] = [
    WorkflowFieldConfig(
        id="jurisdiction",
        label="Primary jurisdiction",
        field_type="selectbox",
        options=INVESTIGATION_JURISDICTIONS,
        required=True,
        has_remarks=True,
        remarks_placeholder="e.g. UAE + offshore holding structure in BVI",
    ),
    WorkflowFieldConfig(
        id="investigation_type",
        label="Investigation type",
        field_type="selectbox",
        options=INVESTIGATION_TYPES_ORDERED,
        required=True,
        has_remarks=True,
        remarks_placeholder="e.g. Type 3 but also involves AML aspects",
    ),
    WorkflowFieldConfig(
        id="regulators_implicated",
        label="Regulators implicated (if any)",
        field_type="multiselect",
        options=INVESTIGATION_REGULATORS,
        required=False,
        has_remarks=True,
        remarks_placeholder="e.g. Possibly DFSA but matter is ongoing — uncertain",
    ),
    WorkflowFieldConfig(
        id="evidence_available",
        label="Evidence available",
        field_type="multiselect",
        options=INVESTIGATION_EVIDENCE,
        required=False,
        has_remarks=True,
        remarks_placeholder="e.g. Some documents withheld by client — access limited",
    ),
    WorkflowFieldConfig(
        id="audience",
        label="Report audience",
        field_type="selectbox",
        options=INVESTIGATION_AUDIENCES,
        required=True,
        has_remarks=False,
    ),
    WorkflowFieldConfig(
        id="industry",
        label="Industry / sector",
        field_type="text",
        required=True,
        has_remarks=False,
        help_text="e.g. Financial services, Real estate, Construction",
    ),
    WorkflowFieldConfig(
        id="description",
        label="Engagement description / scope",
        field_type="textarea",
        required=True,
        has_remarks=False,
        help_text="Narrative fields are always free text — no Remarks trigger per BA-IA-07.",
    ),
]

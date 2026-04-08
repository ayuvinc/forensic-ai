"""Partner agent system and task prompts."""

from __future__ import annotations

from schemas.case import CaseIntake


def build_system_prompt(
    workflow: str,
    intake: CaseIntake,
    firm_name: str = "GoodWork Forensic Consulting",
    research_mode: str = "knowledge_only",
) -> str:
    mode_section = _build_mode_section(research_mode)

    return f"""You are a Partner at {firm_name}.
Your role is the final quality gate before a deliverable is presented to the client.

CLIENT: {intake.client_name}
WORKFLOW: {workflow}
PRIMARY JURISDICTION: {intake.primary_jurisdiction}
OPERATING JURISDICTIONS: {', '.join(intake.operating_jurisdictions)}
RESEARCH MODE: {research_mode}

PARTNER REVIEW STANDARDS:
1. EVIDENCE CHAIN INTEGRITY — investigation findings must follow ACFE procedure → finding → implication → conclusion
2. PERMISSIBLE EVIDENCE ONLY — no lead-only or inadmissible evidence may appear in findings
3. COMMERCIAL DEFENSIBILITY — conclusions must withstand expert witness scrutiny
4. JURISDICTION ALIGNMENT — report must correctly identify {intake.primary_jurisdiction} as governing law
5. NO OPINIONS — only facts derived from documented procedures
6. SCHEMA INTEGRITY — output must be structurally complete (no empty findings/risks list)
{mode_section}

APPROVAL RULES:
- For investigation reports: validate FindingChain.permissible_evidence_only=true before approving
- If approving: set approved=true, conditions=[] (or minor conditions)
- If rejecting: set approved=false, list specific failures

OUTPUT FORMAT:
Your response must be valid JSON:
{{
  "approving_agent": "partner",
  "approved": true/false,
  "conditions": ["condition 1 if any", "..."],
  "regulatory_sign_off": "Partner sign-off statement referencing key regulatory framework...",
  "escalation_required": false,
  "escalation_reason": null,
  "review_notes": "Partner review notes...",
  "revision_requested": false,
  "revision_reason": null
}}

If revision is needed, set revision_requested=true and explain clearly in revision_reason.
"""


def _build_mode_section(research_mode: str) -> str:
    """Return the mode-specific approval guidance block."""
    if research_mode == "knowledge_only":
        return """
KNOWLEDGE-ONLY MODE — APPROVAL RULES:
You are operating in knowledge_only mode. No live regulatory or sanctions data was fetched.

APPROVE if:
- Output structure is sound (all required sections present)
- Risks or findings list is non-empty
- Regulatory references are broadly correct (right regulator, right domain)
- Open questions or evidence gaps are documented (this is expected and acceptable)

DO NOT reject because:
- Authoritative citations are absent or have empty source_url
- Output relies on regulatory knowledge rather than live fetched sources
- Findings are framed in general terms rather than client-specific (document as conditions[])
- Escalation is not required solely due to absence of live citations

DO reject if:
- findings/risks list is empty
- A regulatory citation names a body that does not govern this jurisdiction
- Output has a structural schema violation (missing required top-level fields)
- Logical contradiction: conclusion contradicts a stated finding

For any evidence gaps, set conditions[] with "Consultant to obtain and attach [evidence type] before client delivery."
Escalation is not required in knowledge_only mode for citation absence.
"""
    else:
        # live mode — original citation enforcement
        return """
7. REGULATORY ACCURACY — every regulatory claim must have an authoritative citation fetched via regulatory_lookup

LIVE MODE — APPROVAL RULES:
All 7 standards must be met. Use regulatory_lookup to verify regulatory claims before approving.
For FRM: validate all RiskItems have regulatory_references from authoritative sources.
Missing authoritative citations on regulatory claims are grounds for rejection.
"""


def build_task_message(
    pm_output: dict,
    junior_output: dict | None = None,
    research_mode: str = "knowledge_only",
) -> str:
    import json

    def preview(d: dict, n: int = 3000) -> str:
        t = json.dumps(d, indent=2, default=str)
        return t[:n] + "\n...[truncated]" if len(t) > n else t

    msg = "Please conduct final Partner review of this engagement output.\n\n"
    msg += f"PM REVIEW:\n{preview(pm_output)}\n\n"
    if junior_output:
        msg += f"UNDERLYING DRAFT (summary):\n{preview(junior_output, 2000)}\n\n"
    msg += "Provide your approval decision in the required JSON format."
    if research_mode == "live":
        msg += "\n\nUse regulatory_lookup to verify any regulatory claims before approving."
    return msg

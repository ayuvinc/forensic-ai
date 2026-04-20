"""Junior Analyst system and task prompts."""

from __future__ import annotations

from schemas.case import CaseIntake
from schemas.documents import DocumentIndex


BOUNDED_RETRIEVAL_INSTRUCTIONS = """
DOCUMENT RETRIEVAL RULES (mandatory):
- NEVER attempt to read a full document in one call.
- ALWAYS use read_excerpt(doc_id, max_chars=8000) for your first look at any document.
- For large documents, the excerpt will list available sections — use read_section(doc_id, section_id) to navigate.
- Use read_pages(doc_id, page_range="X-Y") for page-specific content.
- Use find_relevant_docs(query) to locate relevant documents before reading them.
- If a document is truncated, follow the navigation hint provided.
""".strip()

ACFE_EVIDENCE_INSTRUCTIONS = """
EVIDENCE STANDARDS (ACFE):
- Every finding must follow: Procedure performed → Factual finding → Implication → Conclusion.
- Only cite PERMISSIBLE evidence (documented procedures, signed records, official filings).
- LEAD-ONLY sources (tips, hearsay, unverified allegations) may inform procedures but NEVER appear in findings.
- Always include verbatim source excerpts — evidence_ids alone are insufficient.
- Do NOT express opinions. State procedures performed and observations noted.
""".strip()


def build_system_prompt(
    workflow: str,
    intake: CaseIntake,
    doc_index: DocumentIndex | None = None,
    revision_feedback: str | None = None,
    firm_name: str = "GoodWork Forensic Consulting",
    language_standard: str = "acfe",
) -> str:
    """Build the Consultant system prompt for a given workflow and intake."""
    from agents.shared.language_standards import get_language_block

    is_investigation = workflow in ("investigation_report",)

    base = f"""You are a Forensic Consultant at {firm_name}.
Your role is to research and draft initial findings for review by the Project Manager and Partner.

CLIENT: {intake.client_name}
INDUSTRY: {intake.industry}
WORKFLOW: {workflow}
PRIMARY JURISDICTION: {intake.primary_jurisdiction}
OPERATING JURISDICTIONS: {', '.join(intake.operating_jurisdictions)}
DESCRIPTION: {intake.description}

REGULATORY CONTEXT:
- Use regulatory_lookup with jurisdictions={intake.operating_jurisdictions} for all regulatory queries.
- Use company_lookup with jurisdictions={intake.operating_jurisdictions} for company searches.
- Primary law and report language follows: {intake.primary_jurisdiction}

{BOUNDED_RETRIEVAL_INSTRUCTIONS}
"""

    if is_investigation:
        base += f"\n{ACFE_EVIDENCE_INSTRUCTIONS}\n"

    if doc_index and doc_index.documents:
        docs_summary = "\n".join(
            f"  - [{d.doc_id}] {d.filename} ({d.doc_type}) — {d.summary or 'no summary'}"
            for d in doc_index.documents[:20]
        )
        base += f"\nAVAILABLE DOCUMENTS:\n{docs_summary}\n"
        base += "\nUse find_relevant_docs(query) to locate relevant documents, then read_excerpt to read them.\n"

    base += """
OUTPUT FORMAT:
Your final response must be valid JSON matching this structure:
{
  "case_id": "...",
  "version": 1,
  "summary": "Executive summary of findings...",
  "findings": [
    {
      "title": "Finding title",
      "description": "Detailed finding",
      "evidence": "Source references",
      "risk_level": "high|medium|low"
    }
  ],
  "methodology": "Procedures performed...",
  "regulatory_implications": "Regulatory context and obligations...",
  "recommendations": ["Recommendation 1", "..."],
  "open_questions": ["Question requiring further investigation", "..."],
  "citations": [
    {
      "source_url": "...",
      "source_name": "...",
      "source_type": "authoritative|news|general|unverified",
      "retrieved_at": "ISO datetime",
      "excerpt": "Relevant passage",
      "confidence": "high|medium|low"
    }
  ]
}

Produce thorough, professional analysis. Use all available tools before drafting.
"""

    if revision_feedback:
        base += f"\nREVISION INSTRUCTIONS FROM PROJECT MANAGER:\n{revision_feedback}\n"
        base += "Address ALL must_fix items before proceeding to should_fix items.\n"

    base += f"\n{get_language_block(language_standard)}\n"

    return base


def build_task_message(intake: CaseIntake) -> str:
    """Build the initial user message for the Consultant."""
    return (
        f"Please conduct research and draft initial findings for the following engagement:\n\n"
        f"Client: {intake.client_name}\n"
        f"Industry: {intake.industry}\n"
        f"Case ID: {intake.case_id}\n"
        f"Scope: {intake.description}\n\n"
        "Begin by using find_relevant_docs to locate any uploaded documents, "
        "then use regulatory_lookup and other research tools to gather authoritative sources. "
        "Produce a thorough initial draft following the output format specified."
    )

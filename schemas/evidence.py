"""Evidence classification and finding chain schemas — ACFE standard."""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel
from schemas.research import Citation
from schemas.documents import DocumentProvenance, PermissibilityLiteral


class EvidenceItem(BaseModel):
    evidence_id: str
    case_id: str
    source_doc_id: str
    source_excerpt: str            # verbatim excerpt from source — specific passage, not just doc ID
    evidence_type: Literal[
        "document", "email", "excel_data", "interview",
        "transaction", "chat_message", "attachment", "other"
    ]
    description: str
    permissibility: PermissibilityLiteral
    provenance: DocumentProvenance
    usability: Literal["report_citable", "corroborated_fact", "usable_lead"]
    # report_citable: permissible + cited by specific excerpt
    # corroborated_fact: permissible but not yet cited by excerpt
    # usable_lead: lead_only — cannot appear in findings
    citations: list[Citation] = []


class FindingChain(BaseModel):
    """ACFE-standard evidence chain: procedure → finding → implication → conclusion.

    supporting_evidence must contain evidence_ids of PERMISSIBLE items only.
    Partner validates permissible_evidence_only=True before ApprovalDecision(approved=True).
    """
    finding_id: str
    procedure_performed: str       # "We reviewed vendor invoices for period X to Y..."
    factual_finding: str           # "We noted that..."
    implication: str               # "This indicated / led us to..."
    conclusion: str                # "Based on our review of X, Y, Z, we conclude..."
    supporting_evidence: list[str] = []  # evidence_ids — must all be PERMISSIBLE
    supporting_excerpts: list[str] = []  # verbatim quotes from supporting evidence
    permissible_evidence_only: bool = False  # set True by Partner after validation
    risk_rating: Literal["critical", "high", "medium", "low", "informational"]

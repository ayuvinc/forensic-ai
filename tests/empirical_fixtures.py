"""
Shared fixtures for empirical simulation tests.
Provides controlled AgentHandoff builders and test CaseIntake factories.
"""
from __future__ import annotations

import uuid


# ---------------------------------------------------------------------------
# AgentHandoff builders
# ---------------------------------------------------------------------------

def make_junior_handoff(quality: str = "good", revision_round: int = 0,
                        case_id: str = "TEST-001",
                        workflow: str = "investigation_report") -> dict:
    """
    quality values:
      "good"            — complete valid JuniorDraft
      "missing_citations" — citations=[]
      "empty_findings"    — findings=[]
      "bad_evidence_ids"  — finding references non-existent evidence ID
      "schema_invalid"    — missing required field (summary absent)
    """
    base_output = {
        "case_id": case_id,
        "version": revision_round + 1,
        "summary": "Summary of findings from junior analyst review.",
        "findings": [
            {
                "finding_id": "F-001",
                "title": "Unusual expense reimbursements",
                "description": "Multiple reimbursements with no supporting receipts.",
                "evidence": ["E-001"],
                "risk_level": "high",
            }
        ],
        "methodology": "Document review and transaction analysis.",
        "regulatory_implications": "Potential breach of internal controls policy.",
        "recommendations": ["Implement receipt-mandatory policy", "Conduct training"],
        "open_questions": ["Who approved these transactions?"],
        "citations": [
            {
                "source_name": "COSO Framework",
                "source_type": "authoritative",
                "retrieved_at": "2026-04-21",
                "excerpt": "Internal controls framework section 4.2",
                "confidence": "high",
                "source_url": "https://www.coso.org/framework",
            }
        ],
        "revision_round": revision_round,
    }

    if quality == "missing_citations":
        base_output["citations"] = []
    elif quality == "empty_findings":
        base_output["findings"] = []
    elif quality == "bad_evidence_ids":
        base_output["findings"][0]["evidence"] = ["E-NONEXISTENT-999"]
    elif quality == "schema_invalid":
        del base_output["summary"]  # required field removed

    return {
        "output": base_output,
        "revision_requested": False,
        "revision_reason": None,
        "agent": "junior",
        "workflow": workflow,
        "turn_count": 2,
        "tool_calls_made": [],
    }


def make_pm_handoff(revision_requested: bool = False,
                    feedback: str = "Please add more regulatory citations.",
                    case_id: str = "TEST-001",
                    workflow: str = "investigation_report") -> dict:
    return {
        "output": {
            "case_id": case_id,
            "review_agent": "pm",
            "approved": not revision_requested,
            "revision_requested": revision_requested,
            "feedback": feedback if revision_requested else "",
            "annotations": [],
            "quality_score": 0.55 if revision_requested else 0.78,
        },
        "revision_requested": revision_requested,
        "revision_reason": feedback if revision_requested else None,
        "agent": "pm",
        "workflow": workflow,
        "turn_count": 1,
        "tool_calls_made": [],
    }


def make_partner_handoff(revision_requested: bool = False,
                          with_disclaimer: bool = False,
                          case_id: str = "TEST-001",
                          workflow: str = "investigation_report") -> dict:
    return {
        "output": {
            "case_id": case_id,
            "approving_agent": "partner",
            "approved": not revision_requested,
            "revision_requested": revision_requested,
            "conditions": ["Disclaimer: based on available documents only."] if with_disclaimer else [],
            "regulatory_sign_off": not revision_requested,
            "escalation_required": False,
        },
        "revision_requested": revision_requested,
        "revision_reason": "Quality below partner threshold." if revision_requested else None,
        "agent": "partner",
        "workflow": workflow,
        "turn_count": 1,
        "tool_calls_made": [],
    }


# ---------------------------------------------------------------------------
# CaseIntake builder
# ---------------------------------------------------------------------------

def make_intake(workflow: str = "investigation_report",
                case_id: str | None = None,
                **overrides) -> dict:
    """Returns CaseIntake-compatible dict with all required fields."""
    base = {
        "case_id": case_id or f"TEST-{uuid.uuid4().hex[:6].upper()}",
        "client_name": "Test Client Ltd",
        "industry": "Financial Services",
        "workflow": workflow,
        "description": "Test engagement for empirical simulation.",
        "primary_jurisdiction": "UAE",
        "operating_jurisdictions": ["UAE"],
        "language": "en",
        "company_size": "medium",
        "engagement_letter_path": None,
        "sample_report_paths": [],
        "engagement_id": None,
        "recommendation_depth": "structured",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# HookEngine builder
# ---------------------------------------------------------------------------

def make_real_hook_engine():
    """Build a HookEngine with all real hooks registered (same as run.py)."""
    try:
        from core.hook_engine import HookEngine
        from hooks.pre_hooks import PRE_HOOKS
        from hooks.post_hooks import POST_HOOKS

        engine = HookEngine()
        for name, fn in PRE_HOOKS:
            engine.register_pre(name, fn)
        for name, fn in POST_HOOKS:
            engine.register_post(name, fn)
        return engine
    except ImportError as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# EvidenceItem / FindingChain builders
# ---------------------------------------------------------------------------

def make_evidence_payload(
    valid_evidence: bool = True,
    empty_excerpt: bool = False,
    non_permissible: bool = False,
) -> dict:
    """Build a post-hook payload containing evidence_items + finding_chains."""
    evidence_id = "E-001"
    permissibility = "non_permissible" if non_permissible else "permissible"
    excerpt = "" if empty_excerpt else "The transaction log shows irregular entries."

    evidence_items = [{
        "evidence_id": evidence_id,
        "case_id": "TEST-001",
        "source_doc_id": "DOC-001",
        "source_excerpt": excerpt,
        "evidence_type": "documentary",
        "description": "Transaction log extract",
        "permissibility": permissibility,
        "provenance": "Client-provided",
        "usability": "usable",
    }]

    finding_chains = [{
        "finding_id": "FC-001",
        "procedure_performed": "Transaction log review.",
        "factual_finding": "Irregular entries found.",
        "implication": "Potential fraud indicator.",
        "conclusion": "Further investigation warranted.",
        "supporting_evidence": [evidence_id],
        "permissible_evidence_only": True,
    }]

    return {
        "output": {
            "case_id": "TEST-001",
            "evidence_items": evidence_items,
            "finding_chains": finding_chains,
            "summary": "Test output",
            "findings": [],
            "methodology": "Document review",
            "regulatory_implications": "None identified.",
            "recommendations": [],
            "open_questions": [],
            "citations": [],
            "version": 1,
            "revision_round": 0,
        }
    }

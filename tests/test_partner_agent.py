"""Tests for agents/partner — BA-IA-08/BA-IA-10: Partner never blocks delivery.

Two behavioural guarantees:
1. Partner always returns approved=True, revision_requested=False regardless of citation count.
2. Evidence chain failures produce a disclaimer in conditions[], never a block.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_partner_output(**overrides) -> dict:
    """Minimal valid Partner JSON output."""
    base = {
        "approving_agent": "partner",
        "approved": True,
        "conditions": [],
        "regulatory_sign_off": "Partner sign-off.",
        "escalation_required": False,
        "escalation_reason": None,
        "review_notes": "Review complete.",
        "revision_requested": False,
        "revision_reason": None,
    }
    base.update(overrides)
    return base


def _make_finding_chain(finding_id: str = "F-01"):
    """Minimal FindingChain instance via model_construct (skips validation)."""
    from schemas.evidence import FindingChain
    return FindingChain.model_construct(
        finding_id=finding_id,
        procedure_performed="Reviewed invoices.",
        factual_finding="Duplicate payments noted.",
        implication="Control gap identified.",
        conclusion="Further review required.",
        supporting_evidence=["E-01"],
        supporting_excerpts=[],
        permissible_evidence_only=False,
        risk_rating="high",
    )


def _make_evidence_item(evidence_id: str = "E-01"):
    """Minimal EvidenceItem instance via model_construct (skips validation)."""
    from schemas.evidence import EvidenceItem
    return EvidenceItem.model_construct(
        evidence_id=evidence_id,
        case_id="test-case",
        source_doc_id="doc-01",
        source_excerpt="Invoice #1234 paid twice.",
        evidence_type="document",
        permissibility="lead_only",
        usability="usable_lead",
        provenance=None,
        description="Unverified invoice scan.",
        citations=[],
    )


# ── PFIX-01: _parse_output preserves model output faithfully ──────────────────

class TestPartnerParseOutput:
    """_parse_output must return what the model sends — prompt fix prevents bad output."""

    def test_approved_true_revision_false_passes_through(self):
        """Standard compliant output: approved=True, revision_requested=False preserved."""
        from agents.partner.agent import Partner

        output_json = json.dumps(_make_partner_output(
            conditions=["CONDITION 1: regulatory_references — No authoritative citation — verify before delivery."],
        ))

        partner = Partner.__new__(Partner)
        result = partner._parse_output(output_json)

        assert result["approved"] is True
        assert result["revision_requested"] is False

    def test_parse_fallback_on_bad_json_returns_approved_false_not_revision(self):
        """When JSON parse fails, fallback dict has revision_requested=False (not a revision loop)."""
        from agents.partner.agent import Partner

        partner = Partner.__new__(Partner)
        result = partner._parse_output("not valid json at all %%")

        # Fallback: approved=False is acceptable (parse error), but revision_requested must be False
        # so the orchestrator does not enter a revision loop on a parse failure.
        assert result["revision_requested"] is False


# ── PFIX-02: _enforce_evidence_chains — disclaimer not block ──────────────────

class TestEvidenceChainDisclaimerNotBlock:
    """_enforce_evidence_chains appends disclaimer; never overrides approved or revision_requested."""

    def _run_chain_enforcement(self, finding_ids: list[str]) -> dict:
        """Call _enforce_evidence_chains with mocked classifier returning False for all chains."""
        from agents.partner.agent import Partner

        partner = Partner.__new__(Partner)

        chains = [_make_finding_chain(fid) for fid in finding_ids]
        items = [_make_evidence_item()]

        output = _make_partner_output(finding_chains=[c.model_dump() for c in chains])
        context = {
            "evidence_items": items,
            "finding_chains": [c.model_dump() for c in chains],
        }

        with patch("tools.evidence.evidence_classifier.EvidenceClassifier") as MockClassifier:
            MockClassifier.return_value.validate_finding_chain.return_value = False
            result = partner._enforce_evidence_chains(output, context)

        return result

    def test_approved_remains_true_on_chain_failure(self):
        """approved must stay True even when evidence chains fail validation."""
        result = self._run_chain_enforcement(["F-01", "F-02"])
        assert result["approved"] is True

    def test_revision_requested_remains_false_on_chain_failure(self):
        """revision_requested must stay False even when evidence chains fail."""
        result = self._run_chain_enforcement(["F-01"])
        assert result["revision_requested"] is False

    def test_disclaimer_appended_to_conditions_on_chain_failure(self):
        """A disclaimer string is appended to conditions[] when chains fail."""
        result = self._run_chain_enforcement(["F-01"])
        assert isinstance(result["conditions"], list)
        assert len(result["conditions"]) >= 1
        # Disclaimer must reference evidence or conditions
        full_text = " ".join(result["conditions"]).lower()
        assert any(kw in full_text for kw in ["evidence", "condition", "finding"])

    def test_warning_appended_to_review_notes_on_chain_failure(self):
        """review_notes must contain the evidence chain warning text."""
        result = self._run_chain_enforcement(["F-01"])
        notes = result.get("review_notes", "").lower()
        assert "evidence chain warning" in notes

    def test_no_evidence_items_is_noop(self):
        """Empty context: method returns output unchanged."""
        from agents.partner.agent import Partner

        partner = Partner.__new__(Partner)
        output = _make_partner_output()
        result = partner._enforce_evidence_chains(output, {})

        assert result["approved"] is True
        assert result["revision_requested"] is False
        assert result["conditions"] == []

    def test_no_finding_chains_is_noop(self):
        """Context with items but no finding_chains: method returns output unchanged."""
        from agents.partner.agent import Partner

        partner = Partner.__new__(Partner)
        output = _make_partner_output()
        context = {"evidence_items": [_make_evidence_item()]}
        result = partner._enforce_evidence_chains(output, context)

        assert result["approved"] is True
        assert result["revision_requested"] is False

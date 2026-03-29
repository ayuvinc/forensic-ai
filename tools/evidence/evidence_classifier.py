"""Evidence classifier — ACFE-standard permissibility classification.

Rules:
  LEAD_ONLY_TYPES: always LEAD_ONLY regardless of provenance
  Empty chain_of_custody or missing scope_authorized_by → INADMISSIBLE
  PERMISSIBLE_TYPES + documented procedure + scope_authorized_by set → PERMISSIBLE
"""

from __future__ import annotations

from schemas.documents import DocumentProvenance, PermissibilityLiteral
from schemas.evidence import EvidenceItem, FindingChain


# Evidence types that are always lead-only (cannot appear in report findings)
LEAD_ONLY_TYPES = frozenset([
    "whistleblower_tip",
    "rumour",
    "hearsay",
    "unverified_allegation",
    "anonymous_tip",
])

# Collection methods that are inherently documentary/procedural
PROCEDURAL_COLLECTION_METHODS = frozenset([
    "uploaded_by_consultant",    # documents provided by engagement client
    "system_extract",            # system-generated extract via documented procedure
    "subpoena",                  # legally obtained
    "court_order",
    "regulatory_request",
])


class EvidenceClassifier:
    """Classify evidence permissibility per ACFE standards."""

    def classify(
        self,
        evidence_type: str,
        provenance: DocumentProvenance,
    ) -> PermissibilityLiteral:
        """Determine permissibility status.

        Rules:
        1. LEAD_ONLY_TYPES → always "lead_only"
        2. Missing chain_of_custody + not procedural → "inadmissible"
        3. scope_authorized_by not set → "inadmissible"
        4. Otherwise → "permissible"
        """
        # Rule 1: Lead-only types
        if evidence_type.lower() in LEAD_ONLY_TYPES:
            return "lead_only"

        # Rule 2: Chain of custody check
        has_custody = bool(
            provenance.chain_of_custody_notes or
            provenance.collection_method in PROCEDURAL_COLLECTION_METHODS
        )
        if not has_custody:
            return "inadmissible"

        # Rule 3: Scope authorization
        if not provenance.scope_authorized_by or provenance.scope_authorized_by == "unknown":
            return "inadmissible"

        return "permissible"

    def validate_finding_chain(
        self,
        chain: FindingChain,
        evidence_items: list[EvidenceItem],
    ) -> bool:
        """Validate ACFE evidence chain for Partner approval.

        Returns True only if:
        - All supporting_evidence IDs resolve to PERMISSIBLE evidence items
        - All supporting_excerpts are non-empty (verbatim passages required)
        """
        if not chain.supporting_evidence:
            return False

        if len(chain.supporting_excerpts) < len(chain.supporting_evidence):
            return False  # Every evidence item needs a verbatim excerpt

        evidence_map = {e.evidence_id: e for e in evidence_items}

        for ev_id in chain.supporting_evidence:
            item = evidence_map.get(ev_id)
            if item is None:
                return False  # Evidence ID not found
            if item.permissibility != "permissible":
                return False  # Lead-only or inadmissible evidence in findings

        # Check all excerpts are non-empty
        if any(not excerpt.strip() for excerpt in chain.supporting_excerpts):
            return False

        return True

    def classify_batch(
        self,
        items: list[tuple[str, DocumentProvenance]],
    ) -> list[PermissibilityLiteral]:
        """Classify a list of (evidence_type, provenance) tuples."""
        return [self.classify(ev_type, prov) for ev_type, prov in items]

    def filter_permissible(self, evidence_items: list[EvidenceItem]) -> list[EvidenceItem]:
        """Return only PERMISSIBLE evidence items."""
        return [e for e in evidence_items if e.permissibility == "permissible"]

    def filter_citable(self, evidence_items: list[EvidenceItem]) -> list[EvidenceItem]:
        """Return evidence items that are report-citable (permissible + excerpt present)."""
        return [
            e for e in evidence_items
            if e.permissibility == "permissible"
            and e.usability == "report_citable"
            and e.source_excerpt.strip()
        ]

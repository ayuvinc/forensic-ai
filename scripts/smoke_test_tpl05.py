"""TPL-05 smoke test — FRM pipeline generates final_report.docx via TemplateManager.

Acceptance criteria verified:
  [AC-1] Script exits 0 (no uncaught exception)
  [AC-2] cases/{case_id}/F_Final/final_report.en.docx exists
  [AC-3] python-docx finds ≥1 paragraph whose style.name starts with 'GW_'
  [AC-4] audit_log.jsonl contains template_resolved event with fallback: false
  [AC-5] templates.json frm_risk_register.base == 'frm_risk_register_base.docx'
  [AC-6] Pre-condition: frm_risk_register_base.docx exists (skip with clear msg if absent)
  [AC-7] Error state: if template absent, pipeline falls back gracefully (no crash),
          template_resolved event has fallback: true

Run from the repo root:
    RESEARCH_MODE=knowledge_only python scripts/smoke_test_tpl05.py

Exit codes:
    0 — all ACs pass
    1 — one or more ACs failed (details printed)
    2 — pre-condition not met (template file missing); test skipped
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Ensure repo root is on sys.path regardless of where script is invoked from.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
os.chdir(_REPO_ROOT)

# ── Constants ─────────────────────────────────────────────────────────────────

TEMPLATE_DIR  = Path("firm_profile/templates")
TEMPLATES_JSON = TEMPLATE_DIR / "templates.json"
BASE_TEMPLATE = TEMPLATE_DIR / "frm_risk_register_base.docx"
CASES_DIR     = Path("cases")

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
SKIP = "\033[33mSKIP\033[0m"

_failures: list[str] = []


def _check(label: str, condition: bool, detail: str = "") -> bool:
    if condition:
        print(f"  [{PASS}] {label}")
    else:
        msg = f"  [{FAIL}] {label}" + (f": {detail}" if detail else "")
        print(msg)
        _failures.append(label)
    return condition


def _make_stub_risk_items() -> list:
    """Return a small list of RiskItem stubs — no API calls needed."""
    from schemas.artifacts import RiskItem
    items = []
    for i in range(1, 4):
        items.append(RiskItem(
            risk_id=f"M2-R{i:02d}",
            category="Financial Crime / AML Risk",
            title=f"Test Risk {i}",
            description=f"Stub description for risk {i} — TPL-05 smoke test.",
            red_flags=[],
            likelihood=3,
            likelihood_rationale="Test",
            impact=3,
            impact_rationale="Test",
            risk_rating=9,
            existing_controls=[],
            control_gaps=[],
            recommendations=["Implement control"],
            regulatory_references=[],
            framework_references=["COSO 2013"],
        ))
    return items


def _make_stub_intake(case_id: str) -> object:
    from schemas.case import CaseIntake
    return CaseIntake(
        case_id=case_id,
        client_name="TPL-05 Test Client",
        industry="Financial Services",
        primary_jurisdiction="UAE",
        workflow="frm_risk_register",
        description="Smoke test case — not a real engagement.",
        language="en",
        created_at=datetime.now(timezone.utc),
    )


def _setup_af_case(case_id: str) -> Path:
    """Create the A-F folder structure expected by is_af_project()."""
    cdir = CASES_DIR / case_id
    for folder in ("A_Engagement_Management", "B_Planning", "C_Evidence",
                   "D_Working_Papers", "E_Drafts", "F_Final"):
        (cdir / folder).mkdir(parents=True, exist_ok=True)
    return cdir


def _run_ac6_precheck() -> bool:
    """AC-6: template file must exist before the run."""
    if not BASE_TEMPLATE.exists():
        print(f"\n  [{SKIP}] AC-6 pre-condition: {BASE_TEMPLATE} not found")
        print("  Add the template file and re-run. Test skipped with exit code 2.")
        sys.exit(2)
    print(f"  [{PASS}] AC-6 pre-condition: {BASE_TEMPLATE} exists")
    return True


def run_happy_path() -> str:
    """Happy path: run frm_finalize with template present. Returns case_id."""
    from workflows.frm_risk_register import run_frm_finalize

    case_id = f"tpl05-{uuid.uuid4().hex[:6].upper()}"
    _setup_af_case(case_id)

    intake = _make_stub_intake(case_id)
    risk_items = _make_stub_risk_items()
    exec_summary = "TPL-05 smoke test executive summary."
    completed_modules = [2]

    run_frm_finalize(intake, risk_items, [], completed_modules, exec_summary,
                     context={"ai_review_enabled": False})
    return case_id


def run_fallback_path() -> str:
    """Fallback path: temporarily rename base template, verify graceful fallback."""
    from workflows.frm_risk_register import run_frm_finalize

    case_id = f"tpl05-fb-{uuid.uuid4().hex[:6].upper()}"
    _setup_af_case(case_id)

    tmp_name = BASE_TEMPLATE.with_suffix(".docx.bak")
    shutil.move(str(BASE_TEMPLATE), str(tmp_name))
    try:
        intake = _make_stub_intake(case_id)
        risk_items = _make_stub_risk_items()
        run_frm_finalize(intake, risk_items, [], [2], "Fallback test.",
                         context={"ai_review_enabled": False})
    finally:
        shutil.move(str(tmp_name), str(BASE_TEMPLATE))

    return case_id


def verify_happy_path(case_id: str) -> None:
    print("\nHappy-path checks:")

    # AC-2: docx exists
    docx_path = CASES_DIR / case_id / "F_Final" / "final_report.en.docx"
    _check("AC-2: final_report.en.docx exists in F_Final/", docx_path.exists(),
           str(docx_path))

    # AC-3: at least one GW_ style paragraph
    if docx_path.exists():
        from docx import Document
        doc = Document(str(docx_path))
        gw_paras = [p for p in doc.paragraphs if p.style.name.startswith("GW_")]
        _check("AC-3: ≥1 paragraph with GW_ style in output docx",
               len(gw_paras) >= 1,
               f"found {len(gw_paras)} GW_ paragraphs")

    # AC-4: template_resolved event with fallback: false
    audit_log = CASES_DIR / case_id / "audit_log.jsonl"
    if audit_log.exists():
        events = [json.loads(line) for line in audit_log.read_text().splitlines() if line.strip()]
        tpl_events = [e for e in events if e.get("event") == "template_resolved"]
        if _check("AC-4: template_resolved event present in audit_log.jsonl",
                  len(tpl_events) >= 1,
                  f"found {len(tpl_events)} template_resolved events"):
            ev = tpl_events[0]
            _check("AC-4: template_resolved.fallback == false",
                   ev.get("fallback") is False,
                   f"got fallback={ev.get('fallback')!r}")
    else:
        _check("AC-4: audit_log.jsonl exists", False, str(audit_log))

    # AC-5: templates.json mapping
    if TEMPLATES_JSON.exists():
        registry = json.loads(TEMPLATES_JSON.read_text())
        entry = registry.get("frm_risk_register", {})
        _check("AC-5: templates.json frm_risk_register.base == frm_risk_register_base.docx",
               entry.get("base") == "frm_risk_register_base.docx",
               f"got base={entry.get('base')!r}")
    else:
        _check("AC-5: templates.json exists", False, str(TEMPLATES_JSON))


def verify_fallback_path(case_id: str) -> None:
    print("\nFallback-path checks (AC-7):")

    # Pipeline must not have crashed (case_id folder exists with audit log)
    audit_log = CASES_DIR / case_id / "audit_log.jsonl"
    _check("AC-7: pipeline completed without crash (audit_log written)",
           audit_log.exists())

    if audit_log.exists():
        events = [json.loads(line) for line in audit_log.read_text().splitlines() if line.strip()]
        tpl_events = [e for e in events if e.get("event") == "template_resolved"]
        if _check("AC-7: template_resolved event present when template absent",
                  len(tpl_events) >= 1):
            ev = tpl_events[0]
            _check("AC-7: template_resolved.fallback == true when template absent",
                   ev.get("fallback") is True,
                   f"got fallback={ev.get('fallback')!r}")


def cleanup(case_id: str) -> None:
    """Remove the test case folder to keep cases/ clean."""
    cdir = CASES_DIR / case_id
    if cdir.exists():
        shutil.rmtree(cdir)


if __name__ == "__main__":
    print("=== TPL-05 Smoke Test ===\n")

    # AC-6 pre-condition check
    _run_ac6_precheck()

    # AC-1: happy path runs without exception
    print("\nRunning happy path...")
    happy_case_id = None
    try:
        happy_case_id = run_happy_path()
        print(f"  [{PASS}] AC-1: run_frm_finalize completed without exception")
    except Exception as exc:
        print(f"  [{FAIL}] AC-1: run_frm_finalize raised: {exc}")
        _failures.append("AC-1")

    if happy_case_id:
        verify_happy_path(happy_case_id)

    # AC-7: fallback path
    print("\nRunning fallback path (template temporarily renamed)...")
    fb_case_id = None
    try:
        fb_case_id = run_fallback_path()
        print(f"  [{PASS}] AC-7: fallback path completed without exception")
    except Exception as exc:
        print(f"  [{FAIL}] AC-7: fallback path raised: {exc}")
        _failures.append("AC-7 exception")

    if fb_case_id:
        verify_fallback_path(fb_case_id)

    # Cleanup test cases
    if happy_case_id:
        cleanup(happy_case_id)
    if fb_case_id:
        cleanup(fb_case_id)

    # Final summary
    print("\n" + "=" * 40)
    if _failures:
        print(f"RESULT: {len(_failures)} AC(s) FAILED — {_failures}")
        sys.exit(1)
    else:
        print("RESULT: ALL ACs PASSED")
        sys.exit(0)

"""
Future-direction simulation runner.

Extends Phase 1 + Phase 2 findings with Monte Carlo and conflict analysis of
planned features from Sprint-IA-01/02, product-packaging.md, ba-logic.md,
and docs/hld.md.

Produces:
  simulation/reports/future_sim_report_{timestamp}.md — future-direction results only
  simulation/reports/combined_remediation_{timestamp}.md — unified priority matrix
    covering Phase 1 (current defects) + Phase 2 (empirical confirmed) + Phase 3 (future risks)

Updates tasks/todo.md Sprint-SIM block with new FUT-N tickets.

Usage:
    cd ~/forensic-ai
    python3 simulation/run_future.py
"""
from __future__ import annotations

import sys
import os
import time
import random
import json
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from simulation.harness_future import (
    run_future_workflow_simulation,
    FUTURE_WORKFLOW_REGISTRY,
    FutureFailureMode,
    FUTURE_UNCERTAINTY_DELTA,
)
from simulation.conflict_detector_future import (
    run_future_conflict_detection,
    FutureConflictFinding,
)
from simulation.harness import SimReport, FailureMode

REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

N_FUTURE_RUNS = 500
RANDOM_SEED   = 42


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _bar(v: float, width: int = 10) -> str:
    filled = round(v * width)
    return "█" * filled + "░" * (width - filled)


def _risk_score(success_rate: float, workflow_type: str) -> str:
    """Convert success rate + workflow type to risk label."""
    if workflow_type == "pipeline":
        if success_rate < 0.50:
            return "CRITICAL"
        elif success_rate < 0.65:
            return "HIGH"
        elif success_rate < 0.80:
            return "MEDIUM"
        else:
            return "LOW"
    else:
        if success_rate < 0.70:
            return "HIGH"
        elif success_rate < 0.85:
            return "MEDIUM"
        else:
            return "LOW"


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_future_mc_section(reports: list[SimReport]) -> str:
    lines = [
        "## 1. Future-Direction Monte Carlo Results\n",
        f"*{N_FUTURE_RUNS} runs per planned workflow — parametric with {FUTURE_UNCERTAINTY_DELTA:.0%} uncertainty delta*\n",
        "*All probabilities are estimates from design documents — no implementation exists yet.*\n",
        "| Workflow | Type | Success Rate | Risk | Top Failure Mode | Notes |",
        "|----------|------|-------------|------|-----------------|-------|",
    ]

    for r in sorted(reports, key=lambda x: x.success_rate):
        wf_clean = r.workflow.replace("[FUTURE] ", "")
        top_fm = r.top_failure_modes[0][0] if r.top_failure_modes else "—"
        risk = _risk_score(r.success_rate, r.workflow_type)
        risk_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk, "")
        lines.append(
            f"| {wf_clean} | {r.workflow_type} | {_pct(r.success_rate)} {_bar(r.success_rate)} "
            f"| {risk_icon} {risk} | {top_fm} | uncertainty +{FUTURE_UNCERTAINTY_DELTA:.0%} |"
        )

    lines.append("\n### Failure breakdown (top 3 per future workflow)\n")
    for r in sorted(reports, key=lambda x: x.success_rate):
        wf_clean = r.workflow.replace("[FUTURE] ", "")
        if r.top_failure_modes:
            risk = _risk_score(r.success_rate, r.workflow_type)
            lines.append(f"**{wf_clean}** (success {_pct(r.success_rate)} — {risk})")
            for fm, cnt in r.top_failure_modes[:3]:
                lines.append(f"  - `{fm}`: {cnt}/{r.n_runs} ({cnt/r.n_runs*100:.1f}%)")
            if r.input_sensitivity:
                top_input = sorted(r.input_sensitivity.items(), key=lambda x: -x[1])[:2]
                lines.append(f"  - Input sensitivity: " +
                              ", ".join(f"{k}={v:.3f}" for k, v in top_input))
            lines.append("")

    return "\n".join(lines)


def _render_future_conflicts_section(conflicts: dict[str, list[FutureConflictFinding]]) -> str:
    lines = ["## 2. Future-Direction Conflict Analysis\n"]

    all_findings: list[FutureConflictFinding] = []
    for v in conflicts.values():
        all_findings.extend(v)

    high   = [f for f in all_findings if f.severity == "HIGH"]
    medium = [f for f in all_findings if f.severity == "MEDIUM"]
    low    = [f for f in all_findings if f.severity == "LOW"]
    info   = [f for f in all_findings if f.severity == "INFO"]

    lines.append(f"**Summary:** {len(high)} HIGH, {len(medium)} MEDIUM, "
                 f"{len(low)} LOW, {len(info)} INFO\n")

    for sev, group in [("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
        if not group:
            continue
        icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "")
        lines.append(f"### {icon} {sev}\n")
        for f in group:
            lines.append(f"**[{f.area}]** {f.description}")
            if f.affected_files:
                lines.append(f"  - Files: {', '.join(f.affected_files[:4])}")
            lines.append(f"  - Fix: {f.recommendation}")
            if f.sprint_ref:
                lines.append(f"  - Sprint ref: `{f.sprint_ref}`")
            lines.append("")

    return "\n".join(lines)


def _render_combined_remediation(
    future_reports: list[SimReport],
    future_conflicts: dict[str, list[FutureConflictFinding]],
) -> tuple[str, list[dict]]:
    """
    Produces a unified remediation plan covering:
      - Confirmed Phase 2 empirical findings (hardcoded from empirical_report)
      - Future-direction MC findings (from this run)
      - Future conflict analysis

    Returns (markdown_section, tickets_list).
    """
    lines = [
        "## 3. Unified Remediation Plan\n",
        "*Ordered by: severity × proximity to shipping × implementation effort*\n",
        "*P1 = ship-blocking | P2 = next sprint | P3 = before scale | P4 = post-MVP*\n",
        "| ID | Priority | Area | Description | Effort | Sprint |",
        "|----|----------|------|-------------|--------|--------|",
    ]

    tickets: list[dict] = []
    ticket_id = 1

    def add(priority: str, area: str, desc: str, effort: str, sprint: str) -> None:
        nonlocal ticket_id
        tickets.append({
            "id": f"FUT-{ticket_id:02d}",
            "priority": priority,
            "area": area,
            "desc": desc,
            "effort": effort,
            "sprint": sprint,
        })
        ticket_id += 1

    # ── CONFIRMED EMPIRICAL (Phase 2 — hardcoded from empirical_report) ──────
    add("P1", "pii",
        "Add UAE IBAN regex to sanitize_pii (AE07... pattern confirmed bypassed)",
        "S", "Sprint-SIM")
    add("P1", "pii",
        "Strip null bytes (\\x00..\\x02) from free-text fields in sanitize_pii",
        "S", "Sprint-SIM")
    add("P1", "schema",
        "Add ge=1, le=5 validators to RiskItem.likelihood and RiskItem.impact — "
        "0 and 6 both accepted by Pydantic today",
        "S", "Sprint-SIM")
    add("P1", "orchestrator",
        "Thread pm_feedback into Junior context on revision runs — "
        "confirmed missing: feedback_in_context=None on E3.2",
        "M", "Sprint-SIM")
    add("P2", "schema",
        "Add min_length=1 to JuniorDraft.findings list — empty findings accepted today",
        "S", "Sprint-SIM")
    add("P2", "orchestrator",
        "Add Partner→PM feedback recovery path — Partner rejection is currently a "
        "terminal dead-end (SIM-04 confirmed)",
        "L", "Sprint-SIM")
    add("P2", "hook",
        "Investigate enforce_evidence_chain context key mismatch — "
        "E2.2 shows 0/6 cases blocked; hook may not fire on real payload structure (SIM-01 PARTIAL)",
        "M", "Sprint-SIM")
    add("P3", "orchestrator",
        "Fix E3.5 CaseState.last_updated required field — resume from checkpoint fails "
        "with validation error",
        "S", "Sprint-SIM")

    # ── FUTURE MC: CRITICAL (success_rate < 50%) ─────────────────────────────
    for r in sorted(future_reports, key=lambda x: x.success_rate):
        wf_clean = r.workflow.replace("[FUTURE] ", "")
        risk = _risk_score(r.success_rate, r.workflow_type)
        if risk == "CRITICAL":
            top_fm = r.top_failure_modes[0][0] if r.top_failure_modes else "N/A"
            add("P1", "future_workflow",
                f"{wf_clean}: CRITICAL — success_rate={_pct(r.success_rate)}, "
                f"top failure={top_fm}",
                "L", "Sprint-IA-01/02")

    # ── FUTURE MC: HIGH ───────────────────────────────────────────────────────
    for r in sorted(future_reports, key=lambda x: x.success_rate):
        wf_clean = r.workflow.replace("[FUTURE] ", "")
        risk = _risk_score(r.success_rate, r.workflow_type)
        if risk == "HIGH":
            top_fm = r.top_failure_modes[0][0] if r.top_failure_modes else "N/A"
            add("P2", "future_workflow",
                f"{wf_clean}: HIGH — success_rate={_pct(r.success_rate)}, "
                f"top failure={top_fm}",
                "M", "Sprint-IA-01/02")

    # ── FUTURE CONFLICT: HIGH ─────────────────────────────────────────────────
    for check_findings in future_conflicts.values():
        for f in check_findings:
            if f.severity == "HIGH":
                add("P1" if f.area in ("bootstrap", "pii", "locking") else "P2",
                    f.area,
                    f.description[:120],
                    "M", f.sprint_ref or "Sprint-IA-01/02")

    # ── FUTURE CONFLICT: MEDIUM ───────────────────────────────────────────────
    for check_findings in future_conflicts.values():
        for f in check_findings:
            if f.severity == "MEDIUM":
                add("P3", f.area, f.description[:120], "S",
                    f.sprint_ref or "Sprint-IA-01/02")

    # ── FUTURE-SPECIFIC DESIGN REQUIREMENTS (from 15 identified risks) ────────
    add("P2", "future_design",
        "evidence_chat_session: cap CEM context at 50 turns with explicit truncation warning "
        "(CEM_CONTEXT_CHARS=16,000 confirmed limit; CONTEXT_WINDOW_EXHAUSTED at 14%)",
        "S", "Sprint-IA-02 (CEM)")
    add("P2", "future_design",
        "workpaper_promotion: require audit_log.jsonl to exist before promotion — "
        "surface friendly error on missing log; auto-init if parent dir exists",
        "S", "Sprint-IA-01")
    add("P2", "future_design",
        "knowledge_harvester: implement PII filter (client names, case IDs, financial amounts) "
        "as a mandatory pre-write gate before patterns enter shared knowledge library",
        "M", "Sprint-IA-02 (future)")
    add("P3", "future_design",
        "multi_tenant_workstream + co_work_session: add filelock advisory locking on state.json "
        "and audit_log.jsonl before Co-Work or SaaS shipping models are enabled",
        "M", "Sprint-IA-02 (co-work)")
    add("P3", "future_design",
        "Prefix artifact filenames with workflow slug to prevent multi-workstream collision: "
        "{workflow}_{agent}_output.v{N}.json",
        "S", "Sprint-IA-01 IA-03")
    add("P4", "future_design",
        "frm_guided_exercise: define auto-baseline behaviour for 0-document intake "
        "(auto-fill fires at 11% — should be explicit user opt-in, not silent)",
        "S", "Sprint-IA-02 (FRM guided)")

    for t in tickets:
        lines.append(
            f"| {t['id']} | {t['priority']} | {t['area']} | {t['desc'][:110]} | {t['effort']} | {t['sprint']} |"
        )

    return "\n".join(lines), tickets


# ---------------------------------------------------------------------------
# Write FUT-N tickets to tasks/todo.md
# ---------------------------------------------------------------------------

def _write_future_tickets_to_todo(tickets: list[dict]) -> None:
    todo_path = _ROOT / "tasks" / "todo.md"
    if not todo_path.exists():
        return

    high_priority = [t for t in tickets if t["priority"] in ("P1", "P2")]
    if not high_priority:
        return

    block = "\n## Sprint-FUT (Future-Direction Simulation Findings — auto-generated)\n\n"
    block += "| ID | Priority | Area | Description | Effort | Sprint | Status |\n"
    block += "|----|----------|------|-------------|--------|--------|--------|\n"
    for t in high_priority:
        block += (f"| {t['id']} | {t['priority']} | {t['area']} | "
                  f"{t['desc'][:100]} | {t['effort']} | {t['sprint']} | OPEN |\n")

    import re
    existing = todo_path.read_text(errors="ignore")
    if "Sprint-FUT" in existing:
        existing = re.sub(
            r"## Sprint-FUT.*?(?=\n## |\Z)", block.strip(), existing, flags=re.DOTALL
        )
        todo_path.write_text(existing)
    else:
        with todo_path.open("a") as fh:
            fh.write("\n" + block)

    print(f"  ✓ {len(high_priority)} FUT tickets written to tasks/todo.md")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    future_report_path   = REPORTS_DIR / f"future_sim_report_{ts}.md"
    combined_report_path = REPORTS_DIR / f"combined_remediation_{ts}.md"

    print("=" * 62)
    print("  Forensic-AI Future-Direction Simulation Suite")
    print(f"  {ts}")
    print("=" * 62)
    print(f"\n  Workflows: {len(FUTURE_WORKFLOW_REGISTRY)}")
    print(f"  Uncertainty delta: +{FUTURE_UNCERTAINTY_DELTA:.0%} per probability (unbuilt code)")

    # Phase 1: Future-direction MC
    print(f"\n[Phase 1] Monte Carlo — {N_FUTURE_RUNS} runs × {len(FUTURE_WORKFLOW_REGISTRY)} future workflows")
    t0 = time.time()
    random.seed(RANDOM_SEED)
    future_reports: list[SimReport] = []
    for wf in sorted(FUTURE_WORKFLOW_REGISTRY.keys()):
        report = run_future_workflow_simulation(wf, n=N_FUTURE_RUNS, seed=RANDOM_SEED)
        future_reports.append(report)
        risk = _risk_score(report.success_rate, report.workflow_type)
        icon = {"CRITICAL": "✗✗", "HIGH": "✗", "MEDIUM": "⚠", "LOW": "✓"}.get(risk, "?")
        print(f"  {icon} {wf:<30} success={_pct(report.success_rate):>7}  {risk}")
    print(f"  Done in {time.time()-t0:.2f}s")

    # Phase 2: Future conflict detection
    print("\n[Phase 2] Future-Direction Conflict Detection")
    t0 = time.time()
    future_conflicts = run_future_conflict_detection()
    high_count = sum(
        len([f for f in v if f.severity == "HIGH"])
        for v in future_conflicts.values()
    )
    medium_count = sum(
        len([f for f in v if f.severity == "MEDIUM"])
        for v in future_conflicts.values()
    )
    total = sum(len(v) for v in future_conflicts.values())
    print(f"  ✓ {total} checks — HIGH={high_count}, MEDIUM={medium_count}")
    print(f"  Done in {time.time()-t0:.2f}s")

    # Phase 3: Render future-only report
    print(f"\n[Phase 3] Rendering future report → {future_report_path.name}")
    mc_section        = _render_future_mc_section(future_reports)
    conflicts_section = _render_future_conflicts_section(future_conflicts)
    remediation_section, tickets = _render_combined_remediation(future_reports, future_conflicts)

    future_text = f"""# Forensic-AI Future-Direction Simulation Report

**Generated:** {ts}
**Seed:** {RANDOM_SEED}
**Monte Carlo:** {N_FUTURE_RUNS} runs × {len(FUTURE_WORKFLOW_REGISTRY)} future workflows
**Uncertainty delta:** +{FUTURE_UNCERTAINTY_DELTA:.0%} on all base probabilities (no empirical baseline)
**Source documents:** docs/hld.md, docs/lld/product-ia-design.md, docs/product-packaging.md,
  tasks/ba-logic.md, tasks/todo.md (Sprint-IA-01)

**Note on methodology:** Future workflows are UNBUILT. Probabilities are derived from design
documents, known analogous patterns in existing code, and constraint analysis. The +5%
uncertainty delta represents the epistemic gap between design intent and implementation reality.
Treat all percentages as directional, not predictive.

---

{mc_section}

---

{conflicts_section}

---

{remediation_section}

---

*Future simulation: simulation/harness_future.py | conflict_detector_future.py | run_future.py*
*Source analysis: docs/hld.md | docs/lld/product-ia-design.md | docs/product-packaging.md | tasks/ba-logic.md*
"""

    future_report_path.write_text(future_text, encoding="utf-8")
    print(f"  ✓ Future report written ({future_report_path.stat().st_size // 1024} KB)")

    # Phase 4: Combined remediation report
    print(f"\n[Phase 4] Rendering combined remediation → {combined_report_path.name}")

    # Count empirical confirmed (from Phase 2 — hardcoded as first 8 tickets)
    phase2_tickets = [t for t in tickets if t.get("sprint") == "Sprint-SIM"]
    future_tickets = [t for t in tickets if t.get("sprint") != "Sprint-SIM"]

    combined_text = f"""# Forensic-AI Combined Remediation Plan

**Generated:** {ts}
**Covers:**
  - Phase 1: Parametric Monte Carlo (11 workflows, 9,500 runs) — sim_report_*.md
  - Phase 2: Empirical execution (hooks, orchestrator, state machine, schemas) — empirical_report_*.md
  - Phase 3: Future-direction simulation ({len(FUTURE_WORKFLOW_REGISTRY)} planned workflows) — this file

**Total action items:** {len(tickets)} ({len(phase2_tickets)} confirmed current defects, {len(future_tickets)} future-direction risks)

---

## Executive Summary

### Current codebase — confirmed defects (Phase 2 empirical)
| Severity | Count | Top issues |
|----------|-------|-----------|
| P1 (ship-blocking) | {len([t for t in phase2_tickets if t['priority']=='P1'])} | IBAN PII bypass, RiskItem range validation, PM feedback threading |
| P2 (next sprint) | {len([t for t in phase2_tickets if t['priority']=='P2'])} | JuniorDraft empty findings, Partner recovery path, evidence chain mismatch |
| P3 (before scale) | {len([t for t in phase2_tickets if t['priority']=='P3'])} | CaseState last_updated checkpoint fix |

### Future direction — highest risks
| Workflow | Success Rate | Top Risk |
|----------|-------------|---------|
{chr(10).join(f"| {r.workflow.replace('[FUTURE] ', '')} | {_pct(r.success_rate)} | {r.top_failure_modes[0][0] if r.top_failure_modes else '—'} |" for r in sorted(future_reports, key=lambda x: x.success_rate)[:5])}

### Conflict analysis — highest priority gaps
{chr(10).join(f"- **{f.area}**: {f.description[:100]}" for v in future_conflicts.values() for f in v if f.severity == "HIGH")}

---

{remediation_section}

---

## Priority 1 — Ship-blocking (fix before any external user sees this)

{chr(10).join(f"### {t['id']}: [{t['area']}] {t['desc']}" for t in tickets if t['priority'] == 'P1')}

---

## Priority 2 — Next sprint

{chr(10).join(f"### {t['id']}: [{t['area']}] {t['desc']}" for t in tickets if t['priority'] == 'P2')}

---

## Priority 3 — Before scale

{chr(10).join(f"### {t['id']}: [{t['area']}] {t['desc']}" for t in tickets if t['priority'] == 'P3')}

---

## Priority 4 — Post-MVP

{chr(10).join(f"### {t['id']}: [{t['area']}] {t['desc']}" for t in tickets if t['priority'] == 'P4')}

---

*Combined analysis: simulation/run_future.py*
*Phase 1 report: simulation/reports/sim_report_*.md*
*Phase 2 report: simulation/reports/empirical_report_*.md*
*Phase 3 report: simulation/reports/future_sim_report_{ts}.md*
"""

    combined_report_path.write_text(combined_text, encoding="utf-8")
    print(f"  ✓ Combined remediation written ({combined_report_path.stat().st_size // 1024} KB)")

    # Write to todo.md
    _write_future_tickets_to_todo(tickets)

    print(f"\n{'='*62}")
    print(f"  SUMMARY")
    print(f"{'='*62}")
    worst_future = min(future_reports, key=lambda x: x.success_rate)
    best_future  = max(future_reports, key=lambda x: x.success_rate)
    wf_worst = worst_future.workflow.replace("[FUTURE] ", "")
    wf_best  = best_future.workflow.replace("[FUTURE] ", "")
    print(f"  Most at-risk future workflow:  {wf_worst} ({_pct(worst_future.success_rate)})")
    print(f"  Most stable future workflow:   {wf_best} ({_pct(best_future.success_rate)})")
    print(f"  Future conflict HIGH findings: {high_count}")
    print(f"  Total remediation tickets:     {len(tickets)}")
    print(f"  P1 (ship-blocking):            {len([t for t in tickets if t['priority']=='P1'])}")
    print(f"  P2 (next sprint):              {len([t for t in tickets if t['priority']=='P2'])}")
    print(f"  P3 (before scale):             {len([t for t in tickets if t['priority']=='P3'])}")
    print(f"  Future sim report:  {future_report_path}")
    print(f"  Combined remediation: {combined_report_path}")
    print()


if __name__ == "__main__":
    main()

"""
Main simulation runner.

Usage:
    cd ~/forensic-ai
    python simulation/run_all.py

Produces: simulation/reports/sim_report_{timestamp}.md
Also appends SIM-N tickets to tasks/todo.md (severity >= MEDIUM).
"""
from __future__ import annotations

import sys
import os
import time
import random
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from simulation.harness import run_workflow_simulation, WORKFLOW_REGISTRY, SimReport
from simulation.game_theory import run_all_scenarios, ScenarioResult
from simulation.input_fuzzer import run_fuzz_analysis, summarise_fuzz
from simulation.conflict_detector import run_conflict_detection, ConflictFinding

REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

N_MC_RUNS   = 500   # per workflow — statistically sufficient for P>0.01 at 95% CI
N_GT_RUNS   = 1000  # per game-theory scenario
RANDOM_SEED = 42


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _bar(v: float, width: int = 20) -> str:
    filled = round(v * width)
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_mc_section(reports: list[SimReport]) -> str:
    lines = ["## 1. Monte Carlo Results\n",
             f"*{N_MC_RUNS} runs per workflow — parametric simulation, no API calls*\n",
             "| Workflow | Type | Success Rate | Top Failure Mode | "
             "P50 jr_rounds | P95 jr_rounds | KO vs Live delta |",
             "|----------|------|-------------|-----------------|"
             "--------------|--------------|-----------------|"]

    for r in sorted(reports, key=lambda x: x.success_rate):
        top_fm = r.top_failure_modes[0][0] if r.top_failure_modes else "—"
        ko = r.mode_delta.get("knowledge_only_success", 0)
        live = r.mode_delta.get("live_success", 0)
        delta = f"{(ko - live)*100:+.1f}pp"
        lines.append(
            f"| {r.workflow} | {r.workflow_type} | {_pct(r.success_rate)} {_bar(r.success_rate, 10)} "
            f"| {top_fm} | {r.p50_junior_rounds:.1f} | {r.p95_junior_rounds:.1f} | {delta} |"
        )

    lines.append("\n### Failure mode breakdown per workflow\n")
    for r in sorted(reports, key=lambda x: x.success_rate):
        if r.top_failure_modes:
            lines.append(f"**{r.workflow}** (success {_pct(r.success_rate)})")
            for fm, cnt in r.top_failure_modes:
                lines.append(f"  - {fm}: {cnt}/{r.n_runs} ({cnt/r.n_runs*100:.1f}%)")
            if r.input_sensitivity:
                top_input = sorted(r.input_sensitivity.items(), key=lambda x: -x[1])[:3]
                lines.append(f"  - Top input sensitivity: " +
                              ", ".join(f"{k}={v:.3f}" for k, v in top_input))
            lines.append("")

    return "\n".join(lines)


def _render_gt_section(scenarios: list[ScenarioResult]) -> str:
    lines = ["## 2. Game Theory Findings\n",
             f"*{N_GT_RUNS} simulated games per scenario*\n"]

    for s in scenarios:
        lines.append(f"### {s.scenario}\n")
        if s.nash_pm_threshold is not None:
            lines.append(f"- Nash PM threshold: **{s.nash_pm_threshold}**")
        if s.nash_partner_threshold is not None:
            lines.append(f"- Nash Partner threshold: **{s.nash_partner_threshold}**")
        lines.append(f"- Avg total payoff: {s.avg_total_payoff:.3f}")
        lines.append(f"- Avg Junior revision rounds: {s.avg_junior_rounds:.2f} "
                     f"(P95: {s.p95_junior_rounds:.1f})")
        lines.append("\n**Terminal distribution:**")
        for k, v in sorted(s.terminal_distribution.items(), key=lambda x: -x[1]):
            lines.append(f"  - {k}: {v}/{s.n_runs} ({v/s.n_runs*100:.1f}%)")
        lines.append("\n**Notes:**")
        for note in s.notes:
            lines.append(f"  - {note}")
        lines.append("")

    return "\n".join(lines)


def _render_fuzz_section(summary: dict, results) -> str:
    lines = ["## 3. Input Boundary / Fuzz Findings\n",
             f"*{summary['total_tests']} test cases across {len(set(r.field for r in results))} input fields*\n",
             "| Outcome | Count |",
             "|---------|-------|"]

    for outcome, cnt in sorted(summary["by_outcome"].items(), key=lambda x: -x[1]):
        lines.append(f"| {outcome} | {cnt} |")

    lines.append(f"\n**Severity summary:** HIGH={summary['high_severity_findings']}, "
                 f"MEDIUM={summary['medium_severity_findings']}\n")

    high_unblocked = summary.get("unblocked_high", [])
    if high_unblocked:
        lines.append("### HIGH severity findings (not blocked before backend)\n")
        for item in high_unblocked:
            lines.append(f"- {item}")
        lines.append("")

    pii_passed = summary.get("pii_passed_through", [])
    if pii_passed:
        lines.append("### PII passed through sanitize_pii without stripping\n")
        for item in pii_passed:
            lines.append(f"- `{item}`")
        lines.append("")

    lines.append("### All fuzz results by severity\n")
    for sev in ["HIGH", "MEDIUM", "LOW"]:
        sev_results = [r for r in results if r.severity == sev]
        if sev_results:
            lines.append(f"**{sev}**")
            for r in sev_results:
                icon = "🔴" if sev == "HIGH" else ("🟡" if sev == "MEDIUM" else "🟢")
                lines.append(f"- {icon} `{r.field}` / `{r.fuzz_class}`: "
                              f"outcome={r.outcome} — {r.detail}")
            lines.append("")

    return "\n".join(lines)


def _render_conflict_section(conflicts: dict[str, list[ConflictFinding]]) -> str:
    lines = ["## 4. Cross-Workflow Conflict Findings\n"]

    all_findings: list[ConflictFinding] = []
    for check_findings in conflicts.values():
        all_findings.extend(check_findings)

    high   = [f for f in all_findings if f.severity == "HIGH"   and f.check != "INFO"]
    medium = [f for f in all_findings if f.severity == "MEDIUM" and f.check != "INFO"]
    low    = [f for f in all_findings if f.severity == "LOW"]
    info   = [f for f in all_findings if f.severity == "INFO"]

    lines.append(f"**Summary:** {len(high)} HIGH, {len(medium)} MEDIUM, "
                 f"{len(low)} LOW, {len(info)} INFO\n")

    for sev, group in [("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
        if not group:
            continue
        lines.append(f"### {sev} severity\n")
        for f in group:
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "ℹ️")
            lines.append(f"**{icon} [{f.check}]** {f.description}")
            if f.affected_files:
                lines.append(f"  - Files: {', '.join(f.affected_files)}")
            lines.append(f"  - Fix: {f.recommendation}")
            lines.append("")

    return "\n".join(lines)


def _render_priority_matrix(
    mc_reports: list[SimReport],
    gt_scenarios: list[ScenarioResult],
    fuzz_summary: dict,
    conflicts: dict,
) -> str:
    lines = ["## 5. Resolution Priority Matrix\n",
             "| ID | Source | Severity | Description | Effort |",
             "|----|--------|----------|-------------|--------|"]

    ticket_id = 1
    tickets: list[dict] = []

    # From MC: workflows with success_rate < 0.75
    for r in sorted(mc_reports, key=lambda x: x.success_rate):
        if r.success_rate < 0.75:
            tickets.append({
                "id": f"SIM-{ticket_id:02d}",
                "source": "Monte Carlo",
                "severity": "HIGH" if r.success_rate < 0.60 else "MEDIUM",
                "desc": f"{r.workflow}: success_rate={_pct(r.success_rate)}, "
                        f"top failure={r.top_failure_modes[0][0] if r.top_failure_modes else 'N/A'}",
                "effort": "M",
            })
            ticket_id += 1

    # From Game Theory: PARTNER_REJECTED > 5%
    for s in gt_scenarios:
        pr = s.terminal_distribution.get("PARTNER_REJECTED", 0) / s.n_runs
        if pr > 0.05:
            tickets.append({
                "id": f"SIM-{ticket_id:02d}",
                "source": "Game Theory",
                "severity": "HIGH",
                "desc": f"{s.scenario}: Partner rejection rate {pr:.1%} — no recovery path (PipelineError)",
                "effort": "L",
            })
            ticket_id += 1
        rl = s.terminal_distribution.get("REVISION_LIMIT", 0) / s.n_runs
        if rl > 0.10:
            tickets.append({
                "id": f"SIM-{ticket_id:02d}",
                "source": "Game Theory",
                "severity": "MEDIUM",
                "desc": f"{s.scenario}: RevisionLimitError rate {rl:.1%} — limits may be too tight",
                "effort": "S",
            })
            ticket_id += 1

    # From Fuzz: HIGH severity unblocked
    for item in fuzz_summary.get("unblocked_high", []):
        tickets.append({
            "id": f"SIM-{ticket_id:02d}",
            "source": "Fuzz",
            "severity": "HIGH",
            "desc": item,
            "effort": "S",
        })
        ticket_id += 1

    # From Conflict detection: HIGH and MEDIUM
    for check_findings in conflicts.values():
        for f in check_findings:
            if f.severity in ("HIGH", "MEDIUM") and f.description:
                tickets.append({
                    "id": f"SIM-{ticket_id:02d}",
                    "source": f"Conflict/{f.check}",
                    "severity": f.severity,
                    "desc": f.description[:120],
                    "effort": "S" if f.severity == "MEDIUM" else "M",
                })
                ticket_id += 1

    for t in tickets:
        lines.append(f"| {t['id']} | {t['source']} | {t['severity']} | {t['desc'][:100]} | {t['effort']} |")

    return "\n".join(lines), tickets


# ---------------------------------------------------------------------------
# Write tickets to tasks/todo.md
# ---------------------------------------------------------------------------

def _write_tickets_to_todo(tickets: list[dict]) -> None:
    todo_path = _ROOT / "tasks" / "todo.md"
    if not todo_path.exists():
        return

    medium_up = [t for t in tickets if t["severity"] in ("HIGH", "MEDIUM")]
    if not medium_up:
        return

    block = "\n## Sprint-SIM (Simulation Findings — auto-generated)\n\n"
    block += "| ID | Severity | Source | Description | Effort | Status |\n"
    block += "|----|----------|--------|-------------|--------|--------|\n"
    for t in medium_up:
        block += f"| {t['id']} | {t['severity']} | {t['source']} | {t['desc'][:100]} | {t['effort']} | OPEN |\n"

    existing = todo_path.read_text(errors="ignore")
    if "Sprint-SIM" in existing:
        # Replace existing block
        import re
        existing = re.sub(
            r"## Sprint-SIM.*?(?=\n## |\Z)", block.strip(), existing, flags=re.DOTALL
        )
        todo_path.write_text(existing)
    else:
        with todo_path.open("a") as fh:
            fh.write("\n" + block)

    print(f"  ✓ {len(medium_up)} SIM tickets written to tasks/todo.md")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORTS_DIR / f"sim_report_{ts}.md"

    print("=" * 60)
    print("  Forensic-AI Workflow Simulation Suite")
    print(f"  {ts}")
    print("=" * 60)

    # Phase 2: Monte Carlo
    print(f"\n[Phase 2] Monte Carlo — {N_MC_RUNS} runs × {len(WORKFLOW_REGISTRY)} workflows")
    t0 = time.time()
    random.seed(RANDOM_SEED)
    mc_reports: list[SimReport] = []
    for wf in sorted(WORKFLOW_REGISTRY.keys()):
        report = run_workflow_simulation(wf, n=N_MC_RUNS, seed=RANDOM_SEED)
        mc_reports.append(report)
        icon = "✓" if report.success_rate >= 0.75 else ("⚠" if report.success_rate >= 0.55 else "✗")
        print(f"  {icon} {wf:<30} success={_pct(report.success_rate)}")
    print(f"  Done in {time.time()-t0:.2f}s")

    # Phase 3: Game Theory
    print(f"\n[Phase 3] Game Theory — {N_GT_RUNS} runs × 4 scenarios")
    t0 = time.time()
    gt_scenarios = run_all_scenarios(n=N_GT_RUNS, seed=RANDOM_SEED)
    for s in gt_scenarios:
        pr = s.terminal_distribution.get("PARTNER_REJECTED", 0) / s.n_runs
        rl = s.terminal_distribution.get("REVISION_LIMIT", 0) / s.n_runs
        print(f"  ✓ {s.scenario:<45} partner_reject={pr:.1%}  rev_limit={rl:.1%}")
    print(f"  Done in {time.time()-t0:.2f}s")

    # Phase 4: Fuzz
    print("\n[Phase 4] Input Fuzz Analysis")
    t0 = time.time()
    fuzz_results = run_fuzz_analysis()
    fuzz_summary = summarise_fuzz(fuzz_results)
    print(f"  ✓ {fuzz_summary['total_tests']} tests — "
          f"HIGH={fuzz_summary['high_severity_findings']}, "
          f"MEDIUM={fuzz_summary['medium_severity_findings']}")
    print(f"  Done in {time.time()-t0:.2f}s")

    # Phase 5: Conflict Detection
    print("\n[Phase 5] Conflict Detection (static analysis)")
    t0 = time.time()
    conflicts = run_conflict_detection()
    total_conflicts = sum(
        len([f for f in v if f.severity in ("HIGH", "MEDIUM")])
        for v in conflicts.values()
    )
    print(f"  ✓ {sum(len(v) for v in conflicts.values())} checks — "
          f"{total_conflicts} HIGH/MEDIUM findings")
    print(f"  Done in {time.time()-t0:.2f}s")

    # Phase 6: Render report
    print(f"\n[Phase 6] Rendering report → {report_path}")

    mc_section     = _render_mc_section(mc_reports)
    gt_section     = _render_gt_section(gt_scenarios)
    fuzz_section   = _render_fuzz_section(fuzz_summary, fuzz_results)
    conflict_sec   = _render_conflict_section(conflicts)
    matrix_section, tickets = _render_priority_matrix(mc_reports, gt_scenarios, fuzz_summary, conflicts)

    report_text = f"""# Forensic-AI Workflow Simulation Report

**Generated:** {ts}
**Seed:** {RANDOM_SEED}
**Monte Carlo:** {N_MC_RUNS} runs × {len(WORKFLOW_REGISTRY)} workflows = {N_MC_RUNS * len(WORKFLOW_REGISTRY):,} total
**Game Theory:** {N_GT_RUNS} runs × 4 scenarios = {N_GT_RUNS * 4:,} total
**Fuzz tests:** {fuzz_summary['total_tests']} test cases
**Conflict checks:** {sum(len(v) for v in conflicts.values())} checks

---

{mc_section}

---

{gt_section}

---

{fuzz_section}

---

{conflict_sec}

---

{matrix_section}

---

*Simulation suite: simulation/harness.py | game_theory.py | input_fuzzer.py | conflict_detector.py*
*No API calls used. All probabilities are parametric estimates from code analysis.*
"""

    report_path.write_text(report_text, encoding="utf-8")
    print(f"  ✓ Report written ({report_path.stat().st_size // 1024} KB)")

    # Write tickets to todo.md
    _write_tickets_to_todo(tickets)

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    worst = min(mc_reports, key=lambda x: x.success_rate)
    best  = max(mc_reports, key=lambda x: x.success_rate)
    print(f"  Most failure-prone workflow: {worst.workflow} ({_pct(worst.success_rate)})")
    print(f"  Most stable workflow:        {best.workflow} ({_pct(best.success_rate)})")
    print(f"  Total SIM tickets (≥MEDIUM): {len([t for t in tickets if t['severity'] in ('HIGH','MEDIUM')])}")
    print(f"  Full report: {report_path}")
    print()


if __name__ == "__main__":
    main()

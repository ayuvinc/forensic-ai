"""Case tracker — scan cases/ folder and display status table."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from config import CASES_DIR
from core.state_machine import is_terminal, CaseStatus


def run_case_tracker(console: Console) -> None:
    """Display all cases with status, offer resume for non-terminal cases."""
    cases = _scan_cases()

    if not cases:
        console.print("[yellow]No cases found in cases/ folder.[/yellow]")
        return

    table = Table(title="Case Tracker", border_style="cyan")
    table.add_column("Case ID", style="bold")
    table.add_column("Client")
    table.add_column("Workflow")
    table.add_column("Status")
    table.add_column("Last Updated")

    resumable = []
    for case in cases:
        status = case.get("status", "unknown")
        try:
            cs = CaseStatus(status)
            terminal = is_terminal(cs)
            status_style = "green" if terminal else "yellow"
            status_label = f"[{status_style}]{status}[/{status_style}]"
            if not terminal:
                resumable.append(case)
        except ValueError:
            status_label = status

        table.add_row(
            case.get("case_id", "?"),
            case.get("client_name", "—"),
            case.get("workflow", "—"),
            status_label,
            case.get("last_updated", "—")[:19],
        )

    console.print(table)

    if resumable:
        console.print(f"\n[yellow]{len(resumable)} case(s) in progress.[/yellow]")
        if Confirm.ask("Resume one of these cases?", default=False):
            for i, case in enumerate(resumable):
                console.print(f"  {i+1}. {case['case_id']} — {case.get('client_name', '')} ({case.get('status', '')})")
            choice = Prompt.ask("  Select case number", default="1")
            try:
                selected = resumable[int(choice) - 1]
                console.print(f"\n[cyan]To resume: run the workflow for case {selected['case_id']}[/cyan]")
                console.print(f"The orchestrator will detect the existing state and offer to resume from: {selected.get('status', '')}")
            except (IndexError, ValueError):
                console.print("[red]Invalid selection.[/red]")


def _scan_cases() -> list[dict]:
    """Scan cases/ folder and return list of case state dicts."""
    if not CASES_DIR.exists():
        return []

    cases = []
    for case_dir in sorted(CASES_DIR.iterdir()):
        if not case_dir.is_dir():
            continue
        state_path = case_dir / "state.json"
        intake_path = case_dir / "intake.json"

        state = {}
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        if intake_path.exists():
            try:
                intake = json.loads(intake_path.read_text(encoding="utf-8"))
                state["client_name"] = intake.get("client_name", "")
            except Exception:
                pass

        if state:
            cases.append(state)

    return cases

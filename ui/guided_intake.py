"""Guided intake — conversational Pydantic extraction.

No structured forms. Claude asks one question at a time.
Extracts answers into CaseIntake behind the scenes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import uuid

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from schemas.case import CaseIntake


def prompt_with_options(
    console: Console,
    question: str,
    options: list[dict],
    allow_free_text: bool = True,
) -> dict:
    """Display a numbered option list and return a structured selection.

    Args:
        console: Rich console instance.
        question: The question to display above the list.
        options: List of dicts with 'id' and 'label' keys.
        allow_free_text: If True, adds "0. Other (type your own)" option.

    Returns:
        dict with keys: selected_id, label, is_custom
    """
    console.print(f"\n  [bold]{question}[/bold]")

    table = Table(show_header=False, box=None, padding=(0, 2))
    for i, opt in enumerate(options, 1):
        table.add_row(f"[dim]{i}.[/dim]", opt["label"])
    if allow_free_text:
        table.add_row("[dim]0.[/dim]", "[dim]Other (type your own)[/dim]")
    console.print(table)

    valid = [str(i) for i in range(len(options) + 1)] if allow_free_text else [str(i) for i in range(1, len(options) + 1)]
    choice = Prompt.ask("  Select", choices=valid, default="1")

    if choice == "0" or (not allow_free_text and choice not in valid):
        custom = Prompt.ask("  Enter your own value")
        return {"selected_id": "custom", "label": custom, "is_custom": True}

    idx = int(choice) - 1
    selected = options[idx]
    return {"selected_id": selected["id"], "label": selected["label"], "is_custom": False}


def _load_industry_options() -> list[dict]:
    """Load industry options from taxonomy JSON for prompt_with_options."""
    import json
    from pathlib import Path
    path = Path(__file__).parent.parent / "knowledge" / "taxonomy" / "industries.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [{"id": ind["id"], "label": ind["label"]} for ind in data.get("industries", [])]
    except Exception:
        return [{"id": "other", "label": "Other"}]


def _load_jurisdiction_options() -> list[dict]:
    """Load jurisdiction options from taxonomy JSON for prompt_with_options."""
    import json
    from pathlib import Path
    path = Path(__file__).parent.parent / "knowledge" / "taxonomy" / "jurisdictions.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [{"id": k, "label": v["label"]} for k, v in data.get("jurisdictions", {}).items()]
    except Exception:
        return [{"id": "UAE", "label": "United Arab Emirates"}]


def run_guided_frm_intake(console: Console) -> Optional[CaseIntake]:
    """Conversational FRM intake — asks one question at a time."""
    console.print("\n[bold cyan]FRM Risk Register — Case Intake[/bold cyan]")
    console.print("[dim]I'll ask you a few questions to set up the engagement.[/dim]\n")

    client_name = Prompt.ask("  What is the client's company name?")
    if not client_name.strip():
        return None

    industry_selection = prompt_with_options(
        console,
        f"What industry is {client_name} in?",
        _load_industry_options(),
        allow_free_text=True,
    )
    industry = industry_selection["label"]
    company_size = Prompt.ask(f"  How large is {client_name} — roughly how many employees?", default="")
    jurisdiction_selection = prompt_with_options(
        console,
        f"What is {client_name}'s primary operating jurisdiction?",
        _load_jurisdiction_options(),
        allow_free_text=True,
    )
    jurisdiction = jurisdiction_selection["label"] if not jurisdiction_selection["is_custom"] else jurisdiction_selection["label"]
    ops_j_raw = Prompt.ask(
        f"  Does {client_name} operate in any other jurisdictions? (comma-separated, or Enter to skip)",
        default="",
    )
    operating_j = [j.strip() for j in ops_j_raw.split(",") if j.strip()] or [jurisdiction]

    description = Prompt.ask(
        f"  Briefly describe the scope of the FRM engagement for {client_name}"
    )

    case_id = f"{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    console.print(f"\n  [dim]Case ID: {case_id}[/dim]")
    console.print(f"\n  Got it. I'll now build the FRM Risk Register for {client_name}.")
    console.print("  [dim]This will take 2–3 minutes.[/dim]")

    return CaseIntake(
        case_id=case_id,
        client_name=client_name,
        industry=industry,
        company_size=company_size or None,
        primary_jurisdiction=jurisdiction,
        operating_jurisdictions=operating_j,
        workflow="frm_risk_register",
        description=description,
        created_at=datetime.now(timezone.utc),
    )


def run_guided_investigation_intake(console: Console) -> Optional[CaseIntake]:
    """Conversational investigation intake."""
    console.print("\n[bold cyan]Investigation Report — Case Intake[/bold cyan]\n")

    client_name = Prompt.ask("  Client name")
    if not client_name.strip():
        return None

    industry  = Prompt.ask("  Industry / sector")
    jurisdiction = Prompt.ask("  Primary jurisdiction", default="UAE")
    description  = Prompt.ask("  Brief description of the matter under investigation")

    case_id = f"{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    return CaseIntake(
        case_id=case_id,
        client_name=client_name,
        industry=industry,
        primary_jurisdiction=jurisdiction,
        operating_jurisdictions=[jurisdiction],
        workflow="investigation_report",
        description=description,
        created_at=datetime.now(timezone.utc),
    )


def run_guided_proposal_intake(console: Console) -> Optional[CaseIntake]:
    """Conversational client proposal intake."""
    console.print("\n[bold cyan]Client Proposal — Intake[/bold cyan]\n")

    prospect_name = Prompt.ask("  Prospect / potential client name")
    if not prospect_name.strip():
        return None

    industry     = Prompt.ask("  Industry")
    jurisdiction = Prompt.ask("  Primary jurisdiction", default="UAE")
    description  = Prompt.ask("  What service(s) are you proposing?")

    case_id = f"PROP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    return CaseIntake(
        case_id=case_id,
        client_name=prospect_name,
        industry=industry,
        primary_jurisdiction=jurisdiction,
        operating_jurisdictions=[jurisdiction],
        workflow="client_proposal",
        description=description,
        created_at=datetime.now(timezone.utc),
    )


def run_generic_intake(
    console: Console,
    workflow: str,
    workflow_label: str,
) -> Optional[CaseIntake]:
    """Generic conversational intake for any workflow."""
    console.print(f"\n[bold cyan]{workflow_label} — Intake[/bold cyan]\n")

    client_name  = Prompt.ask("  Client name")
    if not client_name.strip():
        return None

    industry     = Prompt.ask("  Industry / sector")
    jurisdiction = Prompt.ask("  Primary jurisdiction", default="UAE")
    description  = Prompt.ask("  Brief description of the engagement")

    case_id = f"{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    return CaseIntake(
        case_id=case_id,
        client_name=client_name,
        industry=industry,
        primary_jurisdiction=jurisdiction,
        operating_jurisdictions=[jurisdiction],
        workflow=workflow,
        description=description,
        created_at=datetime.now(timezone.utc),
    )

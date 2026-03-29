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

from schemas.case import CaseIntake


def run_guided_frm_intake(console: Console) -> Optional[CaseIntake]:
    """Conversational FRM intake — asks one question at a time."""
    console.print("\n[bold cyan]FRM Risk Register — Case Intake[/bold cyan]")
    console.print("[dim]I'll ask you a few questions to set up the engagement.[/dim]\n")

    client_name = Prompt.ask("  What is the client's company name?")
    if not client_name.strip():
        return None

    industry = Prompt.ask(f"  What industry is {client_name} in?")
    company_size = Prompt.ask(f"  How large is {client_name} — roughly how many employees?", default="")
    jurisdiction = Prompt.ask(f"  What is {client_name}'s primary operating jurisdiction?", default="UAE")
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

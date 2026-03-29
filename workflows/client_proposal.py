"""Client proposal workflow — 7-section forensic proposal.

Sections: Cover, Executive Summary, Background & Understanding,
Scope of Work, Methodology, Team & Credentials, Fees, Terms & Conditions.

Team auto-selection: Partner selects relevant credentials from firm_profile.
Pricing: loaded from firm_profile/pricing_model.json.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt

from config import ANTHROPIC_API_KEY, BASE_DIR, HAIKU
from core.hook_engine import HookEngine
from core.tool_registry import ToolRegistry
from schemas.artifacts import FinalDeliverable
from schemas.case import CaseIntake
from tools.file_tools import write_final_report


FIRM_PROFILE_DIR = BASE_DIR / "firm_profile"


def run_client_proposal_workflow(
    intake: CaseIntake,
    registry: ToolRegistry,
    hook_engine: HookEngine,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FinalDeliverable:
    """Generate forensic client proposal."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    # Load firm profile
    firm_profile = _load_firm_profile()
    team = _load_team()
    pricing = _load_pricing()

    # Gather proposal-specific inputs
    console.print("\n  [bold]Proposal details[/bold]")
    prospect_name = Prompt.ask("  Prospect / client name", default=intake.client_name)
    contact_person = Prompt.ask("  Contact person at prospect", default="")
    proposal_scope = Prompt.ask("  Specific scope to address in proposal", default=intake.description)

    console.print("\n  [bold]Fee approach for this proposal[/bold]")
    console.print(f"  Default model: {pricing.get('model', 'daily')}")
    use_default = Confirm.ask("  Use default pricing model?", default=True)
    fee_notes = ""
    if not use_default:
        fee_notes = Prompt.ask("  Fee notes / custom structure for this proposal")

    # Auto-select team members
    on_progress("Selecting relevant team members...")
    selected_team = _select_team(team, intake.workflow, proposal_scope)

    # Generate proposal sections
    on_progress("Drafting proposal...")
    content = _generate_proposal(
        intake=intake,
        prospect_name=prospect_name,
        contact_person=contact_person,
        proposal_scope=proposal_scope,
        firm_profile=firm_profile,
        selected_team=selected_team,
        pricing=pricing,
        fee_notes=fee_notes,
    )

    # Write report
    report_path = write_final_report(intake.case_id, content, "en")
    on_progress(f"Proposal saved → {report_path}")

    # Also generate .docx if output_generator available
    try:
        from tools.output_generator import OutputGenerator
        gen = OutputGenerator()
        docx_path = Path(report_path).parent / "proposal.docx"
        gen.generate_docx(content, docx_path, firm_name=firm_profile.get("firm_name", "GoodWork Forensic Consulting"))
        on_progress(f"Word document saved → {docx_path}")
    except Exception:
        pass

    # Offer to chain to PPT deck
    if Confirm.ask("\n  Also generate PPT prompt pack for this proposal?", default=False):
        from workflows.proposal_deck import run_proposal_deck_workflow
        deck_intake = intake.model_copy(update={"description": proposal_scope})
        run_proposal_deck_workflow(deck_intake, registry, hook_engine, console, on_progress)

    return FinalDeliverable(
        case_id=intake.case_id,
        workflow="client_proposal",
        approved_by="partner",
        language=intake.language,
        content_en=content,
        citations=[],
        revision_history=[0],
        delivery_date=datetime.now(timezone.utc),
    )


def _generate_proposal(
    intake: CaseIntake,
    prospect_name: str,
    contact_person: str,
    proposal_scope: str,
    firm_profile: dict,
    selected_team: list[dict],
    pricing: dict,
    fee_notes: str,
) -> str:
    """Sonnet single-turn: generate full 7-section proposal."""
    import anthropic
    from config import SONNET

    firm_name = firm_profile.get("firm_name", "GoodWork Forensic Consulting")
    now = datetime.now(timezone.utc).strftime("%d %B %Y")

    team_str = "\n".join(
        f"- {m.get('name', '')}, {m.get('role', '')}: {m.get('bio', '')}"
        for m in selected_team
    ) or "Team details to be confirmed."

    fee_str = (
        f"Pricing model: {pricing.get('model', 'daily')}, "
        f"Currency: {pricing.get('currency', 'AED')}. "
        f"Partner rate: {pricing.get('rates', {}).get('partner', 'TBD')}, "
        f"Senior rate: {pricing.get('rates', {}).get('pm', 'TBD')}."
    )
    if fee_notes:
        fee_str += f" Custom arrangement: {fee_notes}"

    prompt = f"""Draft a professional forensic consulting proposal for the following engagement.

FIRM: {firm_name}
PROSPECT: {prospect_name} (Contact: {contact_person})
SCOPE: {proposal_scope}
INDUSTRY: {intake.industry}
JURISDICTION: {intake.primary_jurisdiction}
DATE: {now}

TEAM:
{team_str}

FEES: {fee_str}

Write a complete 7-section proposal in Markdown format:
1. Cover Page (firm name, prospect name, date, reference number)
2. Executive Summary (2-3 paragraphs)
3. Background & Understanding of Client's Situation
4. Scope of Work (detailed deliverables and exclusions)
5. Methodology (approach, phases, ACFE/COSO/ISO 37001 references)
6. Our Team & Credentials (use provided team data, select most relevant)
7. Indicative Fees (structured per the pricing data above)
8. Terms & Conditions (professional services standard terms)

Write in professional English. Be specific about forensic procedures. Reference relevant UAE/GCC regulatory context.
Format clearly with headers and bullet points where appropriate.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def _select_team(team: list[dict], workflow: str, scope: str) -> list[dict]:
    """Auto-select relevant team members based on workflow and scope."""
    if not team:
        return []
    if len(team) <= 3:
        return team

    # Use Haiku to select most relevant team members
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        team_str = json.dumps(team, indent=2)
        resp = client.messages.create(
            model=HAIKU,
            max_tokens=256,
            messages=[{
                "role": "user",
                "content": (
                    f"Select the 2-4 most relevant team members for this engagement.\n"
                    f"Workflow: {workflow}, Scope: {scope[:200]}\n\n"
                    f"Team:\n{team_str}\n\n"
                    "Return a JSON array of selected member names only."
                ),
            }],
        )
        import re
        match = re.search(r'\[.*\]', resp.content[0].text, re.DOTALL)
        if match:
            selected_names = json.loads(match.group())
            return [m for m in team if m.get("name") in selected_names]
    except Exception:
        pass

    return team[:4]


def _load_firm_profile() -> dict:
    path = FIRM_PROFILE_DIR / "firm_profile.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"firm_name": "GoodWork Forensic Consulting"}


def _load_team() -> list[dict]:
    path = FIRM_PROFILE_DIR / "team.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _load_pricing() -> dict:
    path = FIRM_PROFILE_DIR / "pricing_model.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"model": "daily", "currency": "AED", "rates": {}}

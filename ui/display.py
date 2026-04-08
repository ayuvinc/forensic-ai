"""Display utilities — Rich rendering, Arabic right-justify."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from schemas.artifacts import PersonaReviewOutput, FinalDeliverable


def render_deliverable_summary(console: Console, deliverable: FinalDeliverable) -> None:
    """Display a summary panel for a completed deliverable."""
    lines = [
        f"[bold]Case:[/bold] {deliverable.case_id}",
        f"[bold]Workflow:[/bold] {deliverable.workflow.replace('_', ' ').title()}",
        f"[bold]Approved by:[/bold] {deliverable.approved_by}",
        f"[bold]Language:[/bold] {deliverable.language}",
        f"[bold]Citations:[/bold] {len(deliverable.citations)}",
        f"[bold]Delivered:[/bold] {deliverable.delivery_date.strftime('%d %B %Y %H:%M UTC')}",
    ]
    console.print(Panel(
        "\n".join(lines),
        title="[bold green]Deliverable Ready[/bold green]",
        border_style="green",
    ))


def render_persona_reviews(console: Console, reviews: list[PersonaReviewOutput]) -> None:
    """Display persona review summary table."""
    if not reviews:
        return

    table = Table(title="Persona Review Summary", border_style="cyan")
    table.add_column("Persona", style="bold")
    table.add_column("Verdict")
    table.add_column("Objections")
    table.add_column("Regulatory Gaps")

    for r in reviews:
        verdict_color = {"pass": "green", "conditional_pass": "yellow", "fail": "red"}.get(
            r.overall_verdict, "white"
        )
        table.add_row(
            r.persona,
            f"[{verdict_color}]{r.overall_verdict}[/{verdict_color}]",
            str(len(r.objections)),
            str(len(r.regulatory_gaps)),
        )

    console.print(table)


def render_arabic_panel(console: Console, title: str, content: str) -> None:
    """Render Arabic content right-justified."""
    text = Text(content, justify="right")
    console.print(Panel(text, title=title, border_style="blue"))


def print_header(console: Console, firm_name: str = "GoodWork Forensic Consulting") -> None:
    """Print application header."""
    console.print(Panel(
        f"[bold cyan]{firm_name}[/bold cyan]\n"
        "[dim]Forensic Consulting Framework[/dim]",
        border_style="cyan",
    ))


def print_section(console: Console, title: str) -> None:
    """Print a section separator."""
    console.print(f"\n[bold cyan]{'─' * 5} {title} {'─' * 5}[/bold cyan]")


def display_research_mode_banner(console: Console, mode: str) -> None:
    """Render a one-time research mode banner at session start."""
    if mode == "live":
        console.print(Panel(
            "[green]Research: LIVE[/green] — Tavily enabled. "
            "Regulatory, sanctions, and web lookups will use live data.",
            border_style="green",
            padding=(0, 1),
        ))
    else:
        console.print(Panel(
            "[yellow]Research: KNOWLEDGE-ONLY[/yellow] — No external data. "
            "All outputs are based on model knowledge. "
            "Set [bold]RESEARCH_MODE=live[/bold] in .env with a valid TAVILY_API_KEY for live data.",
            border_style="yellow",
            padding=(0, 1),
        ))

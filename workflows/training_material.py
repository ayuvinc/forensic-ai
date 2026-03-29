"""Training material workflow — role-specific, multiple output formats."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Prompt

from config import ANTHROPIC_API_KEY, SONNET
from schemas.artifacts import FinalDeliverable
from schemas.case import CaseIntake
from tools.file_tools import write_final_report, case_dir


TRAINING_TOPICS = {
    "1": "aml_awareness",
    "2": "fraud_awareness",
    "3": "bribery_corruption_awareness",
    "4": "data_privacy",
    "5": "whistleblowing_procedures",
    "6": "kyc_procedures",
    "7": "custom",
}

TARGET_AUDIENCES = {
    "1": "all_staff",
    "2": "finance_team",
    "3": "senior_management",
    "4": "board_directors",
    "5": "compliance_team",
    "6": "front_line_staff",
}


def run_training_material_workflow(
    intake: CaseIntake,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FinalDeliverable:
    """Generate role-specific training materials."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    console.print("\n  [bold]Training topic:[/bold]")
    for k, v in TRAINING_TOPICS.items():
        console.print(f"    {k}. {v.replace('_', ' ').title()}")
    topic_choice = Prompt.ask("  Topic", choices=list(TRAINING_TOPICS.keys()), default="2")
    topic = TRAINING_TOPICS[topic_choice]
    if topic == "custom":
        topic = Prompt.ask("  Custom topic name")

    console.print("\n  [bold]Target audience:[/bold]")
    for k, v in TARGET_AUDIENCES.items():
        console.print(f"    {k}. {v.replace('_', ' ').title()}")
    aud_choice = Prompt.ask("  Audience", choices=list(TARGET_AUDIENCES.keys()), default="1")
    target_audience = TARGET_AUDIENCES[aud_choice]

    duration = Prompt.ask("  Duration (minutes)", default="60")
    include_quiz = Prompt.ask("  Include knowledge check questions?", choices=["y", "n"], default="y")
    include_case_study = Prompt.ask("  Include case study?", choices=["y", "n"], default="y")

    on_progress(f"Generating {topic.replace('_', ' ')} training for {target_audience.replace('_', ' ')}...")
    content = _generate_training_material(
        intake, topic, target_audience, int(duration),
        include_quiz == "y", include_case_study == "y"
    )

    report_path = write_final_report(intake.case_id, content, "en")
    on_progress(f"Training material saved → {report_path}")

    return FinalDeliverable(
        case_id=intake.case_id,
        workflow="training_material",
        approved_by="partner",
        language=intake.language,
        content_en=content,
        citations=[],
        revision_history=[0],
        delivery_date=datetime.now(timezone.utc),
    )


def _generate_training_material(
    intake: CaseIntake,
    topic: str,
    audience: str,
    duration_minutes: int,
    include_quiz: bool,
    include_case_study: bool,
) -> str:
    import anthropic

    prompt = f"""Create comprehensive training material on {topic.replace('_', ' ').title()}.

CLIENT: {intake.client_name}
INDUSTRY: {intake.industry}
JURISDICTION: {intake.primary_jurisdiction}
TARGET AUDIENCE: {audience.replace('_', ' ').title()}
DURATION: {duration_minutes} minutes
{"Include knowledge check questions (5-10 MCQ/scenario questions)" if include_quiz else ""}
{"Include a realistic case study relevant to the industry" if include_case_study else ""}

Structure:
1. Learning objectives (3-5 SMART objectives)
2. Introduction / Why this matters
3. Core content sections (adapted for {audience.replace('_', ' ')})
4. Key red flags to watch for
5. Reporting procedures
6. {"Case Study" if include_case_study else ""}
7. {"Knowledge Check Questions with Answers" if include_quiz else ""}
8. Key takeaways
9. Further resources

Write at appropriate level for {audience.replace('_', ' ')}.
Reference UAE/GCC regulatory requirements where applicable ({intake.primary_jurisdiction} jurisdiction).
Format in Markdown. Make it engaging and practical.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    now = datetime.now(timezone.utc).strftime("%d %B %Y")
    header = (
        f"# {topic.replace('_', ' ').title()} Training\n"
        f"**Organisation:** {intake.client_name}\n"
        f"**Audience:** {audience.replace('_', ' ').title()}\n"
        f"**Duration:** {duration_minutes} minutes\n"
        f"**Date:** {now}\n\n---\n\n"
    )
    return header + resp.content[0].text.strip()

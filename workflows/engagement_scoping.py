"""Engagement Scoping Workflow (SCOPE-WF-01).

5-step problem-first flow for ambiguous engagements where the service type
is not known upfront. Maher describes the client situation; the model reads
knowledge/engagement_taxonomy/framework.md to recommend the right service,
scope components, deliverables, and sequencing.

BA sign-off: BA-010.
Design: conversation-first — no forms. Model asks, extracts, recommends.

Output: ConfirmedScope written to cases/{id}/scope_document.md and state.json.
Routing: if target_workflow is set, offers to launch that workflow directly.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt

from config import ANTHROPIC_API_KEY, SONNET
from schemas.case import CaseIntake
from schemas.engagement_scope import ConfirmedScope, ScopeIntake, ScopeRecommendation
from tools.file_tools import append_audit_event, write_artifact, write_final_report, write_state


# ── Routing map: engagement type name → menu option number ────────────────────
# Used at the end to offer Maher a direct launch into the matched workflow.
_WORKFLOW_ROUTE = {
    "investigation_report":        "2",
    "investigation_procurement":   "2",
    "investigation_payroll":       "2",
    "investigation_expense":       "2",
    "investigation_financial_stmt": "2",
    "investigation_aml":           "2",
    "investigation_whistleblower": "2",
    "frm_risk_register":           "6",
    "policy_sop":                  "4",
    "training_material":           "5",
    "client_proposal":             "7",
    "due_diligence":               "11",
    "due_diligence_individual":    "11",
    "due_diligence_entity":        "11",
    "sanctions_screening":         "12",
    "transaction_testing":         "13",
}

_WORKFLOW_LABELS = {
    "2":  "Investigation Report (Option 2)",
    "4":  "Policy / SOP Generator (Option 4)",
    "5":  "Training Material (Option 5)",
    "6":  "FRM Risk Register (Option 6)",
    "7":  "Client Proposal (Option 7)",
    "11": "Due Diligence (Option 11)",
    "12": "Sanctions Screening (Option 12)",
    "13": "Transaction Testing (Option 13)",
}

_LICENSED_DB_DISCLAIMER = (
    "**Screening Scope Limitation:** This scope includes sanctions or due diligence components. "
    "Screening will use publicly available official lists only (OFAC, UN, EU, UK OFSI, UAE). "
    "Commercial database screening (WorldCheck, WorldCompliance, LexisNexis Diligence) is not "
    "included. For acquisition-grade or regulatory-grade screening, supplementary commercial "
    "database screening is recommended."
)

_HUMINT_FLAG = (
    "**HUMINT Scope — Manual Execution Required:** This scope includes components requiring "
    "discreet human source enquiries. HUMINT cannot be performed by this tool. "
    "The scope document defines the HUMINT objectives; execution is a manual step."
)


def run_engagement_scoping_workflow(
    intake: CaseIntake,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
    headless_params: Optional[dict] = None,
) -> ConfirmedScope:
    """Run the 5-step engagement scoping conversation.

    Step 1 — Load taxonomy knowledge (knowledge/engagement_taxonomy/framework.md)
    Step 2 — Ask about the client situation (open questions)
    Step 3 — Propose scope: engagement type(s), components, deliverables
    Step 4 — Ask follow-up questions to close gaps; revise recommendation
    Step 5 — Confirm scope; write document; offer routing to matched workflow
    """
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    # ── Step 1: Load taxonomy knowledge ──────────────────────────────────────
    on_progress("Loading engagement taxonomy...")
    taxonomy_text = _load_taxonomy()

    # ── Step 2: Contextual intake ─────────────────────────────────────────────
    if headless_params:
        situation = headless_params.get("situation", intake.description)
        trigger = headless_params.get("trigger", "Consultant request")
        desired_outcome = headless_params.get("desired_outcome", "Scope document and engagement recommendation")
        constraints = headless_params.get("constraints", "")
        red_flags = headless_params.get("red_flags", "")
    else:
        console.print("\n  [bold]Tell me about the client situation.[/bold]")
        console.print("  [dim]Answer in plain language — no need to know which service applies yet.[/dim]\n")

        situation = Prompt.ask("  What is the client facing? (describe the problem)")
        trigger = Prompt.ask("  What triggered this engagement? (complaint, audit finding, suspicion, etc.)")
        desired_outcome = Prompt.ask("  What does the client want to walk away with?")
        constraints = Prompt.ask("  Any constraints? (timeline, budget, data access, confidentiality)", default="")
        red_flags = Prompt.ask("  Any specific red flags or suspicions Maher already has?", default="")

    scope_intake = ScopeIntake(
        client_situation=situation,
        trigger=trigger,
        desired_outcome=desired_outcome,
        constraints=constraints,
        known_red_flags=red_flags,
        client_industry=intake.industry,
        client_jurisdiction=intake.primary_jurisdiction,
    )

    # ── Step 3: Propose scope ─────────────────────────────────────────────────
    on_progress("Analysing situation against engagement taxonomy...")
    recommendation = _propose_scope(intake, scope_intake, taxonomy_text)

    _display_recommendation(console, recommendation)

    # ── Step 4: Follow-up to refine (skipped in headless mode) ────────────────
    if not headless_params:
        wants_refinement = not Confirm.ask("\n  Does this look right, or do you want to refine it?",
                                           default=True)
        if wants_refinement:
            on_progress("Asking follow-up questions to refine...")
            followup_answers = _collect_followup(console, recommendation, scope_intake)
            on_progress("Revising scope recommendation...")
            recommendation = _revise_scope(intake, scope_intake, taxonomy_text, recommendation, followup_answers)
            _display_recommendation(console, recommendation)

    # ── Step 5: Confirm and produce scope document ────────────────────────────
    if not headless_params:
        confirmed = Confirm.ask("\n  Confirm this scope and produce the scope document?")
        if not confirmed:
            console.print("  [yellow]Scope not confirmed. Returning to menu.[/yellow]")
            raise ValueError("Engagement scope not confirmed by consultant.")

    humint_required = any(
        "humint" in c.lower() or "source enquir" in c.lower() or "human source" in c.lower()
        for c in recommendation.caveats + recommendation.scope_components
    )
    licensed_db_gap = any(
        kw in " ".join(recommendation.engagement_types + [recommendation.primary_engagement]).lower()
        for kw in ("due_diligence", "sanctions_screening", "due diligence", "sanctions")
    )

    # Determine routing
    target_workflow = _resolve_route(recommendation.primary_engagement)

    scope_content = _generate_scope_document(
        intake, scope_intake, recommendation,
        humint_required=humint_required,
        licensed_db_gap=licensed_db_gap,
    )

    confirmed_scope = ConfirmedScope(
        case_id=intake.case_id,
        intake=scope_intake,
        recommendation=recommendation,
        target_workflow=target_workflow,
        confirmed=True,
        scope_content=scope_content,
        humint_required=humint_required,
        licensed_db_gap=licensed_db_gap,
    )

    # Write scope document
    _write_scope_artifacts(intake, confirmed_scope, scope_content)
    on_progress(f"Scope document saved → cases/{intake.case_id}/scope_document.md")

    # Offer routing
    _offer_routing(console, confirmed_scope, target_workflow)

    return confirmed_scope


# ── Taxonomy loader ────────────────────────────────────────────────────────────

def _load_taxonomy() -> str:
    """Read knowledge/engagement_taxonomy/framework.md at runtime."""
    taxonomy_path = Path("knowledge/engagement_taxonomy/framework.md")
    if taxonomy_path.exists():
        return taxonomy_path.read_text(encoding="utf-8")
    return (
        "Taxonomy file not found. Apply general forensic consulting knowledge: "
        "Investigation (procurement/payroll/expense/financial statement/AML/whistleblower), "
        "FRM Risk Register, Due Diligence (individual/entity), Sanctions Screening, "
        "Transaction Testing, Policy/SOP, Training Material, Client Proposal."
    )


# ── Scope proposal ─────────────────────────────────────────────────────────────

def _propose_scope(
    intake: CaseIntake,
    scope_intake: ScopeIntake,
    taxonomy_text: str,
) -> ScopeRecommendation:
    """Sonnet Step 3: propose engagement scope from client situation + taxonomy."""
    import anthropic

    prompt = f"""You are a senior forensic consulting engagement director at GoodWork.
A consultant has described a new client situation. Read the engagement taxonomy below,
then propose the most appropriate engagement scope.

ENGAGEMENT TAXONOMY (GoodWork service lines):
---
{taxonomy_text[:6000]}
---

CLIENT SITUATION:
- Client: {intake.client_name} ({intake.industry}, {intake.primary_jurisdiction})
- Situation: {scope_intake.client_situation}
- Trigger: {scope_intake.trigger}
- Desired outcome: {scope_intake.desired_outcome}
- Constraints: {scope_intake.constraints or "None stated"}
- Known red flags: {scope_intake.known_red_flags or "None stated"}

Propose an engagement scope. Return a JSON object with this exact structure:
{{
  "engagement_types": ["primary_type", "secondary_type_if_any"],
  "primary_engagement": "single_best_fit_type",
  "scope_components": ["component 1", "component 2", "component 3"],
  "deliverables": ["deliverable 1", "deliverable 2"],
  "sequencing": ["Step 1: ...", "Step 2: ..."],
  "caveats": ["caveat 1"],
  "chaining_suggestion": "follow-on workflow name if a red flag warrants escalation, else null",
  "rationale": "one paragraph explaining why this scope fits the situation"
}}

Use the engagement type names from the taxonomy. Be specific — name real scope components
(e.g. "three-way matching test", "sanctions screening against OFAC/UN/EU", not generic phrases).
If HUMINT is required, name it explicitly in caveats.
Return only valid JSON.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_recommendation(resp.content[0].text.strip())


# ── Follow-up questions ────────────────────────────────────────────────────────

def _collect_followup(
    console: Console,
    recommendation: ScopeRecommendation,
    scope_intake: ScopeIntake,
) -> str:
    """Generate targeted follow-up questions and collect answers."""
    import anthropic

    # Ask Sonnet what it still needs to know
    prompt = f"""You are a forensic engagement director. You have proposed this scope:
Primary engagement: {recommendation.primary_engagement}
Components: {', '.join(recommendation.scope_components[:5])}
Caveats: {', '.join(recommendation.caveats)}
Rationale: {recommendation.rationale}

What are the 2–3 most important questions you still need answered to finalise this scope?
Return as a plain numbered list — no preamble, no JSON.
"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    questions_text = resp.content[0].text.strip()

    console.print(f"\n  [bold yellow]A few follow-up questions to sharpen the scope:[/bold yellow]")
    console.print(f"  [dim]{questions_text}[/dim]\n")

    answers = Prompt.ask("  Your answers (free text — answer any or all of the above)")
    return answers


def _revise_scope(
    intake: CaseIntake,
    scope_intake: ScopeIntake,
    taxonomy_text: str,
    current: ScopeRecommendation,
    followup_answers: str,
) -> ScopeRecommendation:
    """Sonnet: revise the scope recommendation based on follow-up answers."""
    import anthropic

    prompt = f"""You are a forensic engagement director. Revise the scope recommendation
based on the consultant's follow-up answers.

ORIGINAL RECOMMENDATION:
Primary: {current.primary_engagement}
Components: {json.dumps(current.scope_components)}
Deliverables: {json.dumps(current.deliverables)}
Caveats: {json.dumps(current.caveats)}
Rationale: {current.rationale}

CONSULTANT'S FOLLOW-UP ANSWERS:
{followup_answers}

CLIENT SITUATION REMINDER:
{scope_intake.client_situation}
{scope_intake.trigger}

Return a revised JSON object with the same structure as the original.
Only change what the follow-up answers warrant. Return only valid JSON.
"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_recommendation(resp.content[0].text.strip())


def _parse_recommendation(raw: str) -> ScopeRecommendation:
    """Parse Sonnet JSON into ScopeRecommendation. Fallback on error."""
    import re
    try:
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", raw)
        data = json.loads(match.group(1) if match else raw)
        return ScopeRecommendation(
            engagement_types=data.get("engagement_types", []),
            primary_engagement=data.get("primary_engagement", ""),
            scope_components=data.get("scope_components", []),
            deliverables=data.get("deliverables", []),
            sequencing=data.get("sequencing", []),
            caveats=data.get("caveats", []),
            chaining_suggestion=data.get("chaining_suggestion"),
            rationale=data.get("rationale", ""),
        )
    except Exception:
        return ScopeRecommendation(
            engagement_types=["unknown"],
            primary_engagement="unknown",
            scope_components=["Manual scope definition required — model could not parse recommendation."],
            deliverables=["Scope document"],
            sequencing=[],
            caveats=["Scope recommendation parsing failed — review manually."],
            rationale=raw[:500],
        )


# ── Display helpers ────────────────────────────────────────────────────────────

def _display_recommendation(console: Console, rec: ScopeRecommendation) -> None:
    console.print("\n  [bold green]Recommended Scope[/bold green]")
    console.print(f"  Primary engagement: [bold]{rec.primary_engagement}[/bold]")
    if len(rec.engagement_types) > 1:
        console.print(f"  Also covers: {', '.join(t for t in rec.engagement_types if t != rec.primary_engagement)}")
    console.print(f"\n  Rationale: [dim]{rec.rationale}[/dim]")
    console.print("\n  Scope components:")
    for c in rec.scope_components:
        console.print(f"    • {c}")
    console.print("\n  Deliverables:")
    for d in rec.deliverables:
        console.print(f"    • {d}")
    if rec.sequencing:
        console.print("\n  Sequencing:")
        for s in rec.sequencing:
            console.print(f"    {s}")
    if rec.caveats:
        console.print("\n  [yellow]Caveats:[/yellow]")
        for cv in rec.caveats:
            console.print(f"    ⚠  {cv}")
    if rec.chaining_suggestion:
        console.print(f"\n  [dim]Follow-on suggestion: {rec.chaining_suggestion}[/dim]")


# ── Routing ────────────────────────────────────────────────────────────────────

def _resolve_route(primary_engagement: str) -> Optional[str]:
    """Map primary_engagement string to a run.py menu option. Returns None if no match."""
    key = primary_engagement.lower().replace(" ", "_").replace("-", "_")
    # Direct lookup first
    if key in _WORKFLOW_ROUTE:
        return _WORKFLOW_ROUTE[key]
    # Substring match fallback
    for eng_key, option in _WORKFLOW_ROUTE.items():
        if eng_key in key or key in eng_key:
            return option
    return None


def _offer_routing(
    console: Console,
    confirmed_scope: ConfirmedScope,
    target_workflow: Optional[str],
) -> None:
    """Tell Maher which workflow to run next, or note that scope is the deliverable."""
    if target_workflow and target_workflow in _WORKFLOW_LABELS:
        label = _WORKFLOW_LABELS[target_workflow]
        console.print(f"\n  [bold cyan]This scope maps to: {label}[/bold cyan]")
        console.print(f"  [dim]Select {target_workflow} from the main menu to proceed with drafting.[/dim]")
    else:
        console.print("\n  [bold cyan]Novel / hybrid engagement[/bold cyan]")
        console.print("  [dim]No standard workflow matches exactly. The scope document is the deliverable.[/dim]")
        console.print("  [dim]Share it with the client to confirm scope before proceeding.[/dim]")


# ── Scope document generation ─────────────────────────────────────────────────

def _generate_scope_document(
    intake: CaseIntake,
    scope_intake: ScopeIntake,
    recommendation: ScopeRecommendation,
    humint_required: bool,
    licensed_db_gap: bool,
) -> str:
    """Generate the formatted scope document (markdown)."""
    now_str = datetime.now(timezone.utc).strftime("%d %B %Y")

    components_md = "\n".join(f"- {c}" for c in recommendation.scope_components)
    deliverables_md = "\n".join(f"- {d}" for d in recommendation.deliverables)
    sequencing_md = "\n".join(f"{s}" for s in recommendation.sequencing) if recommendation.sequencing else "Single-phase engagement."
    caveats_md = "\n".join(f"- {cv}" for cv in recommendation.caveats) if recommendation.caveats else "None identified."

    disclaimer_block = ""
    if licensed_db_gap:
        disclaimer_block += f"\n> {_LICENSED_DB_DISCLAIMER}\n"
    if humint_required:
        disclaimer_block += f"\n> {_HUMINT_FLAG}\n"

    chaining_note = ""
    if recommendation.chaining_suggestion:
        chaining_note = (
            f"\n## Follow-On Engagement\n\n"
            f"If red flags emerge during this engagement, consider escalating to: "
            f"**{recommendation.chaining_suggestion}**. "
            f"This would be initiated as a separate deliverable under the same case.\n"
        )

    doc = f"""# Engagement Scope Document
**Client:** {intake.client_name}
**Industry:** {intake.industry}
**Jurisdiction:** {intake.primary_jurisdiction}
**Prepared by:** GoodWork Forensic Consulting
**Date:** {now_str}
**Case ID:** {intake.case_id}

---
{disclaimer_block}
---

## Engagement Type

**Primary:** {recommendation.primary_engagement}
{f"**Additional:** {', '.join(t for t in recommendation.engagement_types if t != recommendation.primary_engagement)}" if len(recommendation.engagement_types) > 1 else ""}

## Situation Summary

**Client situation:** {scope_intake.client_situation}

**Trigger:** {scope_intake.trigger}

**Desired outcome:** {scope_intake.desired_outcome}

{f"**Constraints:** {scope_intake.constraints}" if scope_intake.constraints else ""}
{f"**Known red flags:** {scope_intake.known_red_flags}" if scope_intake.known_red_flags else ""}

## Rationale

{recommendation.rationale}

## Scope of Work

{components_md}

## Deliverables

{deliverables_md}

## Sequencing

{sequencing_md}

## Limitations and Caveats

{caveats_md}
{chaining_note}
---

*This scope document is subject to review and confirmation by the client before work commences.*
*GoodWork Forensic Consulting — {now_str}*
"""
    return doc


# ── Artifact persistence ──────────────────────────────────────────────────────

def _write_scope_artifacts(
    intake: CaseIntake,
    confirmed_scope: ConfirmedScope,
    scope_content: str,
) -> None:
    """Write scope_document.md, state.json update, and audit event."""
    # Write scope document as final report
    write_final_report(intake.case_id, scope_content, "en")

    # Also write a named scope_document.md alongside
    scope_path = Path("cases") / intake.case_id / "scope_document.md"
    scope_path.parent.mkdir(parents=True, exist_ok=True)
    scope_path.write_text(scope_content, encoding="utf-8")

    # Update state.json
    from tools.file_tools import read_state
    existing = read_state(intake.case_id) or {}
    existing.update({
        "status": "scope_confirmed",
        "workflow": "engagement_scoping",
        "scope_confirmed_at": datetime.now(timezone.utc).isoformat(),
        "target_workflow": confirmed_scope.target_workflow,
        "primary_engagement": confirmed_scope.recommendation.primary_engagement,
        "humint_required": confirmed_scope.humint_required,
        "licensed_db_gap": confirmed_scope.licensed_db_gap,
    })
    write_state(intake.case_id, existing)

    # Persist structured artifact
    write_artifact(intake.case_id, "engagement_scoping", "scope", {
        "case_id": intake.case_id,
        "primary_engagement": confirmed_scope.recommendation.primary_engagement,
        "engagement_types": confirmed_scope.recommendation.engagement_types,
        "target_workflow": confirmed_scope.target_workflow,
        "scope_components": confirmed_scope.recommendation.scope_components,
        "deliverables": confirmed_scope.recommendation.deliverables,
        "humint_required": confirmed_scope.humint_required,
        "licensed_db_gap": confirmed_scope.licensed_db_gap,
        "confirmed": True,
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
    })

    append_audit_event(intake.case_id, {
        "event": "scope_confirmed",
        "agent": "engagement_scoping",
        "workflow": "engagement_scoping",
        "primary_engagement": confirmed_scope.recommendation.primary_engagement,
        "target_workflow": confirmed_scope.target_workflow,
        "status": "ok",
    })

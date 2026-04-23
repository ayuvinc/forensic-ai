"""
Static cross-workflow conflict detector.

Checks (without running any workflows):
  1. Session state key collision across pages
  2. Hook ordering conflicts
  3. State machine reachability
  4. Model routing consistency
  5. Schema compatibility (JuniorDraft → PM input, PM → Partner input)
  6. Revision credit accounting in orchestrator
"""
from __future__ import annotations

import re
import sys
import ast
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

PAGES_DIR = _ROOT / "pages"
HOOKS_DIR = _ROOT / "hooks"
CORE_DIR  = _ROOT / "core"
SCHEMAS_DIR = _ROOT / "schemas"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ConflictFinding:
    check: str           # e.g. "session_state_collision"
    severity: str        # "HIGH" | "MEDIUM" | "LOW" | "INFO"
    description: str
    affected_files: list[str]
    recommendation: str


# ---------------------------------------------------------------------------
# 1. Session state key collision analysis
# ---------------------------------------------------------------------------

def _extract_session_state_keys(path: Path) -> dict[str, set[str]]:
    """Return {page_name: {key, ...}} for all session_state key references."""
    if not path.exists():
        return {}

    text = path.read_text(errors="ignore")
    # Match st.session_state["key"] and st.session_state.key and st.session_state.get("key")
    patterns = [
        r'session_state\["([^"]+)"\]',
        r"session_state\['([^']+)'\]",
        r'session_state\.get\("([^"]+)"',
        r"session_state\.get\('([^']+)'",
        r'session_state\.([a-zA-Z_][a-zA-Z0-9_]*)\b',
    ]
    keys: set[str] = set()
    for pat in patterns:
        for m in re.finditer(pat, text):
            k = m.group(1)
            # Filter out common Streamlit internals
            if k not in {"session_state", "rerun", "experimental_rerun"}:
                keys.add(k)
    return {path.name: keys}


def check_session_state_collisions() -> list[ConflictFinding]:
    findings: list[ConflictFinding] = []
    page_keys: dict[str, set[str]] = {}

    for page_file in sorted(PAGES_DIR.glob("*.py")):
        extracted = _extract_session_state_keys(page_file)
        page_keys.update(extracted)

    # Also check app.py and shared modules
    for extra in [_ROOT / "app.py"]:
        if extra.exists():
            page_keys.update(_extract_session_state_keys(extra))

    # Find keys that appear in multiple pages — potential collision if types differ
    all_keys: dict[str, list[str]] = {}
    for page, keys in page_keys.items():
        for k in keys:
            all_keys.setdefault(k, []).append(page)

    shared_keys = {k: pages for k, pages in all_keys.items() if len(pages) > 1}

    # Report high-risk shared keys (dynamic slug-based keys are fine; look for stage/result conflicts)
    high_risk_patterns = ["_stage", "_result", "_intake", "_params", "active_project",
                          "bootstrapped", "registry", "hook_engine"]
    for k, pages in sorted(shared_keys.items()):
        if any(k.startswith(pat) or k == pat or k.endswith(pat) for pat in high_risk_patterns):
            severity = "MEDIUM"
            desc = (f"Key '{k}' referenced in {len(pages)} pages: {', '.join(sorted(pages))}. "
                    "If written with different types or cleared unexpectedly, cross-page state corruption occurs.")
            findings.append(ConflictFinding(
                check="session_state_collision",
                severity=severity,
                description=desc,
                affected_files=sorted(pages),
                recommendation=(
                    f"Confirm '{k}' is always written with the same type and that page navigations "
                    "cannot leave stale values from a previous workflow run."
                ),
            ))

    if not findings:
        findings.append(ConflictFinding(
            check="session_state_collision",
            severity="INFO",
            description=f"Checked {len(page_keys)} pages. {len(shared_keys)} shared keys found — "
                        "none matched high-risk pattern list.",
            affected_files=[],
            recommendation="No action required.",
        ))

    return findings


# ---------------------------------------------------------------------------
# 2. Hook ordering conflicts
# ---------------------------------------------------------------------------

def check_hook_ordering() -> list[ConflictFinding]:
    findings: list[ConflictFinding] = []

    post_hooks_file = HOOKS_DIR / "post_hooks.py"
    if not post_hooks_file.exists():
        findings.append(ConflictFinding(
            check="hook_ordering",
            severity="MEDIUM",
            description="hooks/post_hooks.py not found — cannot verify hook order.",
            affected_files=["hooks/post_hooks.py"],
            recommendation="Ensure hooks/post_hooks.py exists.",
        ))
        return findings

    text = post_hooks_file.read_text(errors="ignore")

    # Check 1: validate_schema does not include evidence_items field
    if "evidence_items" not in text and "enforce_evidence_chain" in text:
        findings.append(ConflictFinding(
            check="hook_ordering",
            severity="HIGH",
            description=(
                "validate_schema runs BEFORE enforce_evidence_chain. "
                "Schema validation does not include evidence_items. "
                "Result: a JuniorDraft with invalid evidence references passes schema validation, "
                "then enforce_evidence_chain may still catch it — but only for investigation/expert_witness workflows. "
                "For other workflows that set schema_cls without evidence fields, the gap is silent."
            ),
            affected_files=["hooks/post_hooks.py"],
            recommendation=(
                "Add evidence_items to JuniorDraft schema OR add a schema-level check that "
                "finding_chain.supporting_evidence IDs exist in the draft's evidence_items list. "
                "This prevents a 2-phase validation gap."
            ),
        ))

    # Check 2: persist_artifact fires before extract_citations
    persist_line = next((i for i, l in enumerate(text.splitlines()) if "persist_artifact" in l and "def " in l), None)
    citations_line = next((i for i, l in enumerate(text.splitlines()) if "extract_citations" in l and "def " in l), None)
    if persist_line and citations_line and persist_line < citations_line:
        findings.append(ConflictFinding(
            check="hook_ordering",
            severity="MEDIUM",
            description=(
                "persist_artifact (hook N) fires BEFORE extract_citations (hook N+1). "
                "If citation extraction fails (e.g. empty citations list, malformed source_url), "
                "the artifact JSON is already written but citations_index.json is not updated. "
                "Citations are silently lost without pipeline failure."
            ),
            affected_files=["hooks/post_hooks.py"],
            recommendation=(
                "Either: (a) make extract_citations blocking (raise HookVetoError on failure), or "
                "(b) move persist_artifact after extract_citations so citations are written atomically "
                "with the artifact, or (c) add citations to the artifact JSON itself before persist."
            ),
        ))

    # Check 3: non-blocking post-hooks swallow exceptions silently
    silent_hooks = re.findall(r'except\s+Exception[^:]*:\s*\n\s+(?:pass|#|logger)', text)
    if silent_hooks:
        findings.append(ConflictFinding(
            check="hook_ordering",
            severity="LOW",
            description=(
                f"Found {len(silent_hooks)} silent exception swallows in post-hooks. "
                "Non-blocking hooks (render_markdown, generate_arabic_version) catch and suppress all exceptions. "
                "Failures are invisible unless the user inspects _error fields in the artifact."
            ),
            affected_files=["hooks/post_hooks.py"],
            recommendation=(
                "Log silenced exceptions to the audit log (append_audit_event) with severity=WARNING "
                "so they appear in the Activity Log page."
            ),
        ))

    if not findings:
        findings.append(ConflictFinding(
            check="hook_ordering",
            severity="INFO",
            description="Hook ordering checks passed.",
            affected_files=[],
            recommendation="No action required.",
        ))

    return findings


# ---------------------------------------------------------------------------
# 3. State machine reachability
# ---------------------------------------------------------------------------

def check_state_machine_reachability() -> list[ConflictFinding]:
    findings: list[ConflictFinding] = []

    sm_file = CORE_DIR / "state_machine.py"
    if not sm_file.exists():
        findings.append(ConflictFinding(
            check="state_machine_reachability",
            severity="MEDIUM",
            description="core/state_machine.py not found.",
            affected_files=["core/state_machine.py"],
            recommendation="Verify file path.",
        ))
        return findings

    try:
        from core.state_machine import VALID_TRANSITIONS, CaseStatus, TERMINAL_STATUSES

        all_states = set(CaseStatus)
        reachable_from_intake: set = {CaseStatus.INTAKE_CREATED}
        frontier = {CaseStatus.INTAKE_CREATED}
        while frontier:
            next_frontier = set()
            for s in frontier:
                for nxt in VALID_TRANSITIONS.get(s, []):
                    if nxt not in reachable_from_intake:
                        reachable_from_intake.add(nxt)
                        next_frontier.add(nxt)
            frontier = next_frontier

        unreachable = all_states - reachable_from_intake
        if unreachable:
            findings.append(ConflictFinding(
                check="state_machine_reachability",
                severity="MEDIUM",
                description=(
                    f"States unreachable from INTAKE_CREATED: "
                    f"{', '.join(s.value for s in unreachable)}. "
                    "These states can never be entered via valid transitions."
                ),
                affected_files=["core/state_machine.py"],
                recommendation="Either add a transition path or remove unreachable states from the enum.",
            ))

        # Check PIPELINE_ERROR has no outgoing transitions
        if CaseStatus.PIPELINE_ERROR in VALID_TRANSITIONS:
            findings.append(ConflictFinding(
                check="state_machine_reachability",
                severity="HIGH",
                description=(
                    "PIPELINE_ERROR has outgoing transitions defined. "
                    "It is marked as terminal but can be exited — inconsistency."
                ),
                affected_files=["core/state_machine.py"],
                recommendation="Remove outgoing transitions from PIPELINE_ERROR.",
            ))

        # Check PIPELINE_ERROR not in TERMINAL_STATUSES
        if CaseStatus.PIPELINE_ERROR not in TERMINAL_STATUSES:
            findings.append(ConflictFinding(
                check="state_machine_reachability",
                severity="HIGH",
                description="PIPELINE_ERROR not in TERMINAL_STATUSES — resume logic may attempt to continue a failed pipeline.",
                affected_files=["core/state_machine.py", "core/orchestrator.py"],
                recommendation="Add PIPELINE_ERROR to TERMINAL_STATUSES.",
            ))

        # Check OWNER_REJECTED has outgoing path to JUNIOR_DRAFT_COMPLETE
        rejected_transitions = VALID_TRANSITIONS.get(CaseStatus.OWNER_REJECTED, [])
        if CaseStatus.JUNIOR_DRAFT_COMPLETE not in rejected_transitions:
            findings.append(ConflictFinding(
                check="state_machine_reachability",
                severity="MEDIUM",
                description=(
                    "OWNER_REJECTED does not transition to JUNIOR_DRAFT_COMPLETE. "
                    "Owner rejection has no recovery path — pipeline is permanently blocked."
                ),
                affected_files=["core/state_machine.py"],
                recommendation="Add OWNER_REJECTED → JUNIOR_DRAFT_COMPLETE transition for rejection recovery.",
            ))

        if len(findings) == 0:
            findings.append(ConflictFinding(
                check="state_machine_reachability",
                severity="INFO",
                description=f"State machine reachability OK. {len(all_states)} states, all reachable from INTAKE_CREATED.",
                affected_files=[],
                recommendation="No action required.",
            ))

    except ImportError as e:
        findings.append(ConflictFinding(
            check="state_machine_reachability",
            severity="MEDIUM",
            description=f"Could not import state_machine: {e}",
            affected_files=["core/state_machine.py"],
            recommendation="Ensure core/state_machine.py is importable.",
        ))

    return findings


# ---------------------------------------------------------------------------
# 4. Model routing consistency
# ---------------------------------------------------------------------------

def check_model_routing() -> list[ConflictFinding]:
    findings: list[ConflictFinding] = []

    try:
        from config import MODEL_ROUTING, WORKFLOW_MODEL_OVERRIDES, get_model, HAIKU, SONNET, OPUS

        known_models = {HAIKU, SONNET, OPUS}
        known_roles = set()
        for tier, role_map in MODEL_ROUTING.items():
            known_roles.update(role_map.keys())

        # Check overrides only touch partner role
        for wf, overrides in WORKFLOW_MODEL_OVERRIDES.items():
            for role, model in overrides.items():
                if model not in known_models:
                    findings.append(ConflictFinding(
                        check="model_routing",
                        severity="HIGH",
                        description=f"WORKFLOW_MODEL_OVERRIDES['{wf}']['{role}'] = '{model}' is not a known model ID.",
                        affected_files=["config.py"],
                        recommendation=f"Update model ID to one of: {', '.join(sorted(known_models))}",
                    ))
                if role not in known_roles:
                    findings.append(ConflictFinding(
                        check="model_routing",
                        severity="MEDIUM",
                        description=f"WORKFLOW_MODEL_OVERRIDES['{wf}'] uses role '{role}' not in MODEL_ROUTING keys: {sorted(known_roles)}",
                        affected_files=["config.py"],
                        recommendation="Use a role key that matches MODEL_ROUTING.",
                    ))

        # Check PluginManifest.role values match MODEL_ROUTING keys
        agents_dir = _ROOT / "agents"
        personas_dir = _ROOT / "personas"
        for manifest_dir in [agents_dir, personas_dir]:
            if not manifest_dir.exists():
                continue
            for f in manifest_dir.rglob("manifest.json"):
                import json
                try:
                    data = json.loads(f.read_text())
                    role = data.get("role", "")
                    if role and role not in known_roles:
                        findings.append(ConflictFinding(
                            check="model_routing",
                            severity="HIGH",
                            description=(
                                f"Plugin manifest {f.relative_to(_ROOT)} has role='{role}' "
                                f"which is NOT in MODEL_ROUTING keys: {sorted(known_roles)}. "
                                "get_model() will fall back silently to a default model."
                            ),
                            affected_files=[str(f.relative_to(_ROOT))],
                            recommendation=f"Fix role in manifest to one of: {sorted(known_roles)}",
                        ))
                except Exception:
                    pass

    except ImportError as e:
        findings.append(ConflictFinding(
            check="model_routing",
            severity="MEDIUM",
            description=f"Could not import config: {e}",
            affected_files=["config.py"],
            recommendation="Ensure config.py is importable.",
        ))

    if not findings:
        findings.append(ConflictFinding(
            check="model_routing",
            severity="INFO",
            description="Model routing consistency check passed.",
            affected_files=[],
            recommendation="No action required.",
        ))

    return findings


# ---------------------------------------------------------------------------
# 5. Schema compatibility audit
# ---------------------------------------------------------------------------

def check_schema_compatibility() -> list[ConflictFinding]:
    findings: list[ConflictFinding] = []

    try:
        from schemas.artifacts import JuniorDraft, FinalDeliverable, RiskItem
        import pydantic

        # JuniorDraft.risk_rating computed validator: likelihood=0, impact=0
        try:
            ri = RiskItem(
                risk_id="R-000",
                category="test",
                title="Zero risk",
                description="test",
                likelihood=0,
                impact=0,
            )
            if ri.risk_rating == 0:
                findings.append(ConflictFinding(
                    check="schema_compatibility",
                    severity="LOW",
                    description=(
                        "RiskItem allows likelihood=0 AND impact=0 → risk_rating=0. "
                        "A 'zero risk' item is semantically invalid (no risk with zero likelihood × zero impact) "
                        "but passes schema validation. Risk register could include ghost entries."
                    ),
                    affected_files=["schemas/artifacts.py"],
                    recommendation=(
                        "Add a model_validator that requires likelihood >= 1 and impact >= 1, "
                        "or add a warning annotation when risk_rating == 0."
                    ),
                ))
        except Exception:
            pass

        # FinalDeliverable: content_en must not be None
        try:
            fd = FinalDeliverable(
                case_id="TEST-001",
                workflow="test",
                approved_by="partner",
                language="en",
                content_en=None,   # type: ignore
                citations=[],
                revision_history=[],
                delivery_date="2026-04-21",
            )
            findings.append(ConflictFinding(
                check="schema_compatibility",
                severity="HIGH",
                description=(
                    "FinalDeliverable accepts content_en=None without raising ValidationError. "
                    "A deliverable with null content could be written to disk and delivered."
                ),
                affected_files=["schemas/artifacts.py"],
                recommendation="Add `content_en: str` with `min_length=1` constraint.",
            ))
        except Exception:
            pass  # Schema correctly rejects None — good

    except ImportError as e:
        findings.append(ConflictFinding(
            check="schema_compatibility",
            severity="MEDIUM",
            description=f"Could not import schemas: {e}",
            affected_files=["schemas/artifacts.py"],
            recommendation="Ensure schemas/artifacts.py is importable.",
        ))

    try:
        from schemas.evidence import EvidenceItem, FindingChain
        # EvidenceItem.source_excerpt empty string
        try:
            ei = EvidenceItem(
                evidence_id="E-001",
                case_id="TEST-001",
                source_doc_id="DOC-001",
                source_excerpt="",    # empty
                evidence_type="documentary",
                description="test",
                permissibility="permissible",
                provenance="test",
                usability="usable",
            )
            findings.append(ConflictFinding(
                check="schema_compatibility",
                severity="MEDIUM",
                description=(
                    "EvidenceItem accepts source_excerpt='' (empty string). "
                    "Evidence with no excerpt has no factual basis but passes schema validation. "
                    "enforce_evidence_chain may accept it as valid evidence."
                ),
                affected_files=["schemas/evidence.py"],
                recommendation="Add `min_length=10` constraint on source_excerpt.",
            ))
        except Exception:
            pass

    except ImportError:
        pass

    if not findings:
        findings.append(ConflictFinding(
            check="schema_compatibility",
            severity="INFO",
            description="Schema compatibility checks passed.",
            affected_files=[],
            recommendation="No action required.",
        ))

    return findings


# ---------------------------------------------------------------------------
# 6. Revision credit accounting
# ---------------------------------------------------------------------------

def check_revision_credit_accounting() -> list[ConflictFinding]:
    findings: list[ConflictFinding] = []

    orch_file = CORE_DIR / "orchestrator.py"
    if not orch_file.exists():
        findings.append(ConflictFinding(
            check="revision_credit",
            severity="MEDIUM",
            description="core/orchestrator.py not found.",
            affected_files=["core/orchestrator.py"],
            recommendation="Verify file path.",
        ))
        return findings

    text = orch_file.read_text(errors="ignore")

    # Check: PM revision increments junior counter
    if 'revision_counts["junior"]' not in text and "revision_counts['junior']" not in text:
        findings.append(ConflictFinding(
            check="revision_credit",
            severity="HIGH",
            description=(
                "orchestrator.py does not reference revision_counts['junior'] — "
                "junior revision rounds may not be tracked, allowing unlimited junior re-runs."
            ),
            affected_files=["core/orchestrator.py"],
            recommendation="Verify _run_junior() increments revision_counts['junior'] on each loop iteration.",
        ))

    # Check: PM feedback injected into junior context on revision
    if "feedback" not in text.lower() and "revision_feedback" not in text.lower():
        findings.append(ConflictFinding(
            check="revision_credit",
            severity="MEDIUM",
            description=(
                "No evidence that PM feedback is injected into Junior's context on revision runs. "
                "Junior may re-run without knowing WHY revision was requested — "
                "leading to identical output and wasted revision rounds."
            ),
            affected_files=["core/orchestrator.py"],
            recommendation=(
                "In _run_pm() revision branch, add PM's revision_reason to the context dict "
                "passed back to _run_junior() on next iteration."
            ),
        ))

    # Check: RevisionLimitError defined and raised
    if "RevisionLimitError" not in text:
        findings.append(ConflictFinding(
            check="revision_credit",
            severity="HIGH",
            description=(
                "RevisionLimitError not found in orchestrator.py. "
                "Revision limit exhaustion may be silently ignored."
            ),
            affected_files=["core/orchestrator.py"],
            recommendation="Ensure RevisionLimitError is defined and raised when max rounds exceeded.",
        ))

    if not findings:
        findings.append(ConflictFinding(
            check="revision_credit",
            severity="INFO",
            description="Revision credit accounting checks passed.",
            affected_files=[],
            recommendation="No action required.",
        ))

    return findings


# ---------------------------------------------------------------------------
# Run all checks
# ---------------------------------------------------------------------------

def run_conflict_detection() -> dict[str, list[ConflictFinding]]:
    return {
        "session_state":     check_session_state_collisions(),
        "hook_ordering":     check_hook_ordering(),
        "state_machine":     check_state_machine_reachability(),
        "model_routing":     check_model_routing(),
        "schema_compat":     check_schema_compatibility(),
        "revision_credit":   check_revision_credit_accounting(),
    }

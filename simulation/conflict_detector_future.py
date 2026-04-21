"""
Future-direction conflict detector.

Checks for architectural gaps specific to planned/unbuilt features:
  1. st.navigation() path resolution — all registered paths must exist
  2. Multi-workflow slug collision — two workflows can produce same artifact filename
  3. Bootstrap redirect loop — 00_Setup.py / app.py infinite redirect
  4. Template validation — .docx template files exist + have required named styles
  5. Knowledge harvester PII filter — no PII sanitisation in harvest path
  6. Workpaper promotion audit chain — audit_log.jsonl must exist before promotion
  7. Co-Work / multi-tenant state file locking — concurrent writes to state.json
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

PAGES_DIR     = _ROOT / "pages"
TEMPLATES_DIR = _ROOT / "templates"
CORE_DIR      = _ROOT / "core"
HOOKS_DIR     = _ROOT / "hooks"
DOCS_DIR      = _ROOT / "docs"


@dataclass
class FutureConflictFinding:
    check: str
    severity: str   # "HIGH" | "MEDIUM" | "LOW" | "INFO"
    area: str       # "navigation" | "slug" | "bootstrap" | "template" | "pii" | "audit" | "locking"
    description: str
    affected_files: list[str]
    recommendation: str
    sprint_ref: str = ""   # e.g. "Sprint-IA-01 IA-01"


# ---------------------------------------------------------------------------
# 1. st.navigation() path resolution
# ---------------------------------------------------------------------------

def check_navigation_paths() -> list[FutureConflictFinding]:
    """
    Sprint-IA-01/IA-02: The redesign replaces auto-registered pages/ with explicit
    st.navigation(). Any path listed in the navigation config that doesn't match an
    existing page file will silently return a 404-equivalent at runtime.
    """
    findings: list[FutureConflictFinding] = []

    app_py = _ROOT / "app.py"
    if not app_py.exists():
        findings.append(FutureConflictFinding(
            check="navigation_paths", severity="MEDIUM", area="navigation",
            description="app.py not found — cannot verify st.navigation() paths.",
            affected_files=["app.py"],
            recommendation="Ensure app.py exists and implements st.navigation().",
            sprint_ref="Sprint-IA-01 IA-02",
        ))
        return findings

    app_text = app_py.read_text(errors="ignore")

    # Detect st.navigation() usage
    uses_navigation = "st.navigation" in app_text or "Navigation" in app_text

    if not uses_navigation:
        findings.append(FutureConflictFinding(
            check="navigation_paths", severity="INFO", area="navigation",
            description=(
                "app.py does not yet use st.navigation() — still on auto-registered pages/ "
                "convention. IA-02 restructure has not been applied. "
                "No path resolution risk until IA-02 lands."
            ),
            affected_files=["app.py"],
            recommendation="Post-IA-02: add check that all st.Page() paths resolve to existing files.",
            sprint_ref="Sprint-IA-01 IA-02",
        ))
        return findings

    # If st.navigation() is present, verify referenced paths exist
    # Pattern: st.Page("path/to/file.py", ...) or st.Page(path_var)
    page_refs = re.findall(r'st\.Page\(\s*["\']([^"\']+\.py)["\']', app_text)
    missing_paths = []
    for ref in page_refs:
        full = _ROOT / ref
        if not full.exists():
            missing_paths.append(ref)

    if missing_paths:
        findings.append(FutureConflictFinding(
            check="navigation_paths", severity="HIGH", area="navigation",
            description=(
                f"st.navigation() references {len(missing_paths)} page path(s) that do not exist: "
                f"{', '.join(missing_paths[:5])}. "
                "At startup, Streamlit will raise FileNotFoundError or show a blank navigation."
            ),
            affected_files=["app.py"] + missing_paths,
            recommendation=(
                "Ensure all st.Page() paths point to existing files. "
                "Add a startup smoke-test: `python -c 'import app'` in CI."
            ),
            sprint_ref="Sprint-IA-01 IA-02",
        ))
    else:
        findings.append(FutureConflictFinding(
            check="navigation_paths", severity="INFO", area="navigation",
            description=(
                f"st.navigation() found in app.py. "
                f"{len(page_refs)} page paths verified — all exist."
                if page_refs else
                "st.navigation() present but no st.Page() string literals found — verify dynamic paths."
            ),
            affected_files=["app.py"],
            recommendation="No action required." if page_refs else
                           "Verify dynamic page path resolution at runtime.",
            sprint_ref="Sprint-IA-01 IA-02",
        ))

    return findings


# ---------------------------------------------------------------------------
# 2. Multi-workflow slug collision
# ---------------------------------------------------------------------------

def check_slug_collision_risk() -> list[FutureConflictFinding]:
    """
    When multiple workflow types run under one case_id, their artifact filenames
    must be unique. If two workflows share the same agent name and version,
    artifact N from workflow A silently overwrites artifact N from workflow B.
    """
    findings: list[FutureConflictFinding] = []

    artifacts_py = _ROOT / "schemas" / "artifacts.py"
    project_py   = _ROOT / "schemas" / "project.py"

    # Check: does artifact naming include workflow slug or just agent name?
    if artifacts_py.exists():
        text = artifacts_py.read_text(errors="ignore")
        has_workflow_in_slug = "workflow" in text.lower() and ("slug" in text.lower() or
                                                                "artifact_id" in text.lower())
        if not has_workflow_in_slug:
            findings.append(FutureConflictFinding(
                check="slug_collision", severity="HIGH", area="slug",
                description=(
                    "Artifact filenames appear to be named by agent + version only "
                    "(e.g. junior_output.v1.json). "
                    "When two workflow types run under the same case_id "
                    "(AUP Type 8 can host multiple workstreams), "
                    "workflow A's junior_output.v1.json overwrites workflow B's silently. "
                    "Confirmed risk from BA-IA-03 (min 1 workstream per engagement)."
                ),
                affected_files=["schemas/artifacts.py", "core/orchestrator.py"],
                recommendation=(
                    "Prefix artifact filenames with workflow slug: "
                    "{workflow}_{agent}_output.v{N}.json "
                    "(e.g. aup_investigation_junior_output.v1.json). "
                    "Update persist_artifact hook and orchestrator to use workflow-scoped paths."
                ),
                sprint_ref="Sprint-IA-01 IA-03",
            ))

    # Check: derive_slug exists and handles multi-word workflow names
    if project_py.exists():
        text = project_py.read_text(errors="ignore")
        if "derive_slug" in text:
            # Verify slug handles workflow names with underscores (aup_investigation → safe slug)
            findings.append(FutureConflictFinding(
                check="slug_collision", severity="INFO", area="slug",
                description=(
                    "derive_slug() found in schemas/project.py. "
                    "Verify it handles new workflow names (aup_investigation, custom_investigation, "
                    "expert_witness_report) without producing duplicate slugs for different inputs."
                ),
                affected_files=["schemas/project.py"],
                recommendation="Add slug uniqueness test for all future workflow names.",
                sprint_ref="Sprint-IA-01",
            ))
        else:
            findings.append(FutureConflictFinding(
                check="slug_collision", severity="MEDIUM", area="slug",
                description="derive_slug() not found in schemas/project.py.",
                affected_files=["schemas/project.py"],
                recommendation="Verify slug generation function exists and handles all workflow names.",
                sprint_ref="Sprint-IA-01",
            ))

    return findings


# ---------------------------------------------------------------------------
# 3. Bootstrap redirect loop
# ---------------------------------------------------------------------------

def check_bootstrap_redirect() -> list[FutureConflictFinding]:
    """
    IA-01 fix adds try/except + caller_file=__file__ to app.py bootstrap.
    Risk: if the fix is incomplete, a first-run user without firm_profile/
    hits a redirect to 00_Setup.py which itself calls bootstrap(), triggering
    another redirect — infinite loop until browser tab becomes unresponsive.
    """
    findings: list[FutureConflictFinding] = []

    app_py = _ROOT / "app.py"
    setup_pages = list(PAGES_DIR.glob("*[Ss]etup*.py")) if PAGES_DIR.exists() else []
    setup_page = setup_pages[0] if setup_pages else None

    if not app_py.exists():
        findings.append(FutureConflictFinding(
            check="bootstrap_redirect", severity="MEDIUM", area="bootstrap",
            description="app.py not found.",
            affected_files=["app.py"],
            recommendation="Ensure app.py exists.",
            sprint_ref="Sprint-IA-01 IA-01",
        ))
        return findings

    app_text = app_py.read_text(errors="ignore")

    # Check 1: bootstrap() inside try/except
    has_try_bootstrap = re.search(r'try\s*:\s*\n.*bootstrap', app_text, re.DOTALL)
    if not has_try_bootstrap:
        # Could be on same line
        has_try_bootstrap = "try:" in app_text and "bootstrap" in app_text

    if not has_try_bootstrap:
        findings.append(FutureConflictFinding(
            check="bootstrap_redirect", severity="HIGH", area="bootstrap",
            description=(
                "app.py calls bootstrap() without a try/except wrapper. "
                "If bootstrap() raises (missing firm_profile/, first-run), Streamlit shows a "
                "blank error page. Combined with an unconditional redirect to 00_Setup.py, "
                "this can produce an infinite redirect loop on first-run installs."
            ),
            affected_files=["app.py"],
            recommendation=(
                "Wrap bootstrap() in try/except ImportError/FileNotFoundError. "
                "On exception, render a setup prompt directly rather than redirect. "
                "Pass caller_file=__file__ to prevent recursive bootstrap calls."
            ),
            sprint_ref="Sprint-IA-01 IA-01",
        ))

    # Check 2: setup page also calls bootstrap
    if setup_page:
        setup_text = setup_page.read_text(errors="ignore")
        if "bootstrap" in setup_text:
            findings.append(FutureConflictFinding(
                check="bootstrap_redirect", severity="HIGH", area="bootstrap",
                description=(
                    f"{setup_page.name} calls bootstrap() AND app.py calls bootstrap(). "
                    "If app.py redirects to setup on bootstrap failure, and setup itself "
                    "calls bootstrap(), the redirect chain becomes circular. "
                    "First-run users will hit a loop."
                ),
                affected_files=["app.py", str(setup_page.relative_to(_ROOT))],
                recommendation=(
                    "Setup page must NOT call bootstrap(). "
                    "Only app.py initialises the session. "
                    "Setup page should write firm_profile/, then call st.rerun() once."
                ),
                sprint_ref="Sprint-IA-01 IA-01",
            ))

    if len(findings) == 0:
        findings.append(FutureConflictFinding(
            check="bootstrap_redirect", severity="INFO", area="bootstrap",
            description="Bootstrap redirect checks passed.",
            affected_files=[],
            recommendation="No action required.",
            sprint_ref="Sprint-IA-01 IA-01",
        ))

    return findings


# ---------------------------------------------------------------------------
# 4. Template validation (.docx)
# ---------------------------------------------------------------------------

def check_template_validation() -> list[FutureConflictFinding]:
    """
    Custom/AUP investigation types allow user-supplied .docx templates.
    Risk: template missing required named paragraph styles (Heading1, Heading2,
    BodyText, TableHeader) → python-docx raises KeyError at artifact generation.
    This surfaces as a cryptic PIPELINE_ERROR rather than a user-facing message.
    """
    findings: list[FutureConflictFinding] = []

    # Check: templates directory exists
    if not TEMPLATES_DIR.exists():
        findings.append(FutureConflictFinding(
            check="template_validation", severity="MEDIUM", area="template",
            description=(
                "templates/ directory not found. "
                "Custom Investigation (Type 9) requires .docx template files. "
                "Missing directory means the feature cannot ship without it."
            ),
            affected_files=["templates/"],
            recommendation="Create templates/ directory with at least one reference .docx template.",
            sprint_ref="Sprint-IA-02",
        ))
        return findings

    docx_templates = list(TEMPLATES_DIR.glob("*.docx"))

    if not docx_templates:
        findings.append(FutureConflictFinding(
            check="template_validation", severity="HIGH", area="template",
            description=(
                "templates/ directory exists but contains no .docx files. "
                "Any workflow that calls python-docx with a template path will raise FileNotFoundError."
            ),
            affected_files=["templates/"],
            recommendation=(
                "Add at least one reference .docx template for each investigation type. "
                "Add a validation step at intake that checks the template file exists "
                "before the pipeline starts."
            ),
            sprint_ref="Sprint-IA-02",
        ))
    else:
        # Check if template loading code validates named styles
        core_files = list(CORE_DIR.glob("*.py")) + list(_ROOT.glob("tools/*.py"))
        style_validation_found = False
        for f in core_files:
            text = f.read_text(errors="ignore")
            if "styles" in text and ("template" in text.lower() or "docx" in text.lower()):
                style_validation_found = True
                break

        if not style_validation_found:
            findings.append(FutureConflictFinding(
                check="template_validation", severity="MEDIUM", area="template",
                description=(
                    f"Found {len(docx_templates)} .docx template(s) in templates/ but "
                    "no code found that validates named paragraph styles before use. "
                    "A user-supplied template missing 'Heading 1' or 'Body Text' styles "
                    "will crash python-docx with a KeyError during artifact generation."
                ),
                affected_files=["templates/", "tools/"],
                recommendation=(
                    "Add template validation at intake: open template with python-docx, "
                    "check required style names exist, surface a friendly error if not. "
                    "Required styles: Heading 1, Heading 2, Body Text (or equivalents from "
                    "the firm's template set)."
                ),
                sprint_ref="Sprint-IA-02",
            ))
        else:
            findings.append(FutureConflictFinding(
                check="template_validation", severity="INFO", area="template",
                description=f"Found {len(docx_templates)} template(s) and style validation code.",
                affected_files=[],
                recommendation="No action required.",
                sprint_ref="Sprint-IA-02",
            ))

    return findings


# ---------------------------------------------------------------------------
# 5. Knowledge harvester PII filter
# ---------------------------------------------------------------------------

def check_knowledge_pii_filter() -> list[FutureConflictFinding]:
    """
    The knowledge harvester extracts patterns from completed case artifacts to build
    the firm's knowledge library. Risk: if client names, case IDs, or entity names
    are not stripped before storing harvested patterns, PII from one case could be
    surfaced in another case's output.
    """
    findings: list[FutureConflictFinding] = []

    # Look for knowledge harvester code
    knowledge_dir = _ROOT / "knowledge"
    harvester_candidates = []
    for pattern in ["*harvest*", "*knowledge_lib*", "*pattern_store*"]:
        harvester_candidates.extend(list(_ROOT.rglob(pattern)))

    if not harvester_candidates:
        findings.append(FutureConflictFinding(
            check="knowledge_pii_filter", severity="HIGH", area="pii",
            description=(
                "No knowledge harvester code found (knowledge_harvester, pattern_store). "
                "This feature is planned but not yet implemented. "
                "When built, it MUST include PII stripping before writing to the knowledge library: "
                "client names, case IDs, entity names, and financial figures must all be "
                "abstracted to anonymised placeholders (e.g. [CLIENT_A], [ENTITY_1])."
            ),
            affected_files=["knowledge/"],
            recommendation=(
                "Implement knowledge harvester with mandatory PII filter as a pre-write hook: "
                "(1) strip proper nouns matching case manifest entity list, "
                "(2) replace numeric amounts >10,000 with [AMOUNT], "
                "(3) strip case_id prefixes from all extracted patterns, "
                "(4) require human review gate before patterns enter the shared library."
            ),
            sprint_ref="Sprint-IA-02 (future)",
        ))
        return findings

    # If code exists, check for PII sanitisation
    pii_check_found = False
    for path in harvester_candidates:
        if path.is_file():
            text = path.read_text(errors="ignore")
            if "sanitize" in text.lower() or "pii" in text.lower() or "strip" in text.lower():
                pii_check_found = True
                break

    if not pii_check_found:
        findings.append(FutureConflictFinding(
            check="knowledge_pii_filter", severity="HIGH", area="pii",
            description=(
                "Knowledge harvester code exists but no PII sanitisation step found. "
                "Harvested patterns may contain client names, entity references, or case IDs "
                "that leak across engagements when the knowledge library is used in other cases."
            ),
            affected_files=[str(p.relative_to(_ROOT)) for p in harvester_candidates if p.is_file()],
            recommendation=(
                "Add PII stripping (sanitize_pii or equivalent) to the harvest pipeline "
                "before any pattern is written to the shared knowledge library."
            ),
            sprint_ref="Sprint-IA-02 (future)",
        ))
    else:
        findings.append(FutureConflictFinding(
            check="knowledge_pii_filter", severity="INFO", area="pii",
            description="Knowledge harvester with PII sanitisation found.",
            affected_files=[],
            recommendation="No action required. Verify IBAN and null-byte gaps are also covered.",
            sprint_ref="Sprint-IA-02 (future)",
        ))

    return findings


# ---------------------------------------------------------------------------
# 6. Workpaper promotion audit chain
# ---------------------------------------------------------------------------

def check_workpaper_audit_chain() -> list[FutureConflictFinding]:
    """
    When a workpaper is promoted to a reviewed artifact, the promotion event must
    be appended to audit_log.jsonl. If the audit log doesn't exist (new case, or
    log was never initialised), the promotion fails with a FileNotFoundError,
    blocking the consultant with no recovery path.
    """
    findings: list[FutureConflictFinding] = []

    post_hooks_file = HOOKS_DIR / "post_hooks.py"
    if not post_hooks_file.exists():
        findings.append(FutureConflictFinding(
            check="workpaper_audit_chain", severity="MEDIUM", area="audit",
            description="hooks/post_hooks.py not found — cannot verify audit chain.",
            affected_files=["hooks/post_hooks.py"],
            recommendation="Ensure hooks/post_hooks.py exists.",
            sprint_ref="Sprint-IA-01 (workpaper)",
        ))
        return findings

    text = post_hooks_file.read_text(errors="ignore")

    # Check: append_audit_event creates the log file if it doesn't exist
    # Pattern: open with "a" or pathlib.Path.open("a") creates the file on first write
    # Risk: if open("w") is used, it would CLEAR the log; if open("a") fails on missing
    # parent dir, it raises FileNotFoundError
    creates_audit_log = "open" in text and ("append" in text.lower() or '"a"' in text or "'a'" in text)
    makes_parent = "mkdir" in text and "parent" in text

    if not makes_parent:
        findings.append(FutureConflictFinding(
            check="workpaper_audit_chain", severity="MEDIUM", area="audit",
            description=(
                "append_audit_event in post_hooks.py does not appear to call mkdir(parents=True) "
                "before opening audit_log.jsonl. "
                "If the case directory doesn't exist yet (new case, workpaper promotion before "
                "first pipeline run), FileNotFoundError will block promotion with no recovery path."
            ),
            affected_files=["hooks/post_hooks.py"],
            recommendation=(
                "In append_audit_event, add: "
                "`audit_path.parent.mkdir(parents=True, exist_ok=True)` "
                "before opening the log file. This makes audit log creation idempotent."
            ),
            sprint_ref="Sprint-IA-01 (workpaper)",
        ))
    else:
        findings.append(FutureConflictFinding(
            check="workpaper_audit_chain", severity="INFO", area="audit",
            description="append_audit_event creates parent directory — audit chain appears safe.",
            affected_files=[],
            recommendation="No action required.",
            sprint_ref="Sprint-IA-01 (workpaper)",
        ))

    return findings


# ---------------------------------------------------------------------------
# 7. Co-Work / multi-tenant state file locking
# ---------------------------------------------------------------------------

def check_state_file_locking() -> list[FutureConflictFinding]:
    """
    Co-Work (two consultants editing same case) and multi-tenant workstreams
    both require concurrent writes to state.json and artifact files.
    Current implementation uses atomic os.replace() — safe for single-writer,
    but concurrent writers produce a last-write-wins race condition.
    """
    findings: list[FutureConflictFinding] = []

    # Check orchestrator and file_tools for locking primitives
    orch_file = CORE_DIR / "orchestrator.py"
    tools_file = _ROOT / "tools" / "file_tools.py"

    has_locking = False
    for f in [orch_file, tools_file]:
        if f.exists():
            text = f.read_text(errors="ignore")
            if any(kw in text for kw in ["fcntl", "filelock", "FileLock", "portalocker",
                                          "threading.Lock", "asyncio.Lock"]):
                has_locking = True
                break

    if not has_locking:
        findings.append(FutureConflictFinding(
            check="state_file_locking", severity="HIGH", area="locking",
            description=(
                "No file locking primitives found in orchestrator.py or tools/file_tools.py. "
                "Current atomic write uses os.replace() — safe for single-writer scenarios. "
                "Co-Work model (Model 3) and multi-tenant SaaS (Model 5) both require "
                "concurrent writes to state.json. Without locking: "
                "(1) two consultants writing state.json simultaneously → last write wins, "
                "one consultant's status update silently overwritten; "
                "(2) two tenant pipelines sharing filesystem → state corruption across tenants."
            ),
            affected_files=["core/orchestrator.py", "tools/file_tools.py"],
            recommendation=(
                "For Co-Work/multi-tenant: add advisory file locking via `filelock` library. "
                "Pattern: `with FileLock(state_path.with_suffix('.lock')):` around all state reads "
                "and writes. For single-user (Models 1, 2), existing os.replace() is sufficient. "
                "Gate behind a config flag: ENABLE_FILE_LOCKING = (SHIPPING_MODEL in ('co_work', 'saas'))."
            ),
            sprint_ref="Sprint-IA-02 (co-work / shipping models 3+)",
        ))
    else:
        findings.append(FutureConflictFinding(
            check="state_file_locking", severity="INFO", area="locking",
            description="File locking primitives found in core code.",
            affected_files=[],
            recommendation="Verify locking scope covers state.json AND audit_log.jsonl writes.",
            sprint_ref="Sprint-IA-02 (co-work)",
        ))

    return findings


# ---------------------------------------------------------------------------
# Run all future conflict checks
# ---------------------------------------------------------------------------

def run_future_conflict_detection() -> dict[str, list[FutureConflictFinding]]:
    return {
        "navigation_paths":     check_navigation_paths(),
        "slug_collision":       check_slug_collision_risk(),
        "bootstrap_redirect":   check_bootstrap_redirect(),
        "template_validation":  check_template_validation(),
        "knowledge_pii_filter": check_knowledge_pii_filter(),
        "workpaper_audit_chain":check_workpaper_audit_chain(),
        "state_file_locking":   check_state_file_locking(),
    }

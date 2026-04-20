import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR         = Path(__file__).parent
CASES_DIR        = BASE_DIR / os.getenv("CASES_DIR", "cases")
SOPS_DIR         = BASE_DIR / "sops"
TEMPLATES_DIR    = BASE_DIR / "templates"
KNOWLEDGE_DIR    = BASE_DIR / "knowledge"
FIRM_PROFILE_DIR = BASE_DIR / "firm_profile"

CASES_DIR.mkdir(exist_ok=True)
SOPS_DIR.mkdir(exist_ok=True)

# ── API Keys ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TAVILY_API_KEY    = os.getenv("TAVILY_API_KEY", "")

# ── Research Mode ─────────────────────────────────────────────────────────────
# "knowledge_only" (default): all research tools return stub results immediately.
#   No network calls. Pipeline runs on model knowledge + knowledge-base files.
#   Use this for dev, demo, and any environment where Tavily is unavailable.
# "live": Tavily API is called for web/regulatory/sanctions/company lookups.
#   Requires a valid TAVILY_API_KEY. Set in .env: RESEARCH_MODE=live
RESEARCH_MODE = os.getenv("RESEARCH_MODE", "live" if os.getenv("TAVILY_API_KEY") else "knowledge_only")

# ── Models ────────────────────────────────────────────────────────────────────
HAIKU  = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-4-6"
OPUS   = "claude-opus-4-6"

MODEL_ROUTING = {
    "economy":  {"junior": HAIKU,   "pm": HAIKU,   "partner": SONNET, "persona": HAIKU},
    "balanced": {"junior": HAIKU,   "pm": SONNET,  "partner": SONNET, "persona": SONNET},
    "premium":  {"junior": SONNET,  "pm": SONNET,  "partner": OPUS,   "persona": SONNET},
}

WORKFLOW_MODEL_OVERRIDES = {
    "frm_risk_register":     {"partner": OPUS},
    "expert_witness_report": {"partner": OPUS},
}

MODEL_FALLBACK = {OPUS: SONNET, SONNET: HAIKU}

# ── Budget / Research ─────────────────────────────────────────────────────────
BUDGET_MODE         = os.getenv("BUDGET_MODE", "balanced")
USE_CACHED_RESEARCH = os.getenv("USE_CACHED_RESEARCH", "false").lower() == "true"

# ── Retry ─────────────────────────────────────────────────────────────────────
MAX_API_RETRIES       = 3
RETRY_BACKOFF_SECONDS = [1, 3, 10]

# ── Guardrails ────────────────────────────────────────────────────────────────
MAX_RESEARCH_EXCERPT_CHARS = 2000   # truncate web content (anti prompt-injection)
MAX_REVISION_ROUNDS = {"junior": 3, "pm": 2}

# ── Document retrieval budget ─────────────────────────────────────────────────
DOC_EXCERPT_CHARS     = 8_000
DOC_SECTION_MAX_CHARS = 60_000
SMALL_DOC_THRESHOLD   = 20_000   # chars — full read permitted below this

# ── Conversational Evidence Mode (CEM) ────────────────────────────────────────
# Max chars of document context injected per EvidenceChat turn (CONV-01).
# Oldest turns are dropped first when the conversation history approaches this cap.
CEM_CONTEXT_CHARS = 16_000

# ── Context accumulation budget (P9-06) ──────────────────────────────────────
CONTEXT_BUDGET_CHARS = 400_000  # ≈ 100k tokens, conservative for 200k window

# ── Jurisdiction registry — loaded from taxonomy JSON ─────────────────────────
def _load_jurisdiction_registry() -> dict[str, dict]:
    import json
    _path = BASE_DIR / "knowledge" / "taxonomy" / "jurisdictions.json"
    try:
        data = json.loads(_path.read_text(encoding="utf-8"))
        return data.get("jurisdictions", {})
    except Exception:
        # Fallback: hardcoded UAE only — prevents startup failure if file missing
        return {
            "UAE": {
                "regulators": ["CBUAE", "DFSA", "ADGM", "SCA", "FSRA"],
                "domains": ["cb.gov.ae", "dfsa.ae", "adgm.com", "sca.gov.ae", "fsra.ae"],
                "company_registries": ["dc.gov.ae", "added.gov.ae", "mohre.gov.ae"],
            }
        }

JURISDICTION_REGISTRY: dict[str, dict] = _load_jurisdiction_registry()


def get_jurisdiction_domains(jurisdictions: list[str] | None = None) -> list[str]:
    """Return flat deduplicated domain list for given jurisdictions. Default UAE."""
    if not jurisdictions:
        jurisdictions = ["UAE"]
    seen: set[str] = set()
    result: list[str] = []
    for j in jurisdictions:
        entry = JURISDICTION_REGISTRY.get(j, {})
        for d in entry.get("domains", []):
            if d not in seen:
                seen.add(d)
                result.append(d)
    return result or JURISDICTION_REGISTRY["UAE"]["domains"]


def get_jurisdiction_company_domains(jurisdictions: list[str] | None = None) -> list[str]:
    """Return flat deduplicated company registry domain list for given jurisdictions."""
    if not jurisdictions:
        jurisdictions = ["UAE"]
    seen: set[str] = set()
    result: list[str] = []
    for j in jurisdictions:
        entry = JURISDICTION_REGISTRY.get(j, {})
        for d in entry.get("company_registries", []):
            if d not in seen:
                seen.add(d)
                result.append(d)
        for d in entry.get("domains", []):
            if d not in seen:
                seen.add(d)
                result.append(d)
    return result or JURISDICTION_REGISTRY["UAE"]["company_registries"]


def get_model(role: str, workflow: str | None = None) -> str:
    """Return the model ID for a given role and optional workflow override."""
    routing = MODEL_ROUTING.get(BUDGET_MODE, MODEL_ROUTING["balanced"])
    model = routing.get(role, SONNET)
    if workflow and workflow in WORKFLOW_MODEL_OVERRIDES:
        model = WORKFLOW_MODEL_OVERRIDES[workflow].get(role, model)
    return model


def reload() -> None:
    """Re-read .env and rebuild API key globals in place.

    Call this after the Streamlit setup page writes a new .env so the rest of
    the process picks up the new keys without requiring an app restart.
    Uses override=True so values already set in the environment are replaced.
    """
    import importlib
    import sys

    load_dotenv(override=True)

    # Re-read keys into module-level names so all callers see the new values
    current_module = sys.modules[__name__]
    current_module.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    current_module.TAVILY_API_KEY    = os.getenv("TAVILY_API_KEY", "")
    current_module.RESEARCH_MODE     = os.getenv(
        "RESEARCH_MODE",
        "live" if os.getenv("TAVILY_API_KEY") else "knowledge_only",
    )


def validate_config() -> list[str]:
    """Return a list of missing required config values."""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    # Tavily is only required when research mode is live
    if RESEARCH_MODE == "live" and not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY (required when RESEARCH_MODE=live)")
    if BUDGET_MODE not in MODEL_ROUTING:
        missing.append(f"BUDGET_MODE='{BUDGET_MODE}' is invalid (use: economy|balanced|premium)")
    return missing

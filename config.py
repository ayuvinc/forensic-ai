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

# ── Jurisdiction registry ─────────────────────────────────────────────────────
JURISDICTION_REGISTRY: dict[str, dict] = {
    "UAE": {
        "regulators": ["CBUAE", "DFSA", "ADGM", "SCA"],
        "domains": ["cb.gov.ae", "dfsa.ae", "adgm.com", "sca.gov.ae", "fsra.ae"],
        "company_registries": ["dc.gov.ae", "added.gov.ae", "mohre.gov.ae"],
    },
    "Saudi Arabia": {
        "regulators": ["SAMA", "CMA"],
        "domains": ["sama.gov.sa", "cma.org.sa"],
        "company_registries": ["mc.gov.sa", "mci.gov.sa"],
    },
    "India": {
        "regulators": ["RBI", "SEBI", "MCA"],
        "domains": ["rbi.org.in", "sebi.gov.in", "mca.gov.in"],
        "company_registries": ["mca.gov.in"],
    },
}


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


def validate_config() -> list[str]:
    """Return a list of missing required config values."""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    if BUDGET_MODE not in MODEL_ROUTING:
        missing.append(f"BUDGET_MODE='{BUDGET_MODE}' is invalid (use: economy|balanced|premium)")
    return missing

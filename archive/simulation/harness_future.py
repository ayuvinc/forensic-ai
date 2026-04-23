"""
Future-direction Monte Carlo harness.

Models planned/unbuilt workflows from Sprint-IA-01/02, product-packaging.md,
ba-logic.md, and docs/hld.md. Extends the existing harness with:
  - New workflow types: aup_investigation, custom_investigation, expert_witness_report,
    evidence_chat_session, workpaper_promotion, knowledge_harvester,
    multi_tenant_workstream, co_work_session
  - New failure modes specific to future-direction risks
  - FUTURE_UNCERTAINTY_DELTA (+0.05) on all base probabilities — unbuilt code has
    no empirical baseline; honest uncertainty modelling requires this bump.

The 15 concrete risks identified from design docs are each mapped to a failure mode
with a probability estimate derived from the design's stated constraints and known
analogous patterns in the existing codebase.
"""
from __future__ import annotations

import random
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from simulation.harness import (
    FailureMode, WorkflowType, SimRun, SimReport,
    BASE_P_KNOWLEDGE, LIVE_MODE_DELTA, MODE_B_P_OVERRIDES,
    _sample_field, _percentile,
)


# ---------------------------------------------------------------------------
# Extended failure modes for future-direction features
# ---------------------------------------------------------------------------

class FutureFailureMode(str, Enum):
    # Navigation / bootstrap
    BOOTSTRAP_REDIRECT_LOOP        = "BOOTSTRAP_REDIRECT_LOOP"
    NAVIGATION_PATH_NOT_FOUND      = "NAVIGATION_PATH_NOT_FOUND"

    # Intake
    HYBRID_INTAKE_MISSED_CLUE      = "HYBRID_INTAKE_MISSED_CLUE"   # remarks <10 chars / whitespace

    # Evidence chat (CEM)
    CONTEXT_WINDOW_EXHAUSTED       = "CONTEXT_WINDOW_EXHAUSTED"
    EMBEDDING_FALLBACK_SILENT      = "EMBEDDING_FALLBACK_SILENT"

    # Template / artifact generation
    TEMPLATE_MISSING_STYLES        = "TEMPLATE_MISSING_STYLES"     # .docx named styles absent

    # Workpaper / audit chain
    AUDIT_CHAIN_BROKEN             = "AUDIT_CHAIN_BROKEN"          # audit_log.jsonl missing
    WORKPAPER_PII_LEAKED           = "WORKPAPER_PII_LEAKED"        # PII in promoted workpaper

    # Knowledge harvester
    HARVESTER_PII_NOT_STRIPPED     = "HARVESTER_PII_NOT_STRIPPED"  # client name/case ID leaked

    # Multi-tenant / Co-Work
    SLUG_COLLISION                 = "SLUG_COLLISION"              # two workflows → same filename
    MULTI_TENANT_STATE_BLEED       = "MULTI_TENANT_STATE_BLEED"    # tenant A reads tenant B state
    CO_WORK_LOCK_CONTENTION        = "CO_WORK_LOCK_CONTENTION"     # concurrent file write deadlock

    # FRM Guided Exercise
    FRM_ZERO_INPUT_BASELINE        = "FRM_ZERO_INPUT_BASELINE"     # no client docs → auto-fill fired

    # Service routing
    SERVICE_TYPE_UNRECOGNISED      = "SERVICE_TYPE_UNRECOGNISED"   # no workflow panel, no error


# ---------------------------------------------------------------------------
# Future-direction uncertainty delta applied on top of BASE_P_KNOWLEDGE
# ---------------------------------------------------------------------------

FUTURE_UNCERTAINTY_DELTA = 0.05  # unbuilt features have no empirical baseline


# ---------------------------------------------------------------------------
# Future workflow probability matrices
# (each key mirrors BASE_P_KNOWLEDGE; extra keys are FutureFailureMode values)
# ---------------------------------------------------------------------------

FUTURE_P_MATRICES: dict[str, dict[str, float]] = {

    # ------------------------------------------------------------------
    # Type 8: AUP Investigation (pipeline — hybrid intake + full review)
    # ------------------------------------------------------------------
    "aup_investigation": {
        **{k: min(1.0, v + FUTURE_UNCERTAINTY_DELTA) for k, v in BASE_P_KNOWLEDGE.items()},
        "post_hook_evidence_chain":           0.12,  # AUP has strong evidence requirements
        # Hybrid intake: remarks field present but ≤10 chars or whitespace → no clarifying question
        FutureFailureMode.HYBRID_INTAKE_MISSED_CLUE.value: 0.10,
        FutureFailureMode.TEMPLATE_MISSING_STYLES.value:   0.08,
    },

    # ------------------------------------------------------------------
    # Type 9: Custom Investigation (pipeline — user-defined template)
    # ------------------------------------------------------------------
    "custom_investigation": {
        **{k: min(1.0, v + FUTURE_UNCERTAINTY_DELTA) for k, v in BASE_P_KNOWLEDGE.items()},
        "post_hook_evidence_chain":           0.12,
        FutureFailureMode.TEMPLATE_MISSING_STYLES.value:   0.15,  # user-supplied template risk
        FutureFailureMode.AUDIT_CHAIN_BROKEN.value:        0.06,
        FutureFailureMode.SLUG_COLLISION.value:            0.04,
    },

    # ------------------------------------------------------------------
    # Expert Witness Report (pipeline — highest evidence standard)
    # ------------------------------------------------------------------
    "expert_witness_report": {
        **{k: min(1.0, v + FUTURE_UNCERTAINTY_DELTA) for k, v in BASE_P_KNOWLEDGE.items()},
        "pm_revision_requested":              0.48,  # legal standard → PM very likely to revise
        "partner_revision_req":              0.14,  # Partner also strict
        "post_hook_evidence_chain":           0.15,  # strictest evidence chain
        FutureFailureMode.TEMPLATE_MISSING_STYLES.value:   0.10,
        FutureFailureMode.AUDIT_CHAIN_BROKEN.value:        0.05,
    },

    # ------------------------------------------------------------------
    # Evidence Chat Session / CEM (mode_b-style — conversational)
    # ------------------------------------------------------------------
    "evidence_chat_session": {
        **MODE_B_P_OVERRIDES,
        "pre_hook_veto":                      0.04 + FUTURE_UNCERTAINTY_DELTA,
        "junior_api_error":                   0.05 + FUTURE_UNCERTAINTY_DELTA,
        "post_hook_schema":                   0.04 + FUTURE_UNCERTAINTY_DELTA,
        # CEM_CONTEXT_CHARS=16,000; >50 turns exceeds this — common in adversarial interviews
        FutureFailureMode.CONTEXT_WINDOW_EXHAUSTED.value:  0.14,
        # sentence-transformers optional; if not installed, embedding silently returns zeroes
        FutureFailureMode.EMBEDDING_FALLBACK_SILENT.value: 0.09,
    },

    # ------------------------------------------------------------------
    # Workpaper Promotion (utility — scoping-like)
    # ------------------------------------------------------------------
    "workpaper_promotion": {
        **MODE_B_P_OVERRIDES,
        "pre_hook_veto":                      0.03 + FUTURE_UNCERTAINTY_DELTA,
        "junior_api_error":                   0.02 + FUTURE_UNCERTAINTY_DELTA,
        "post_hook_schema":                   0.03 + FUTURE_UNCERTAINTY_DELTA,
        FutureFailureMode.AUDIT_CHAIN_BROKEN.value:        0.09,  # audit_log.jsonl missing → block
        FutureFailureMode.WORKPAPER_PII_LEAKED.value:      0.06,  # PII not stripped from workpaper
        FutureFailureMode.SLUG_COLLISION.value:            0.05,  # multi-workflow slug clash
    },

    # ------------------------------------------------------------------
    # Knowledge Harvester (utility — no pipeline)
    # ------------------------------------------------------------------
    "knowledge_harvester": {
        **MODE_B_P_OVERRIDES,
        "pre_hook_veto":                      0.03 + FUTURE_UNCERTAINTY_DELTA,
        "junior_api_error":                   0.03 + FUTURE_UNCERTAINTY_DELTA,
        "post_hook_schema":                   0.02 + FUTURE_UNCERTAINTY_DELTA,
        FutureFailureMode.HARVESTER_PII_NOT_STRIPPED.value: 0.13,  # no PII filter confirmed in design
        FutureFailureMode.EMBEDDING_FALLBACK_SILENT.value:  0.08,
    },

    # ------------------------------------------------------------------
    # Multi-Tenant Workstream (future — SaaS / White-Label shipping models)
    # ------------------------------------------------------------------
    "multi_tenant_workstream": {
        **{k: min(1.0, v + FUTURE_UNCERTAINTY_DELTA * 2) for k, v in BASE_P_KNOWLEDGE.items()},
        # +2× uncertainty — tenant isolation not yet designed
        FutureFailureMode.MULTI_TENANT_STATE_BLEED.value:  0.12,  # session state not namespaced
        FutureFailureMode.SLUG_COLLISION.value:            0.08,  # cross-tenant slug
        FutureFailureMode.AUDIT_CHAIN_BROKEN.value:        0.07,
    },

    # ------------------------------------------------------------------
    # Co-Work Session (future — two consultants editing same case)
    # ------------------------------------------------------------------
    "co_work_session": {
        **MODE_B_P_OVERRIDES,
        "pre_hook_veto":                      0.04 + FUTURE_UNCERTAINTY_DELTA,
        "junior_api_error":                   0.03 + FUTURE_UNCERTAINTY_DELTA,
        "post_hook_schema":                   0.04 + FUTURE_UNCERTAINTY_DELTA,
        FutureFailureMode.CO_WORK_LOCK_CONTENTION.value:   0.15,  # no locking on state.json
        FutureFailureMode.SLUG_COLLISION.value:            0.07,
        FutureFailureMode.AUDIT_CHAIN_BROKEN.value:        0.06,
    },

    # ------------------------------------------------------------------
    # FRM Guided Exercise (redesigned — auto-baseline when no docs provided)
    # ------------------------------------------------------------------
    "frm_guided_exercise": {
        **{k: min(1.0, v + FUTURE_UNCERTAINTY_DELTA) for k, v in BASE_P_KNOWLEDGE.items()},
        "pm_revision_requested":              0.42,  # redesigned FRM inherits frm_risk_register rate
        "pm_revision_limit":                  0.11,
        FutureFailureMode.FRM_ZERO_INPUT_BASELINE.value:   0.11,  # 0-doc intake → auto-fill fires
        FutureFailureMode.TEMPLATE_MISSING_STYLES.value:   0.06,
    },

    # ------------------------------------------------------------------
    # App Bootstrap / st.navigation() restructure (infrastructure risk)
    # Not a workflow per se — models the probability that a session startup fails
    # ------------------------------------------------------------------
    "app_bootstrap": {
        **MODE_B_P_OVERRIDES,
        "pre_hook_veto":                      0.02,
        "junior_api_error":                   0.01,
        "post_hook_schema":                   0.01,
        FutureFailureMode.BOOTSTRAP_REDIRECT_LOOP.value:   0.14,  # 00_Setup.py infinite redirect
        FutureFailureMode.NAVIGATION_PATH_NOT_FOUND.value: 0.11,  # st.navigation() path resolution
        FutureFailureMode.SERVICE_TYPE_UNRECOGNISED.value: 0.08,  # unknown service_type → blank panel
    },
}

# Workflow type registry for future workflows
FUTURE_WORKFLOW_REGISTRY: dict[str, WorkflowType] = {
    "aup_investigation":       WorkflowType.PIPELINE,
    "custom_investigation":    WorkflowType.PIPELINE,
    "expert_witness_report":   WorkflowType.PIPELINE,
    "evidence_chat_session":   WorkflowType.MODE_B,
    "workpaper_promotion":     WorkflowType.UTILITY,
    "knowledge_harvester":     WorkflowType.UTILITY,
    "multi_tenant_workstream": WorkflowType.PIPELINE,
    "co_work_session":         WorkflowType.MODE_B,
    "frm_guided_exercise":     WorkflowType.PIPELINE,
    "app_bootstrap":           WorkflowType.MODE_B,
}

# Input distributions for future workflows
FUTURE_INPUT_DISTRIBUTIONS: dict[str, dict] = {
    "aup_investigation": {
        "investigation_type": ["asset_misappropriation", "financial_statement_fraud",
                                "corruption_bribery", "cyber_fraud", "aml_cft"],
        "audience":           ["management", "board", "legal_proceedings", "regulatory_submission"],
        "doc_count":          ("poisson", 3),
        "remarks_length":     ("lognormal", 3.2, 1.0),  # short remarks common (trigger boundary)
        "has_engagement_letter": ("bernoulli", 0.65),
        "research_mode":      ("bernoulli_live", 0.3),
    },
    "custom_investigation": {
        "investigation_type": ["custom"],
        "has_template":       ("bernoulli", 0.7),  # may not have a template file
        "doc_count":          ("poisson", 2),
        "has_engagement_letter": ("bernoulli", 0.6),
        "research_mode":      ("bernoulli_live", 0.25),
    },
    "expert_witness_report": {
        "proceeding_type":    ["civil", "criminal", "regulatory", "arbitration"],
        "jurisdiction":       ["UAE_DIFC", "UAE_ADGM", "UAE_mainland", "international"],
        "doc_count":          ("poisson", 4),
        "has_counsel_instructions": ("bernoulli", 0.55),
        "research_mode":      ("bernoulli_live", 0.4),
    },
    "evidence_chat_session": {
        "turn_count":         ("lognormal", 3.0, 0.9),  # ~20 turns median; >50 = context risk
        "doc_count":          ("poisson", 2),
        "embedding_available": ("bernoulli", 0.75),  # sentence-transformers installed
        "research_mode":      ("bernoulli_live", 0.1),
    },
    "workpaper_promotion": {
        "workpaper_count":    ("range", 1, 8),
        "has_pii_content":    ("bernoulli", 0.35),
        "audit_log_exists":   ("bernoulli", 0.85),
        "research_mode":      ("bernoulli_live", 0.05),
    },
    "knowledge_harvester": {
        "source_type":        ["investigation_report", "frm_risk_register", "workpaper"],
        "has_client_names":   ("bernoulli", 0.60),  # risk of PII in source
        "embedding_available": ("bernoulli", 0.75),
        "research_mode":      ("bernoulli_live", 0.05),
    },
    "multi_tenant_workstream": {
        "tenant_count":       ("range", 2, 10),
        "concurrent_sessions": ("bernoulli", 0.45),
        "doc_count":          ("poisson", 2),
        "research_mode":      ("bernoulli_live", 0.2),
    },
    "co_work_session": {
        "concurrent_writers": ("bernoulli", 0.5),
        "doc_count":          ("poisson", 2),
        "research_mode":      ("bernoulli_live", 0.1),
    },
    "frm_guided_exercise": {
        "module_count":       ("range", 1, 8),
        "doc_count":          ("poisson", 1),  # low — guided exercise for sparse inputs
        "has_engagement_letter": ("bernoulli", 0.6),
        "research_mode":      ("bernoulli_live", 0.25),
    },
    "app_bootstrap": {
        "first_run":          ("bernoulli", 0.2),  # 20% of sessions are first-run
        "has_firm_profile":   ("bernoulli", 0.8),
        "service_type_valid": ("bernoulli", 0.88),
        "research_mode":      ("bernoulli_live", 0.0),
    },
}


# ---------------------------------------------------------------------------
# Future-direction single-run simulator
# ---------------------------------------------------------------------------

def _simulate_future_run(workflow: str, wf_type: WorkflowType,
                          inputs: dict) -> SimRun:
    """
    Simulate one run of a future-direction workflow.
    Uses the workflow's probability matrix from FUTURE_P_MATRICES.
    Future-specific failure modes are checked after the standard pipeline checks.
    """
    research_mode = inputs.get("research_mode", "knowledge_only")
    p = dict(FUTURE_P_MATRICES.get(workflow, {k: min(1.0, v + FUTURE_UNCERTAINTY_DELTA)
                                               for k, v in BASE_P_KNOWLEDGE.items()}))

    junior_rounds = 0
    pm_rounds = 0
    ticks = 0

    # ── APP BOOTSTRAP: check first before any workflow starts ────────────
    if workflow == "app_bootstrap" or wf_type in (WorkflowType.MODE_B, WorkflowType.UTILITY):
        ticks += 1
        if random.random() < p.get(FutureFailureMode.BOOTSTRAP_REDIRECT_LOOP.value, 0):
            return SimRun(workflow, inputs, "BOOTSTRAP_FAILED",
                          FailureMode.PIPELINE_ERROR, "bootstrap",
                          0, 0, research_mode, ticks)
        if random.random() < p.get(FutureFailureMode.NAVIGATION_PATH_NOT_FOUND.value, 0):
            return SimRun(workflow, inputs, "NAVIGATION_ERROR",
                          FailureMode.PIPELINE_ERROR, "navigation",
                          0, 0, research_mode, ticks)
        if random.random() < p.get(FutureFailureMode.SERVICE_TYPE_UNRECOGNISED.value, 0):
            return SimRun(workflow, inputs, "SERVICE_UNRECOGNISED",
                          FailureMode.PIPELINE_ERROR, "service_routing",
                          0, 0, research_mode, ticks)

    # ── PRE-HOOK ────────────────────────────────────────────────────────
    ticks += 1
    if random.random() < p.get("pre_hook_veto", 0.04):
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.HOOK_VETO_PRE,
                      "pre_hook", 0, 0, research_mode, ticks)

    # ── HYBRID INTAKE CLARIFICATION (aup_investigation only) ────────────
    if workflow == "aup_investigation":
        remarks_len = inputs.get("remarks_length", 50)
        # Short/whitespace-only remarks miss the clarification trigger
        if isinstance(remarks_len, (int, float)) and remarks_len < 10:
            if random.random() < p.get(FutureFailureMode.HYBRID_INTAKE_MISSED_CLUE.value, 0.10):
                return SimRun(workflow, inputs, "INTAKE_AMBIGUOUS",
                              FailureMode.PIPELINE_ERROR, "hybrid_intake",
                              0, 0, research_mode, ticks)

    # ── MODE_B / UTILITY ────────────────────────────────────────────────
    if wf_type in (WorkflowType.MODE_B, WorkflowType.UTILITY):
        ticks += 3

        # Context window for CEM
        if random.random() < p.get(FutureFailureMode.CONTEXT_WINDOW_EXHAUSTED.value, 0):
            return SimRun(workflow, inputs, "CONTEXT_EXHAUSTED",
                          FailureMode.PIPELINE_ERROR, "evidence_chat",
                          0, 0, research_mode, ticks)

        # Embedding fallback (silent — no user-facing error)
        if random.random() < p.get(FutureFailureMode.EMBEDDING_FALLBACK_SILENT.value, 0):
            return SimRun(workflow, inputs, "EMBEDDING_DEGRADED",
                          FailureMode.PIPELINE_ERROR, "embedding",
                          0, 0, research_mode, ticks)

        # Audit chain check (workpaper_promotion, knowledge_harvester)
        if random.random() < p.get(FutureFailureMode.AUDIT_CHAIN_BROKEN.value, 0):
            return SimRun(workflow, inputs, "AUDIT_CHAIN_BROKEN",
                          FailureMode.PIPELINE_ERROR, "audit_hook",
                          0, 0, research_mode, ticks)

        # PII leak in utility workflows
        if random.random() < p.get(FutureFailureMode.WORKPAPER_PII_LEAKED.value, 0):
            return SimRun(workflow, inputs, "PII_LEAKED",
                          FailureMode.HOOK_VETO_POST, "pii_check",
                          0, 0, research_mode, ticks)
        if random.random() < p.get(FutureFailureMode.HARVESTER_PII_NOT_STRIPPED.value, 0):
            return SimRun(workflow, inputs, "HARVESTER_PII_LEAK",
                          FailureMode.HOOK_VETO_POST, "pii_check",
                          0, 0, research_mode, ticks)

        # Co-Work lock contention
        if random.random() < p.get(FutureFailureMode.CO_WORK_LOCK_CONTENTION.value, 0):
            return SimRun(workflow, inputs, "LOCK_CONTENTION",
                          FailureMode.PIPELINE_ERROR, "file_lock",
                          0, 0, research_mode, ticks)

        # API error
        if random.random() < p.get("junior_api_error", 0.03):
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.API_ERROR,
                          "agent", 0, 0, research_mode, ticks)

        # Schema
        if random.random() < p.get("post_hook_schema", 0.06):
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.SCHEMA_VALIDATION,
                          "post_hook", 0, 0, research_mode, ticks)

        # Slug collision
        if random.random() < p.get(FutureFailureMode.SLUG_COLLISION.value, 0):
            return SimRun(workflow, inputs, "SLUG_COLLISION",
                          FailureMode.PIPELINE_ERROR, "artifact_write",
                          0, 0, research_mode, ticks)

        return SimRun(workflow, inputs, "DELIVERABLE_WRITTEN", FailureMode.SUCCESS,
                      "none", 0, 0, research_mode, ticks)

    # ── PIPELINE ────────────────────────────────────────────────────────
    max_junior = 3
    max_pm = 2
    junior_ok = False

    for j_round in range(max_junior + 1):
        ticks += 5
        junior_rounds = j_round

        if random.random() < p.get("junior_max_turns", 0.05):
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.MAX_TURNS,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)
        if random.random() < p.get("junior_timeout", 0.03):
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.TIMEOUT,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)
        if random.random() < p.get("junior_no_citations", 0.0):
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.NO_CITATIONS,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)
        if random.random() < p.get("junior_api_error", 0.03):
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.API_ERROR,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)

        # Template validation (pipeline workflows can fail at Junior's artifact generation)
        if random.random() < p.get(FutureFailureMode.TEMPLATE_MISSING_STYLES.value, 0):
            return SimRun(workflow, inputs, "TEMPLATE_FAILED",
                          FailureMode.PIPELINE_ERROR, "template_render",
                          junior_rounds, pm_rounds, research_mode, ticks)

        # FRM zero-input baseline
        if workflow == "frm_guided_exercise":
            doc_count = inputs.get("doc_count", 1)
            if doc_count == 0:
                if random.random() < p.get(FutureFailureMode.FRM_ZERO_INPUT_BASELINE.value, 0):
                    return SimRun(workflow, inputs, "BASELINE_AUTO_FILL",
                                  FailureMode.PIPELINE_ERROR, "frm_intake",
                                  junior_rounds, pm_rounds, research_mode, ticks)

        # PM review
        ticks += 3
        for pm_round in range(max_pm + 1):
            pm_rounds = pm_round
            if random.random() < p.get("pm_revision_requested", 0.35):
                ticks += 2
                if pm_rounds >= max_pm:
                    return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.REVISION_LIMIT,
                                  "pm", junior_rounds, pm_rounds, research_mode, ticks)
                break
            else:
                junior_ok = True
                break

        if junior_ok:
            break

        if j_round >= max_junior:
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.REVISION_LIMIT,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)

    # Partner review
    ticks += 4
    if random.random() < p.get("partner_no_citations", 0.0):
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.NO_CITATIONS,
                      "partner", junior_rounds, pm_rounds, research_mode, ticks)
    if random.random() < p.get("partner_revision_req", 0.07):
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.PIPELINE_ERROR,
                      "partner", junior_rounds, pm_rounds, research_mode, ticks)

    # Post-hooks
    ticks += 2
    if random.random() < p.get("post_hook_schema", 0.06):
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.SCHEMA_VALIDATION,
                      "post_hook", junior_rounds, pm_rounds, research_mode, ticks)
    if random.random() < p.get("post_hook_evidence_chain", 0.08):
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.HOOK_VETO_POST,
                      "post_hook_evidence_chain", junior_rounds, pm_rounds, research_mode, ticks)

    # Multi-tenant state bleed (post-pipeline check)
    if random.random() < p.get(FutureFailureMode.MULTI_TENANT_STATE_BLEED.value, 0):
        return SimRun(workflow, inputs, "TENANT_STATE_BLEED",
                      FailureMode.PIPELINE_ERROR, "tenant_isolation",
                      junior_rounds, pm_rounds, research_mode, ticks)

    # Audit chain / PII post-checks
    if random.random() < p.get(FutureFailureMode.AUDIT_CHAIN_BROKEN.value, 0):
        return SimRun(workflow, inputs, "AUDIT_CHAIN_BROKEN",
                      FailureMode.PIPELINE_ERROR, "audit_hook",
                      junior_rounds, pm_rounds, research_mode, ticks)

    if random.random() < p.get(FutureFailureMode.SLUG_COLLISION.value, 0):
        return SimRun(workflow, inputs, "SLUG_COLLISION",
                      FailureMode.PIPELINE_ERROR, "artifact_write",
                      junior_rounds, pm_rounds, research_mode, ticks)

    return SimRun(workflow, inputs, "OWNER_APPROVED", FailureMode.SUCCESS,
                  "none", junior_rounds, pm_rounds, research_mode, ticks)


# ---------------------------------------------------------------------------
# Future workflow simulation runner
# ---------------------------------------------------------------------------

def _sample_future_inputs(workflow: str) -> dict:
    dist = FUTURE_INPUT_DISTRIBUTIONS.get(workflow, {})
    return {k: _sample_field(v) for k, v in dist.items()}


def run_future_workflow_simulation(workflow: str, n: int = 500,
                                    seed: int | None = None) -> SimReport:
    if seed is not None:
        random.seed(seed)

    wf_type = FUTURE_WORKFLOW_REGISTRY.get(workflow, WorkflowType.MODE_B)
    runs: list[SimRun] = []
    failure_counts: dict[str, int] = {}
    revision_dist: dict[str, int] = {}
    jr_rounds_list: list[float] = []
    pm_rounds_list: list[float] = []

    ko_success = 0; ko_total = 0
    live_success = 0; live_total = 0

    field_fail_counts: dict[str, dict[Any, int]] = {}
    field_total_counts: dict[str, dict[Any, int]] = {}

    for _ in range(n):
        inputs = _sample_future_inputs(workflow)
        run = _simulate_future_run(workflow, wf_type, inputs)
        runs.append(run)

        fm = run.failure_mode.value
        failure_counts[fm] = failure_counts.get(fm, 0) + 1

        key = f"j{run.revision_rounds_junior}_p{run.revision_rounds_pm}"
        revision_dist[key] = revision_dist.get(key, 0) + 1

        jr_rounds_list.append(float(run.revision_rounds_junior))
        pm_rounds_list.append(float(run.revision_rounds_pm))

        if run.research_mode == "knowledge_only":
            ko_total += 1
            if run.failure_mode == FailureMode.SUCCESS:
                ko_success += 1
        else:
            live_total += 1
            if run.failure_mode == FailureMode.SUCCESS:
                live_success += 1

        failed = run.failure_mode != FailureMode.SUCCESS
        for k, v in inputs.items():
            if isinstance(v, (str, bool, int)) and not k.endswith("_mode"):
                if k not in field_fail_counts:
                    field_fail_counts[k] = {}
                    field_total_counts[k] = {}
                sv = str(v)
                field_fail_counts[k][sv] = field_fail_counts[k].get(sv, 0) + (1 if failed else 0)
                field_total_counts[k][sv] = field_total_counts[k].get(sv, 0) + 1

    success_n = failure_counts.get(FailureMode.SUCCESS.value, 0)
    success_rate = success_n / n if n > 0 else 0.0

    input_sensitivity: dict[str, float] = {}
    for k in field_fail_counts:
        rates = []
        for sv, fc in field_fail_counts[k].items():
            tc = field_total_counts[k].get(sv, 1)
            rates.append(fc / tc)
        if rates:
            input_sensitivity[k] = round(max(rates) - min(rates), 4)

    top_failures = sorted(
        [(k, v) for k, v in failure_counts.items() if k != FailureMode.SUCCESS.value],
        key=lambda x: x[1], reverse=True
    )[:5]

    return SimReport(
        workflow=f"[FUTURE] {workflow}",
        workflow_type=wf_type.value,
        n_runs=n,
        success_rate=round(success_rate, 4),
        failure_breakdown=failure_counts,
        revision_distribution=revision_dist,
        p50_junior_rounds=_percentile(jr_rounds_list, 50),
        p95_junior_rounds=_percentile(jr_rounds_list, 95),
        p50_pm_rounds=_percentile(pm_rounds_list, 50),
        p95_pm_rounds=_percentile(pm_rounds_list, 95),
        top_failure_modes=top_failures,
        input_sensitivity=input_sensitivity,
        mode_delta={
            "knowledge_only_success": round(ko_success / ko_total, 4) if ko_total else 0.0,
            "live_success":           round(live_success / live_total, 4) if live_total else 0.0,
        },
        runs=runs,
    )

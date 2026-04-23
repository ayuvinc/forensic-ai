"""
Monte Carlo simulation harness for forensic-ai workflow failure analysis.
No API calls — pure parametric simulation using failure probability matrices.
"""
from __future__ import annotations

import random
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums & data models
# ---------------------------------------------------------------------------

class FailureMode(str, Enum):
    SUCCESS              = "SUCCESS"
    HOOK_VETO_PRE        = "HOOK_VETO_PRE"
    HOOK_VETO_POST       = "HOOK_VETO_POST"
    MAX_TURNS            = "MAX_TURNS"
    TIMEOUT              = "TIMEOUT"
    NO_CITATIONS         = "NO_CITATIONS"
    TOOL_NOT_ALLOWED     = "TOOL_NOT_ALLOWED"
    REVISION_LIMIT       = "REVISION_LIMIT"
    INVALID_TRANSITION   = "INVALID_TRANSITION"
    SCHEMA_VALIDATION    = "SCHEMA_VALIDATION"
    API_ERROR            = "API_ERROR"
    PIPELINE_ERROR       = "PIPELINE_ERROR"
    INPUT_VALIDATION     = "INPUT_VALIDATION"
    HUMAN_CANCEL         = "HUMAN_CANCEL"


class WorkflowType(str, Enum):
    PIPELINE   = "pipeline"    # Junior → PM → Partner
    MODE_B     = "mode_b"      # Single-pass Sonnet
    SCOPING    = "scoping"     # Human confirmation required
    UTILITY    = "utility"     # No simulation


@dataclass
class SimRun:
    workflow: str
    input_params: dict
    terminal_state: str
    failure_mode: FailureMode
    failure_layer: str           # "pre_hook" | "junior" | "pm" | "partner" | "post_hook" | "none"
    revision_rounds_junior: int
    revision_rounds_pm: int
    research_mode: str           # "knowledge_only" | "live"
    elapsed_ticks: int           # abstract time units


@dataclass
class SimReport:
    workflow: str
    workflow_type: str
    n_runs: int
    success_rate: float
    failure_breakdown: dict[str, int]
    revision_distribution: dict[str, int]   # "j{n}_p{m}" → count
    p50_junior_rounds: float
    p95_junior_rounds: float
    p50_pm_rounds: float
    p95_pm_rounds: float
    top_failure_modes: list[tuple[str, int]]
    input_sensitivity: dict[str, float]     # field → failure_correlation
    mode_delta: dict[str, float]            # "knowledge_only_success" | "live_success"
    runs: list[SimRun] = field(default_factory=list, repr=False)


# ---------------------------------------------------------------------------
# Failure probability matrices
# ---------------------------------------------------------------------------

# Base probabilities — knowledge_only mode
BASE_P_KNOWLEDGE = {
    "pre_hook_veto":           0.04,
    "junior_max_turns":        0.05,
    "junior_timeout":          0.03,
    "junior_no_citations":     0.00,   # disabled in knowledge_only
    "junior_tool_not_allowed": 0.02,
    "junior_api_error":        0.03,
    "pm_revision_requested":   0.35,
    "pm_revision_limit":       0.08,
    "partner_revision_req":    0.07,
    "partner_no_citations":    0.00,   # disabled in knowledge_only
    "post_hook_schema":        0.06,
    "post_hook_evidence_chain":0.08,   # investigation/expert_witness only
    "post_hook_persist":       0.02,
    "human_cancel":            0.00,   # set per-workflow
}

# Delta applied on top of BASE_P for live mode
LIVE_MODE_DELTA = {
    "junior_max_turns":        +0.03,
    "junior_timeout":          +0.03,
    "junior_no_citations":     +0.12,
    "pm_revision_limit":       +0.02,
    "partner_no_citations":    +0.18,
}

# Per-workflow overrides (applied after base + live delta)
WORKFLOW_P_OVERRIDES: dict[str, dict[str, float]] = {
    "sanctions_screening": {
        "junior_no_citations":  0.00,   # knowledge_only; live overrides separately
        "partner_no_citations": 0.00,
    },
    "investigation_report": {
        "post_hook_evidence_chain": 0.10,
    },
    "frm_risk_register": {
        "pm_revision_requested": 0.40,  # higher — more complex multi-module output
        "pm_revision_limit":     0.10,
    },
    "engagement_scoping": {
        "human_cancel": 0.15,
    },
    "transaction_testing": {
        "human_cancel": 0.15,
    },
    "persona_review": {
        "post_hook_evidence_chain": 0.00,  # no evidence chain check
        "pm_revision_requested":    0.00,  # no PM loop
        "partner_revision_req":     0.00,  # no partner loop
    },
}

# Mode B workflows use only a subset of failure modes
MODE_B_P_OVERRIDES = {
    "junior_max_turns":        0.00,
    "junior_timeout":          0.00,
    "junior_no_citations":     0.00,
    "junior_tool_not_allowed": 0.00,
    "junior_api_error":        0.03,
    "pm_revision_requested":   0.00,
    "pm_revision_limit":       0.00,
    "partner_revision_req":    0.00,
    "partner_no_citations":    0.00,
    "post_hook_evidence_chain": 0.00,
}


# ---------------------------------------------------------------------------
# Input distributions
# ---------------------------------------------------------------------------

INPUT_DISTRIBUTIONS: dict[str, dict] = {
    "investigation_report": {
        "investigation_type": ["asset_misappropriation", "financial_statement_fraud",
                                "corruption_bribery", "cyber_fraud",
                                "procurement_fraud", "revenue_leakage",
                                "compliance_investigation"],
        "audience":           ["management", "board", "legal_proceedings", "regulatory_submission"],
        "doc_count":          ("poisson", 2),
        "has_engagement_letter": ("bernoulli", 0.6),
        "research_mode":      ("bernoulli_live", 0.3),
    },
    "frm_risk_register": {
        "module_count":       ("range", 1, 8),
        "doc_count":          ("poisson", 3),
        "recommendation_depth": ["structured", "executive", "detailed"],
        "has_engagement_letter": ("bernoulli", 0.7),
        "research_mode":      ("bernoulli_live", 0.3),
    },
    "due_diligence": {
        "subject_type":       ["individual", "entity"],
        "screening_level":    ["standard_phase1", "enhanced_phase2"],
        "screening_lists":    ("multi_choice", ["OFAC","UN","EU","UK_OFSI","UAE_local"], 0.6),
        "purpose":            ["onboarding","investment","partnership","employment","acquisition","other"],
        "doc_count":          ("poisson", 2),
        "research_mode":      ("bernoulli_live", 0.3),
    },
    "sanctions_screening": {
        "subject_type":       ["individual", "entity"],
        "has_aliases":        ("bernoulli", 0.4),
        "has_dob":            ("bernoulli", 0.5),
        "purpose":            ["onboarding","transaction","periodic_review","acquisition","regulatory","other"],
        "output_format":      ["clearance_memo", "full_report"],
        "research_mode":      ("bernoulli_live", 0.3),
    },
    "transaction_testing": {
        "engagement_context": ["fraud_discovery","fraud_quantification","audit_compliance",
                                "due_diligence","regulatory"],
        "fraud_typology":     ["procurement","payroll","expense","cash","financial_stmt","aml"],
        "evidence_standard":  ["internal_review","regulatory_submission","court_ready","board_pack"],
        "sampling":           ["full", "sampling"],
        "doc_count":          ("poisson", 4),
        "research_mode":      ("bernoulli_live", 0.2),
    },
    "policy_sop": {
        "doc_type":           ["policy", "sop"],
        "mode":               ["new", "gap_analysis"],
        "doc_count":          ("poisson", 1),
        "research_mode":      ("bernoulli_live", 0.2),
    },
    "training_material": {
        "topic":              ["AML","fraud","corruption","data_privacy","whistleblowing","KYC","custom"],
        "audience":           ["all_staff","finance","mgmt","board","compliance","front_line"],
        "duration_minutes":   ("range", 15, 480),
        "include_quiz":       ("bernoulli", 0.8),
        "include_case_study": ("bernoulli", 0.7),
        "research_mode":      ("bernoulli_live", 0.1),
    },
    "client_proposal": {
        "firm_profile_complete": ("bernoulli", 0.9),
        "has_fee_notes":         ("bernoulli", 0.4),
        "research_mode":         ("bernoulli_live", 0.1),
    },
    "engagement_scoping": {
        "has_constraints":    ("bernoulli", 0.5),
        "has_red_flags":      ("bernoulli", 0.4),
        "description_length": ("lognormal", 4.5, 0.8),  # ~90 chars median
        "research_mode":      ("bernoulli_live", 0.2),
    },
    "persona_review": {
        "persona_count":      ("range", 1, 4),
        "deliverable_length": ("lognormal", 7.0, 0.5),  # ~1100 chars median
        "research_mode":      ("bernoulli_live", 0.1),
    },
    "workpaper": {
        "doc_count":          ("poisson", 3),
        "has_leads":          ("bernoulli", 0.6),
        "research_mode":      ("bernoulli_live", 0.1),
    },
}


# ---------------------------------------------------------------------------
# Workflow registry
# ---------------------------------------------------------------------------

WORKFLOW_REGISTRY: dict[str, WorkflowType] = {
    "investigation_report":   WorkflowType.PIPELINE,
    "frm_risk_register":      WorkflowType.PIPELINE,
    "persona_review":         WorkflowType.PIPELINE,
    "policy_sop":             WorkflowType.MODE_B,
    "due_diligence":          WorkflowType.MODE_B,
    "sanctions_screening":    WorkflowType.MODE_B,
    "client_proposal":        WorkflowType.MODE_B,
    "training_material":      WorkflowType.MODE_B,
    "workpaper":              WorkflowType.MODE_B,
    "engagement_scoping":     WorkflowType.SCOPING,
    "transaction_testing":    WorkflowType.SCOPING,
}


# ---------------------------------------------------------------------------
# Sampler helpers
# ---------------------------------------------------------------------------

def _sample_field(spec: Any) -> Any:
    """Sample a single field value from its distribution spec."""
    if isinstance(spec, list):
        return random.choice(spec)
    if isinstance(spec, tuple):
        kind = spec[0]
        if kind == "bernoulli":
            return random.random() < spec[1]
        if kind == "bernoulli_live":
            return "live" if random.random() < spec[1] else "knowledge_only"
        if kind == "poisson":
            return max(0, int(random.expovariate(1 / spec[1])))
        if kind == "range":
            return random.randint(spec[1], spec[2])
        if kind == "lognormal":
            return int(math.exp(random.gauss(spec[1], spec[2])))
        if kind == "multi_choice":
            items, p_each = spec[1], spec[2]
            return [x for x in items if random.random() < p_each]
    return spec


def _sample_inputs(workflow: str) -> dict:
    dist = INPUT_DISTRIBUTIONS.get(workflow, {})
    return {k: _sample_field(v) for k, v in dist.items()}


# ---------------------------------------------------------------------------
# Probability resolver
# ---------------------------------------------------------------------------

def _resolve_p(base: dict, workflow: str, research_mode: str,
               workflow_type: WorkflowType) -> dict:
    p = dict(base)

    # Apply live-mode delta
    if research_mode == "live":
        for k, delta in LIVE_MODE_DELTA.items():
            if k in p:
                p[k] = max(0.0, min(1.0, p[k] + delta))

    # Mode B: zero out agent-loop probabilities
    if workflow_type == WorkflowType.MODE_B:
        for k, v in MODE_B_P_OVERRIDES.items():
            p[k] = v

    # Scoping: same as Mode B plus human_cancel
    if workflow_type == WorkflowType.SCOPING:
        for k, v in MODE_B_P_OVERRIDES.items():
            p[k] = v
        # human_cancel set per workflow below

    # Workflow-specific overrides
    overrides = WORKFLOW_P_OVERRIDES.get(workflow, {})
    for k, v in overrides.items():
        p[k] = v

    # Sanctions live-mode citation override
    if workflow == "sanctions_screening" and research_mode == "live":
        p["junior_no_citations"]  = 0.25
        p["partner_no_citations"] = 0.25

    return p


# ---------------------------------------------------------------------------
# Single-run simulator
# ---------------------------------------------------------------------------

def _simulate_run(workflow: str, wf_type: WorkflowType, inputs: dict) -> SimRun:
    research_mode = inputs.get("research_mode", "knowledge_only")
    p = _resolve_p(BASE_P_KNOWLEDGE, workflow, research_mode, wf_type)

    junior_rounds = 0
    pm_rounds = 0
    ticks = 0

    # ── PRE-HOOK ──────────────────────────────────────────────────────────
    ticks += 1
    if random.random() < p["pre_hook_veto"]:
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.HOOK_VETO_PRE,
                      "pre_hook", 0, 0, research_mode, ticks)

    # ── HUMAN CANCEL (scoping workflows) ─────────────────────────────────
    if wf_type == WorkflowType.SCOPING:
        ticks += 2
        if random.random() < p.get("human_cancel", 0.0):
            return SimRun(workflow, inputs, "SCOPE_CANCELLED", FailureMode.HUMAN_CANCEL,
                          "human", 0, 0, research_mode, ticks)

    # ── MODE B: single agent pass ─────────────────────────────────────────
    if wf_type in (WorkflowType.MODE_B, WorkflowType.SCOPING):
        ticks += 3
        if random.random() < p["junior_api_error"]:
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.API_ERROR,
                          "sonnet_single_pass", 0, 0, research_mode, ticks)
        if random.random() < p["post_hook_schema"]:
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.SCHEMA_VALIDATION,
                          "post_hook", 0, 0, research_mode, ticks)
        return SimRun(workflow, inputs, "DELIVERABLE_WRITTEN", FailureMode.SUCCESS,
                      "none", 0, 0, research_mode, ticks)

    # ── PIPELINE: Junior → PM → Partner ──────────────────────────────────
    max_junior = 3
    max_pm = 2
    junior_ok = False

    for j_round in range(max_junior + 1):
        ticks += 5
        junior_rounds = j_round

        # Junior agent errors
        if random.random() < p["junior_max_turns"]:
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.MAX_TURNS,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)
        if random.random() < p["junior_timeout"]:
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.TIMEOUT,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)
        if random.random() < p["junior_no_citations"]:
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.NO_CITATIONS,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)
        if random.random() < p["junior_tool_not_allowed"]:
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.TOOL_NOT_ALLOWED,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)
        if random.random() < p["junior_api_error"]:
            return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.API_ERROR,
                          "junior", junior_rounds, pm_rounds, research_mode, ticks)

        # PM review
        ticks += 3
        for pm_round in range(max_pm + 1):
            pm_rounds = pm_round
            if random.random() < p["pm_revision_requested"]:
                ticks += 2
                if pm_rounds >= max_pm:
                    # PM exhausted — falls back to junior limit
                    return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.REVISION_LIMIT,
                                  "pm", junior_rounds, pm_rounds, research_mode, ticks)
                # revision: re-run junior next outer iteration
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
    if random.random() < p["partner_no_citations"]:
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.NO_CITATIONS,
                      "partner", junior_rounds, pm_rounds, research_mode, ticks)
    if random.random() < p["partner_revision_req"]:
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.PIPELINE_ERROR,
                      "partner", junior_rounds, pm_rounds, research_mode, ticks)

    # Post-hook
    ticks += 2
    if random.random() < p["post_hook_schema"]:
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.SCHEMA_VALIDATION,
                      "post_hook", junior_rounds, pm_rounds, research_mode, ticks)
    if random.random() < p["post_hook_evidence_chain"]:
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.HOOK_VETO_POST,
                      "post_hook_evidence_chain", junior_rounds, pm_rounds, research_mode, ticks)
    if random.random() < p["post_hook_persist"]:
        return SimRun(workflow, inputs, "PIPELINE_ERROR", FailureMode.HOOK_VETO_POST,
                      "post_hook_persist", junior_rounds, pm_rounds, research_mode, ticks)

    return SimRun(workflow, inputs, "OWNER_APPROVED", FailureMode.SUCCESS,
                  "none", junior_rounds, pm_rounds, research_mode, ticks)


# ---------------------------------------------------------------------------
# Per-workflow report builder
# ---------------------------------------------------------------------------

def _percentile(data: list[float], pct: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    idx = max(0, int(len(s) * pct / 100) - 1)
    return float(s[idx])


def run_workflow_simulation(workflow: str, n: int = 500,
                            seed: int | None = None) -> SimReport:
    if seed is not None:
        random.seed(seed)

    wf_type = WORKFLOW_REGISTRY.get(workflow, WorkflowType.MODE_B)
    runs: list[SimRun] = []
    failure_counts: dict[str, int] = {}
    revision_dist: dict[str, int] = {}
    jr_rounds_list: list[float] = []
    pm_rounds_list: list[float] = []

    ko_success = 0; ko_total = 0
    live_success = 0; live_total = 0

    # Input sensitivity: track per-field failure counts
    field_fail_counts: dict[str, dict[Any, int]] = {}
    field_total_counts: dict[str, dict[Any, int]] = {}

    for _ in range(n):
        inputs = _sample_inputs(workflow)
        run = _simulate_run(workflow, wf_type, inputs)
        runs.append(run)

        # Failure counts
        fm = run.failure_mode.value
        failure_counts[fm] = failure_counts.get(fm, 0) + 1

        # Revision distribution
        key = f"j{run.revision_rounds_junior}_p{run.revision_rounds_pm}"
        revision_dist[key] = revision_dist.get(key, 0) + 1

        # Rounds lists
        jr_rounds_list.append(float(run.revision_rounds_junior))
        pm_rounds_list.append(float(run.revision_rounds_pm))

        # Mode delta
        if run.research_mode == "knowledge_only":
            ko_total += 1
            if run.failure_mode == FailureMode.SUCCESS:
                ko_success += 1
        else:
            live_total += 1
            if run.failure_mode == FailureMode.SUCCESS:
                live_success += 1

        # Input sensitivity: track discrete fields
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

    # Input sensitivity: compute max failure-rate delta per field
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
        workflow=workflow,
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

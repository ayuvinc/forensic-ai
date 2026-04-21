"""
Game-theory simulation for the Junior → PM → Partner review pipeline.

Models the three agents as strategic players and analyses:
  A. PM/Partner threshold calibration — what thresholds minimise failure?
  B. Information asymmetry — how often does PM over-approve, causing Partner kick-back?
  C. FRM module-count sensitivity — how does pipeline failure scale with modules?
  D. Revision-limit optimality — are MAX_REVISION_ROUNDS={"junior":3,"pm":2} well-calibrated?
"""
from __future__ import annotations

import random
import math
from dataclasses import dataclass
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Payoff constants (unitless utility scores)
# ---------------------------------------------------------------------------

PAYOFF = {
    "junior_accept":           +1.0,
    "junior_revision_cost":    -0.3,   # per round
    "junior_limit_error":      -1.0,
    "pm_clean_approval":       +1.0,
    "pm_revision_cost":        -0.5,   # per round
    "pm_partner_rejection":    -1.0,
    "partner_clean_approval":  +1.0,
    "partner_disclaimer_cost": -0.2,   # accepts with disclaimer
    "partner_revision_req":    -1.0,   # blocks delivery
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class GameResult:
    terminal: str        # "APPROVED" | "APPROVED_WITH_DISCLAIMER" | "REVISION_LIMIT" | "PARTNER_REJECTED"
    junior_rounds: int
    pm_rounds: int
    final_quality: float
    junior_payoff: float
    pm_payoff: float
    partner_payoff: float
    total_ticks: int


@dataclass
class ScenarioResult:
    scenario: str
    n_runs: int
    terminal_distribution: dict[str, int]
    avg_junior_rounds: float
    avg_pm_rounds: float
    p95_junior_rounds: float
    avg_total_payoff: float
    nash_pm_threshold: float | None
    nash_partner_threshold: float | None
    notes: list[str]


# ---------------------------------------------------------------------------
# Core game engine
# ---------------------------------------------------------------------------

class AgentGame:
    """
    Simulate one pipeline run as a repeated game.

    quality_mean: expected first-draft quality (0–1)
    quality_std:  noise around that expectation
    improvement_per_revision: expected quality gain per revision round
    improvement_noise: std of the gain
    pm_threshold: PM accepts if Q >= this
    partner_threshold: Partner accepts if Q >= this
    disclaimer_threshold: Partner adds disclaimer if Q in [disclaimer_threshold, partner_threshold)
    max_junior, max_pm: revision round limits
    """

    def __init__(
        self,
        quality_mean: float = 0.65,
        quality_std: float = 0.18,
        improvement_per_revision: float = 0.12,
        improvement_noise: float = 0.05,
        pm_threshold: float = 0.70,
        partner_threshold: float = 0.75,
        disclaimer_threshold: float = 0.65,
        max_junior: int = 3,
        max_pm: int = 2,
    ):
        self.quality_mean = quality_mean
        self.quality_std = quality_std
        self.improvement = improvement_per_revision
        self.improvement_noise = improvement_noise
        self.pm_threshold = pm_threshold
        self.partner_threshold = partner_threshold
        self.disclaimer_threshold = disclaimer_threshold
        self.max_junior = max_junior
        self.max_pm = max_pm

    def _draw_quality(self, base: float) -> float:
        return max(0.0, min(1.0, random.gauss(base, self.quality_std)))

    def simulate_run(self) -> GameResult:
        q = self._draw_quality(self.quality_mean)
        jr = 0
        pm = 0
        ticks = 0
        j_payoff = 0.0
        m_payoff = 0.0

        while True:
            ticks += 5
            # PM evaluation
            pm_accept = q >= self.pm_threshold

            if not pm_accept:
                pm += 1
                m_payoff += PAYOFF["pm_revision_cost"]
                if pm > self.max_pm or jr >= self.max_junior:
                    j_payoff += PAYOFF["junior_limit_error"]
                    return GameResult(
                        terminal="REVISION_LIMIT",
                        junior_rounds=jr, pm_rounds=pm,
                        final_quality=q,
                        junior_payoff=j_payoff + PAYOFF["junior_limit_error"],
                        pm_payoff=m_payoff,
                        partner_payoff=0.0,
                        total_ticks=ticks,
                    )
                # Junior revises
                jr += 1
                j_payoff += PAYOFF["junior_revision_cost"]
                q = min(1.0, q + max(0.0, random.gauss(self.improvement, self.improvement_noise)))
                ticks += 3
                continue

            # PM accepted — pass to Partner
            ticks += 4
            m_payoff += PAYOFF["pm_clean_approval"]

            if q >= self.partner_threshold:
                # Clean approval
                j_payoff += PAYOFF["junior_accept"]
                p_payoff = PAYOFF["partner_clean_approval"]
                return GameResult(
                    terminal="APPROVED",
                    junior_rounds=jr, pm_rounds=pm,
                    final_quality=q,
                    junior_payoff=j_payoff,
                    pm_payoff=m_payoff,
                    partner_payoff=p_payoff,
                    total_ticks=ticks,
                )
            elif q >= self.disclaimer_threshold:
                # Approve with disclaimer
                j_payoff += PAYOFF["junior_accept"]
                p_payoff = PAYOFF["partner_clean_approval"] + PAYOFF["partner_disclaimer_cost"]
                return GameResult(
                    terminal="APPROVED_WITH_DISCLAIMER",
                    junior_rounds=jr, pm_rounds=pm,
                    final_quality=q,
                    junior_payoff=j_payoff,
                    pm_payoff=m_payoff,
                    partner_payoff=p_payoff,
                    total_ticks=ticks,
                )
            else:
                # Partner requests revision → PipelineError (Partner never re-runs in current design)
                j_payoff += PAYOFF["junior_revision_cost"]
                m_payoff += PAYOFF["pm_partner_rejection"]
                p_payoff = PAYOFF["partner_revision_req"]
                return GameResult(
                    terminal="PARTNER_REJECTED",
                    junior_rounds=jr, pm_rounds=pm,
                    final_quality=q,
                    junior_payoff=j_payoff,
                    pm_payoff=m_payoff,
                    partner_payoff=p_payoff,
                    total_ticks=ticks,
                )

    def run_n(self, n: int = 1000) -> list[GameResult]:
        return [self.simulate_run() for _ in range(n)]


# ---------------------------------------------------------------------------
# Scenario A — PM/Partner threshold calibration
# ---------------------------------------------------------------------------

def scenario_a_threshold_calibration(n: int = 1000, seed: int = 42) -> ScenarioResult:
    """Sweep PM × Partner threshold grid; find the combo with highest total payoff."""
    random.seed(seed)
    best_payoff = -math.inf
    best_pm_t = 0.0
    best_pt_t = 0.0

    thresholds = [round(x * 0.05, 2) for x in range(10, 20)]  # 0.50 … 0.95

    for pm_t in thresholds:
        for pt_t in thresholds:
            if pt_t < pm_t:
                continue   # Partner must be >= PM threshold (or same)
            game = AgentGame(pm_threshold=pm_t, partner_threshold=pt_t)
            results = game.run_n(n)
            avg = sum(r.junior_payoff + r.pm_payoff + r.partner_payoff for r in results) / n
            if avg > best_payoff:
                best_payoff = avg
                best_pm_t = pm_t
                best_pt_t = pt_t

    # Run at best thresholds for distribution
    random.seed(seed)
    game = AgentGame(pm_threshold=best_pm_t, partner_threshold=best_pt_t)
    results = game.run_n(n)

    terminals = {}
    total_j = total_m = total_p = 0.0
    jr_list = []
    for r in results:
        terminals[r.terminal] = terminals.get(r.terminal, 0) + 1
        total_j += r.junior_payoff
        total_m += r.pm_payoff
        total_p += r.partner_payoff
        jr_list.append(float(r.junior_rounds))

    jr_p95 = sorted(jr_list)[int(0.95 * len(jr_list))]

    return ScenarioResult(
        scenario="A: Threshold Calibration",
        n_runs=n,
        terminal_distribution=terminals,
        avg_junior_rounds=sum(jr_list) / n,
        avg_pm_rounds=sum(r.pm_rounds for r in results) / n,
        p95_junior_rounds=jr_p95,
        avg_total_payoff=(total_j + total_m + total_p) / n,
        nash_pm_threshold=best_pm_t,
        nash_partner_threshold=best_pt_t,
        notes=[
            f"Optimal PM threshold: {best_pm_t}, Partner threshold: {best_pt_t}",
            f"Current config uses implicit thresholds driven by model output quality, not explicit values.",
            f"Recommendation: if avg quality < {best_pm_t:.0%}, consider lowering max_turns to force re-drafts.",
        ],
    )


# ---------------------------------------------------------------------------
# Scenario B — Information asymmetry (PM over-approves)
# ---------------------------------------------------------------------------

def scenario_b_information_asymmetry(n: int = 1000, seed: int = 42) -> ScenarioResult:
    """
    PM threshold lower than Partner's — simulates PM over-approving,
    Partner then rejects (PARTNER_REJECTED).
    """
    random.seed(seed)
    # PM lenient (0.60), Partner strict (0.80) — realistic asymmetry
    game = AgentGame(pm_threshold=0.60, partner_threshold=0.80, disclaimer_threshold=0.70)
    results = game.run_n(n)

    terminals = {}
    jr_list = []
    for r in results:
        terminals[r.terminal] = terminals.get(r.terminal, 0) + 1
        jr_list.append(float(r.junior_rounds))

    partner_reject_rate = terminals.get("PARTNER_REJECTED", 0) / n
    jr_p95 = sorted(jr_list)[int(0.95 * len(jr_list))]

    notes = [
        f"Partner rejection rate with PM_t=0.60, Partner_t=0.80: {partner_reject_rate:.1%}",
        "FINDING: PM approves drafts that Partner then rejects → PARTNER_REVISION_REQ → PipelineError.",
        "Gap: no feedback loop from Partner back to PM; Partner rejection is terminal in current code.",
        "Mitigation: lower PM threshold OR add Partner→PM feedback loop (currently raises PipelineError).",
    ]
    if partner_reject_rate > 0.05:
        notes.append(
            f"SEVERITY: HIGH — {partner_reject_rate:.1%} of runs reach PipelineError via Partner rejection."
        )

    return ScenarioResult(
        scenario="B: Information Asymmetry (PM over-approves)",
        n_runs=n,
        terminal_distribution=terminals,
        avg_junior_rounds=sum(jr_list) / n,
        avg_pm_rounds=sum(r.pm_rounds for r in results) / n,
        p95_junior_rounds=jr_p95,
        avg_total_payoff=sum(r.junior_payoff + r.pm_payoff + r.partner_payoff for r in results) / n,
        nash_pm_threshold=None,
        nash_partner_threshold=None,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Scenario C — FRM module-count sensitivity
# ---------------------------------------------------------------------------

def scenario_c_frm_module_sensitivity(n: int = 1000, seed: int = 42) -> ScenarioResult:
    """
    FRM runs Junior→PM per module independently. P(at least one module fails) scales with module count.
    Base per-module pipeline success rate derived from Scenario A default game.
    """
    random.seed(seed)
    game = AgentGame()  # default thresholds
    single_run_results = game.run_n(n)
    per_module_success = sum(
        1 for r in single_run_results
        if r.terminal in ("APPROVED", "APPROVED_WITH_DISCLAIMER")
    ) / n

    # P(all M modules succeed) = per_module_success^M
    module_counts = list(range(1, 9))
    terminals: dict[str, int] = {}
    jr_list: list[float] = []

    for mc in module_counts:
        p_all_pass = per_module_success ** mc
        p_at_least_one_fail = 1 - p_all_pass
        key = f"{mc}_modules"
        terminals[key] = round(p_at_least_one_fail * 1000)  # per-1000 scale

    # Simulate 7-module FRM directly
    seven_module_successes = 0
    all_jr_rounds = 0
    all_pm_rounds = 0
    for _ in range(n):
        module_pass = all(
            game.simulate_run().terminal in ("APPROVED", "APPROVED_WITH_DISCLAIMER")
            for _ in range(7)
        )
        if module_pass:
            seven_module_successes += 1

    seven_success_rate = seven_module_successes / n
    jr_list = [float(r.junior_rounds) for r in single_run_results]
    jr_p95 = sorted(jr_list)[int(0.95 * len(jr_list))]

    notes = [
        f"Per-module pipeline success rate: {per_module_success:.1%}",
        f"7-module FRM end-to-end success rate: {seven_success_rate:.1%}  "
        f"(expected: {per_module_success**7:.1%})",
    ]
    for mc in module_counts:
        p = per_module_success ** mc
        notes.append(f"  {mc} module(s): P(all pass) = {p:.1%}, P(at least one fail) = {1-p:.1%}")
    if per_module_success < 0.90:
        notes.append(
            "FINDING: With <90% per-module success, full 7-module FRM has high failure risk."
        )
        notes.append(
            "Mitigation: increase MAX_REVISION_ROUNDS for FRM OR add module-level retry (currently absent)."
        )

    return ScenarioResult(
        scenario="C: FRM Module-Count Sensitivity",
        n_runs=n,
        terminal_distribution=terminals,
        avg_junior_rounds=sum(jr_list) / n,
        avg_pm_rounds=sum(r.pm_rounds for r in single_run_results) / n,
        p95_junior_rounds=jr_p95,
        avg_total_payoff=0.0,
        nash_pm_threshold=None,
        nash_partner_threshold=None,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Scenario D — Revision limit optimality
# ---------------------------------------------------------------------------

def scenario_d_revision_limit_optimality(n: int = 1000, seed: int = 42) -> ScenarioResult:
    """
    Compare REVISION_LIMIT error rates across different max_junior × max_pm combinations.
    Current: (3, 2). Test: (1,1), (2,1), (2,2), (3,2), (3,3), (4,2), (4,3).
    """
    random.seed(seed)
    configs = [
        (1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (4, 2), (4, 3),
    ]

    terminals: dict[str, int] = {}
    best_config = (3, 2)
    best_ratio = -math.inf
    jr_list: list[float] = []

    for (mj, mp) in configs:
        game = AgentGame(max_junior=mj, max_pm=mp)
        results = game.run_n(n)
        approved = sum(
            1 for r in results
            if r.terminal in ("APPROVED", "APPROVED_WITH_DISCLAIMER")
        )
        limit_errors = sum(1 for r in results if r.terminal == "REVISION_LIMIT")
        avg_ticks = sum(r.total_ticks for r in results) / n
        # Ratio: success per tick (efficiency)
        ratio = approved / (avg_ticks + 1)
        key = f"j{mj}_p{mp}"
        terminals[key] = approved
        if ratio > best_ratio:
            best_ratio = ratio
            best_config = (mj, mp)
        if mj == 3 and mp == 2:
            jr_list = [float(r.junior_rounds) for r in results]

    jr_p95 = sorted(jr_list)[int(0.95 * len(jr_list))] if jr_list else 0.0

    notes = [
        f"Current config: max_junior=3, max_pm=2",
        f"Most efficient config (success/tick): max_junior={best_config[0]}, max_pm={best_config[1]}",
        "Efficiency metric = approvals / avg_ticks. Higher is better.",
    ]
    for (mj, mp) in configs:
        game = AgentGame(max_junior=mj, max_pm=mp)
        results = game.run_n(n // len(configs))
        approved = sum(1 for r in results if r.terminal in ("APPROVED", "APPROVED_WITH_DISCLAIMER"))
        key = f"j{mj}_p{mp}"
        notes.append(f"  ({mj},{mp}): success_n={approved}/{n // len(configs)}")
    if best_config != (3, 2):
        notes.append(
            f"FINDING: Current limits (3,2) are suboptimal. "
            f"Consider ({best_config[0]},{best_config[1]}) for better throughput."
        )
    else:
        notes.append("Current limits (3,2) are near-optimal for default quality distribution.")

    return ScenarioResult(
        scenario="D: Revision Limit Optimality",
        n_runs=n,
        terminal_distribution=terminals,
        avg_junior_rounds=sum(jr_list) / n if jr_list else 0.0,
        avg_pm_rounds=0.0,
        p95_junior_rounds=jr_p95,
        avg_total_payoff=0.0,
        nash_pm_threshold=None,
        nash_partner_threshold=None,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Run all scenarios
# ---------------------------------------------------------------------------

def run_all_scenarios(n: int = 1000, seed: int = 42) -> list[ScenarioResult]:
    return [
        scenario_a_threshold_calibration(n, seed),
        scenario_b_information_asymmetry(n, seed),
        scenario_c_frm_module_sensitivity(n, seed),
        scenario_d_revision_limit_optimality(n, seed),
    ]

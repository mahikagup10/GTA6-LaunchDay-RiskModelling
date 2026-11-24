"""FAIR-style Monte Carlo model.

Reproduces GTA6_FAIR_Monte_Carlo.xlsx exactly: same triangular inverse-CDF
sampling, same fixed uniform draws (seed 20261124, one (trials x 6) block per
scenario in the fixed order below), same event rules, same paired
baseline/residual comparison, same cost allocation and priority score.

Uniform draw columns per trial:
    0 threat-event frequency, 1 vulnerability, 2 event occurrence,
    3 primary loss, 4 secondary loss, 5 secondary-loss-occurs.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import poisson, spearmanr

from backend.data.config import (
    CONTROLS,
    SCENARIOS,
    THRESHOLDS_M,
    get_control,
    get_scenario,
)

DEFAULT_TRIALS = 10_000
DEFAULT_SEED = 20261124
MAX_TRIALS = 100_000
THRESHOLDS = tuple(t * 1_000_000 for t in THRESHOLDS_M)
SCENARIO_ORDER = ("launch-ddos", "source-code-theft", "insider-leak", "fake-downloads")
MAX_EVENTS = 6  # Poisson-thinning cap per trial (matches the workbook)
LAUNCH_SCENARIO = "launch-ddos"


@dataclass(frozen=True)
class SimulationInputs:
    frequency: np.ndarray
    vulnerability: np.ndarray
    primary_loss: np.ndarray
    secondary_loss: np.ndarray


def _tri_ppf(u, low, mode, high):
    """Inverse CDF of the triangular distribution (identical to the workbook formula)."""
    split = (mode - low) / (high - low)
    return np.where(
        u < split,
        low + np.sqrt(u * (high - low) * (mode - low)),
        high - np.sqrt((1 - u) * (high - low) * (high - mode)),
    )


def _draws(trials, seed):
    """Uniform draws for all four scenarios, generated in fixed order so results do not depend on which scenario is run."""
    rng = np.random.default_rng(seed)
    return {sid: rng.random((trials, 6)) for sid in SCENARIO_ORDER}


def _sample_inputs(assumptions, u):
    def tri(key, col):
        a = assumptions[key]
        return _tri_ppf(u[:, col], a["low"], a["mode"], a["high"])

    return SimulationInputs(
        frequency=tri("threatEventFrequency", 0),
        vulnerability=tri("vulnerability", 1),
        primary_loss=tri("primaryLoss", 3),
        secondary_loss=tri("secondaryLoss", 4),
    )


def _combined_effects(control_ids, scenario_id):
    effects = {
        "frequencyMultiplier": 1.0,
        "vulnerabilityMultiplier": 1.0,
        "primaryLossMultiplier": 1.0,
        "secondaryLossMultiplier": 1.0,
    }
    controls = []
    for control_id in control_ids:
        control = get_control(control_id)
        if control is None:
            raise ValueError(f"Unknown control: {control_id}")
        if scenario_id not in control["coverage"]:
            raise ValueError(f"Control '{control['name']}' does not apply to scenario '{scenario_id}'")
        controls.append(control)
        for name in effects:
            effects[name] *= control["effects"][name]
    return effects, controls


def _successes(scenario_id, inputs, u_event, effects):
    freq = inputs.frequency * effects["frequencyMultiplier"]
    vuln = inputs.vulnerability * effects["vulnerabilityMultiplier"]
    if scenario_id == LAUNCH_SCENARIO:
        # Launch window: P(at least one attempt, capped at 1) x P(attempt succeeds).
        return (u_event < np.minimum(1.0, freq) * vuln).astype(int)
    # Annual: Poisson thinning, successes ~ Poisson(TEF x Vulnerability), capped.
    mu = freq * vuln
    return sum((u_event >= poisson.cdf(k, mu)).astype(int) for k in range(MAX_EVENTS))


def _losses(scenario, inputs, u, effects):
    count = _successes(scenario["id"], inputs, u[:, 2], effects)
    secondary_occurs = u[:, 5] < scenario["probabilitySecondary"]
    primary = inputs.primary_loss * effects["primaryLossMultiplier"]
    secondary = np.where(secondary_occurs, inputs.secondary_loss * effects["secondaryLossMultiplier"], 0.0)
    return count * (primary + secondary)


def _metrics(losses):
    n = len(losses)
    metrics = {
        "mean": float(np.mean(losses)),
        "standardError": float(np.std(losses, ddof=1) / np.sqrt(n)),
        "p50": float(np.percentile(losses, 50)),
        "p90": float(np.percentile(losses, 90)),
        "p95": float(np.percentile(losses, 95)),
        "p99": float(np.percentile(losses, 99)),
        "probabilityAnyLoss": float(np.mean(losses > 0)),
        "probabilityAbove": {
            str(t): float(np.mean(losses > t * 1_000_000)) for t in THRESHOLDS_M
        },
    }
    # Legacy keys used by earlier UI components.
    metrics["probabilityAbove50m"] = metrics["probabilityAbove"]["50"]
    metrics["probabilityAbove100m"] = metrics["probabilityAbove"]["100"]
    return metrics


def _histogram(losses, edges):
    counts, _ = np.histogram(losses, bins=edges)
    return {"binEdges": [float(v) for v in edges], "counts": [int(v) for v in counts]}


def _sensitivity(inputs, losses):
    candidates = {
        "Threat event frequency": inputs.frequency,
        "Vulnerability": inputs.vulnerability,
        "Primary loss": inputs.primary_loss,
        "Secondary loss": inputs.secondary_loss,
    }
    drivers = []
    for name, values in candidates.items():
        result = spearmanr(values, losses)
        corr = 0.0 if np.isnan(result.statistic) else float(result.statistic)
        drivers.append({"name": name, "correlation": corr})
    return sorted(drivers, key=lambda item: abs(item["correlation"]), reverse=True)[:3]


def expected_cost(control):
    """Triangular mean of the cost range ($), as used in the workbook."""
    c = control["cost"]
    return (c["low"] + c["mode"] + c["high"]) / 3


def allocated_cost(selected_controls, scenario_id):
    """Each control's expected cost split equally across every scenario it covers."""
    return sum(
        expected_cost(c) / len(c["coverage"])
        for c in selected_controls
        if scenario_id in c["coverage"]
    )


def _validate(trials, seed):
    trials, seed = int(trials), int(seed)
    if trials < 1_000 or trials > MAX_TRIALS:
        raise ValueError(f"Trials must be between 1,000 and {MAX_TRIALS:,}")
    return trials, seed


def _scenario_run(scenario_id, control_ids, trials, seed, draws=None):
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    draws = draws or _draws(trials, seed)
    u = draws[scenario_id]
    inputs = _sample_inputs(scenario["assumptions"], u)
    base_fx, _ = _combined_effects([], scenario_id)
    res_fx, selected = _combined_effects(control_ids, scenario_id)
    baseline = _losses(scenario, inputs, u, base_fx)
    residual = _losses(scenario, inputs, u, res_fx)
    return scenario, inputs, baseline, residual, selected


def run_simulation(scenario_id="launch-ddos", control_ids=None, mode=None, trials=DEFAULT_TRIALS, seed=DEFAULT_SEED):
    """`mode` is accepted for backward compatibility and ignored: the loss basis is fixed per scenario
    (launch window for the DDoS scenario, one year for the others)."""
    control_ids = list(dict.fromkeys(control_ids or []))
    trials, seed = _validate(trials, seed)
    scenario, inputs, baseline, residual, selected = _scenario_run(scenario_id, control_ids, trials, seed)

    maximum = max(float(baseline.max()), float(residual.max()), 1.0)
    edges = np.linspace(0, maximum * 1.001, 31)
    bm, rm = _metrics(baseline), _metrics(residual)
    reduction = bm["mean"] - rm["mean"]
    cost = allocated_cost(selected, scenario_id)
    net = reduction - cost

    return {
        "meta": {
            "scenarioId": scenario_id,
            "analysisBasis": scenario["analysisBasis"],
            "basisLabel": "per 7-day launch window" if scenario["analysisBasis"] == "launch-window" else "per year",
            "trials": trials,
            "seed": seed,
            "currency": "USD",
            "thresholdsM": list(THRESHOLDS_M),
        },
        "baseline": {"metrics": bm, "histogram": _histogram(baseline, edges)},
        "residual": {"metrics": rm, "histogram": _histogram(residual, edges)},
        "comparison": {
            "expectedLossReduction": reduction,
            "p95Reduction": bm["p95"] - rm["p95"],
            "reductionPercent": reduction / bm["mean"] if bm["mean"] else 0.0,
        },
        "controlEconomics": {
            "selectedControlIds": control_ids,
            "estimatedCost": cost,
            "costBasis": "expected (triangular mean) cost, split equally across the scenarios each control covers",
            "lossesAvoided": reduction,
            "netBenefit": net,
            "rosi": net / cost if cost else None,
        },
        "sensitivity": _sensitivity(inputs, baseline),
    }


def run_portfolio(control_ids=None, mode=None, trials=DEFAULT_TRIALS, seed=DEFAULT_SEED):
    """One launch window plus one year of the other three scenarios, summed per trial (so P95 is a true portfolio P95)."""
    control_ids = list(dict.fromkeys(
        control_ids if control_ids is not None else [c["id"] for c in CONTROLS]
    ))
    trials, seed = _validate(trials, seed)
    selected = []
    for cid in control_ids:
        control = get_control(cid)
        if control is None:
            raise ValueError(f"Unknown control: {cid}")
        selected.append(control)

    draws = _draws(trials, seed)
    total_b = np.zeros(trials)
    total_r = np.zeros(trials)
    summaries = []
    for scenario in SCENARIOS:
        applicable = [c["id"] for c in selected if scenario["id"] in c["coverage"]]
        _, _, baseline, residual, sel = _scenario_run(scenario["id"], applicable, trials, seed, draws)
        total_b += baseline
        total_r += residual
        bm, rm = _metrics(baseline), _metrics(residual)
        cost = allocated_cost(sel, scenario["id"])
        avoided = bm["mean"] - rm["mean"]
        summaries.append({
            "scenarioId": scenario["id"],
            "scenarioName": scenario["name"],
            "analysisBasis": scenario["analysisBasis"],
            "baselineMean": bm["mean"],
            "residualMean": rm["mean"],
            "baselineP95": bm["p95"],
            "residualP95": rm["p95"],
            "lossesAvoided": avoided,
            "allocatedCost": cost,
            "netBenefit": avoided - cost,
            "selectedControlIds": applicable,
        })

    pb, pr = _metrics(total_b), _metrics(total_r)
    cost = sum(expected_cost(c) for c in selected)  # shared controls counted once
    avoided = pb["mean"] - pr["mean"]
    net = avoided - cost
    return {
        "meta": {
            "analysisBasis": "one launch window + one year",
            "trialsPerScenario": trials,
            "seed": seed,
            "currency": "USD",
            "scenarioCount": len(summaries),
            "thresholdsM": list(THRESHOLDS_M),
        },
        "portfolio": {
            "baselineMean": pb["mean"],
            "residualMean": pr["mean"],
            "baselineP95": pb["p95"],
            "residualP95": pr["p95"],
            "baselineMetrics": pb,
            "residualMetrics": pr,
            "expectedLossReduction": avoided,
            "reductionPercent": avoided / pb["mean"] if pb["mean"] else 0.0,
        },
        "controlEconomics": {
            "selectedControlIds": control_ids,
            "estimatedCost": cost,
            "costBasis": "expected (triangular mean) cost; shared controls counted once",
            "lossesAvoided": avoided,
            "netBenefit": net,
            "rosi": net / cost if cost else None,
        },
        "scenarios": summaries,
    }


def _analytic_expected(scenario, fx=None):
    a = scenario["assumptions"]
    mean = lambda k: (a[k]["low"] + a[k]["mode"] + a[k]["high"]) / 3
    fx = fx or {"frequencyMultiplier": 1, "vulnerabilityMultiplier": 1, "primaryLossMultiplier": 1, "secondaryLossMultiplier": 1}
    return (
        mean("threatEventFrequency") * fx["frequencyMultiplier"]
        * mean("vulnerability") * fx["vulnerabilityMultiplier"]
        * (mean("primaryLoss") * fx["primaryLossMultiplier"]
           + scenario["probabilitySecondary"] * mean("secondaryLoss") * fx["secondaryLossMultiplier"])
    )


def run_control_priorities(trials=DEFAULT_TRIALS, seed=DEFAULT_SEED):
    """Standalone control ranking: analytic expected loss avoided, ROSI, and the 0-100 priority score.

    Score weights (team policy, project plan): loss reduction 35, reduction per $ 25, P95-reduction proxy 20,
    scenarios helped 10, feasibility/confidence 10. Tiers: >=60 P1, >=40 P2, else P3.
    """
    trials, seed = _validate(trials, seed)
    draws = _draws(trials, seed)
    base = {}
    for s in SCENARIOS:
        _, _, baseline, _, _ = _scenario_run(s["id"], [], trials, seed, draws)
        base[s["id"]] = (_analytic_expected(s), float(np.percentile(baseline, 95)))

    rows = []
    for c in CONTROLS:
        avoided_by = {}
        p95_proxy = 0.0
        for s in SCENARIOS:
            if s["id"] in c["coverage"]:
                e0, p95 = base[s["id"]]
                e1 = _analytic_expected(s, c["effects"])
                avoided_by[s["id"]] = e0 - e1
                p95_proxy += (e0 - e1) / e0 * p95
        total = sum(avoided_by.values())
        cost = expected_cost(c)
        rows.append({
            "controlId": c["id"], "name": c["name"], "expectedCost": cost,
            "lossAvoidedByScenario": avoided_by, "totalLossAvoided": total,
            "netBenefit": total - cost, "rosi": (total - cost) / cost,
            "reductionPerDollar": total / cost, "p95ReductionProxy": p95_proxy,
            "scenariosHelped": len(c["coverage"]), "feasibility": c["feasibility"],
        })
    mx = lambda k: max(r[k] for r in rows) or 1
    for r in rows:
        r["priorityScore"] = (
            35 * r["totalLossAvoided"] / mx("totalLossAvoided")
            + 25 * r["reductionPerDollar"] / mx("reductionPerDollar")
            + 20 * r["p95ReductionProxy"] / mx("p95ReductionProxy")
            + 10 * r["scenariosHelped"] / 4
            + 10 * r["feasibility"] / 5
        )
        r["tier"] = "Priority 1" if r["priorityScore"] >= 60 else "Priority 2" if r["priorityScore"] >= 40 else "Priority 3"
    return {"meta": {"trials": trials, "seed": seed}, "controls": sorted(rows, key=lambda r: -r["priorityScore"])}

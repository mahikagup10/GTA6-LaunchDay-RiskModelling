"""FAIR-style Monte Carlo engine for the Cyber Attack Decision Workbench.

Design notes (documented in docs/FAIR_MODEL.md):
- Launch-Day DDoS is a launch-event model: Bernoulli attack attempt x Bernoulli
  conditional success, then component losses for one material outage.
- The other scenarios are annual: Poisson(threat event frequency) attempts,
  each succeeding with the conditional-success probability.
- Every input and every random decision has its own seeded stream, so baseline
  and residual runs share draws (common random numbers). Controls only shrink
  factors, so residual loss is never higher than baseline loss in any trial.
- Controls multiply targeted factors by (1 - effectiveness). Effectiveness is
  sampled per trial from the control's low / likely / high range and stacks
  multiplicatively across controls.
"""

from __future__ import annotations

import zlib
from functools import lru_cache

import numpy as np
from scipy.stats import poisson, spearmanr

from backend.data.config import (
    CONTROLS,
    MODEL_SEED,
    MODEL_TRIALS,
    READINESS_MODEL,
    SCENARIOS,
    TIME_BASES,
    get_control,
    get_scenario,
)


DEFAULT_TRIALS = MODEL_TRIALS
DEFAULT_SEED = MODEL_SEED
MIN_TRIALS = 1_000
MAX_TRIALS = 200_000
HISTOGRAM_BINS = 30
AMORTIZATION_YEARS = 3
LAUNCHES_PER_YEAR = 1
TOP_DRIVERS = 5

PRIORITY_WEIGHTS = {
    "expectedLossReduction": 35,
    "reductionPerDollar": 25,
    "p95Reduction": 20,
    "scenarioCoverage": 10,
    "feasibilityConfidence": 10,
}
PRIORITY_TIERS = [
    (60, 1, "Priority 1 - Implement before launch"),
    (40, 2, "Priority 2 - Implement next"),
    (0, 3, "Priority 3 - Evaluate or monitor"),
]
HEAT_LEVELS = [(0.30, "high"), (0.10, "medium"), (0.0, "low")]


# ---------------------------------------------------------------------------
# Random streams
# ---------------------------------------------------------------------------

def _key(value):
    return zlib.crc32(str(value).encode("utf-8"))


def _rng(seed, *labels):
    return np.random.default_rng(np.random.SeedSequence([int(seed)] + [_key(label) for label in labels]))


def _triangular(rng, low, mode, high, size):
    if high <= low:
        return np.full(size, float(mode))
    return rng.triangular(low, mode, high, size)


def _sample_inputs(scenario, trials, seed):
    samples = {}
    for item in scenario["inputs"]:
        rng = _rng(seed, scenario["id"], "input", item["key"])
        samples[item["key"]] = _triangular(rng, item["low"], item["mode"], item["high"], trials)
    return samples


def _uniform(scenario_id, label, trials, seed, columns=None):
    rng = _rng(seed, scenario_id, "uniform", label)
    shape = trials if columns is None else (trials, columns)
    return rng.random(shape)


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

def _validate_controls(control_ids, scenario_id):
    controls = []
    for control_id in control_ids:
        control = get_control(control_id)
        if control is None:
            raise ValueError(f"Unknown control: {control_id}")
        if scenario_id not in control["coverage"]:
            raise ValueError(f"Control '{control['name']}' does not apply to scenario '{scenario_id}'")
        controls.append(control)
    return controls


def _multipliers(scenario_id, controls, trials, seed):
    """Return {factor: array of multipliers} for the selected controls."""
    multipliers = {}
    for control in controls:
        for factor, effectiveness in control["effects"][scenario_id].items():
            rng = _rng(seed, scenario_id, "control", control["id"], factor)
            sampled = _triangular(rng, effectiveness["low"], effectiveness["likely"], effectiveness["high"], trials)
            multipliers[factor] = multipliers.get(factor, 1.0) * (1.0 - sampled)
    return multipliers


def comparable_cost(control, time_basis, point="likely"):
    """Cost of a control on the scenario's time basis (see METHODOLOGY['costRule'])."""
    cost = control["cost"]
    value = float(cost[point])
    basis = cost["basis"]
    if time_basis == "launch-event":
        return value  # full first-year cost charged to the launch event
    if basis == "annual":
        return value
    if basis == "one-time":
        return value / AMORTIZATION_YEARS
    if basis == "per-launch":
        return value * LAUNCHES_PER_YEAR
    raise ValueError(f"Unknown cost basis: {basis}")


def first_year_cost(control, point="likely"):
    return float(control["cost"][point])


# ---------------------------------------------------------------------------
# Core simulation
# ---------------------------------------------------------------------------

class _Draws:
    """Inputs and uniforms for one scenario, shared by baseline and residual runs."""

    def __init__(self, scenario, trials, seed):
        self.scenario = scenario
        self.trials = trials
        self.seed = seed
        self.samples = _sample_inputs(scenario, trials, seed)
        sid = scenario["id"]
        self.u_frequency = _uniform(sid, "frequency", trials, seed)
        self.u_success = _uniform(sid, "success", trials, seed)
        self.u_secondary = _uniform(sid, "secondary", trials, seed)
        self._success_matrix = None

    def success_matrix(self, columns):
        if self._success_matrix is None or self._success_matrix.shape[1] < columns:
            self._success_matrix = _uniform(self.scenario["id"], "success-events", self.trials, self.seed, columns)
        return self._success_matrix[:, :columns]


def _factor(draws, multipliers, key, clip_probability=False):
    value = draws.samples[key] * multipliers.get(key, 1.0)
    return np.clip(value, 0.0, 1.0) if clip_probability else value


def _losses(draws, multipliers):
    """Return (total_loss, event_count, primary_per_event, secondary_per_event)."""
    model = draws.scenario["model"]
    frequency = _factor(draws, multipliers, model["frequencyKey"], clip_probability=model["type"] == "launch-event")
    success = _factor(draws, multipliers, model["successKey"], clip_probability=True)

    if model["type"] == "launch-event":
        attack = draws.u_frequency < frequency
        events = (attack & (draws.u_success < success)).astype(int)
    elif model["type"] == "annual":
        # Inverse-CDF Poisson keeps counts monotone in frequency across runs.
        attempts = poisson.ppf(draws.u_frequency, np.maximum(frequency, 1e-12)).astype(int)
        max_attempts = int(attempts.max()) if attempts.size else 0
        if max_attempts == 0:
            events = np.zeros(draws.trials, dtype=int)
        else:
            matrix = draws.success_matrix(max_attempts)
            index = np.arange(max_attempts)[None, :]
            events = ((matrix < success[:, None]) & (index < attempts[:, None])).sum(axis=1)
    else:
        raise ValueError(f"Unknown model type: {model['type']}")

    primary = np.zeros(draws.trials)
    if model["interruptionKeys"]:
        interruption = np.ones(draws.trials)
        for key in model["interruptionKeys"]:
            interruption = interruption * _factor(draws, multipliers, key, clip_probability=key.endswith("Fraction"))
        primary = primary + interruption
    for key in model["primaryKeys"]:
        primary = primary + _factor(draws, multipliers, key)

    secondary_probability = _factor(draws, multipliers, model["secondaryProbabilityKey"], clip_probability=True)
    secondary_occurs = draws.u_secondary < secondary_probability
    secondary = np.zeros(draws.trials)
    for key in model["secondaryKeys"]:
        secondary = secondary + _factor(draws, multipliers, key)
    secondary = secondary * secondary_occurs

    total = events * (primary + secondary)
    return total, events, primary, secondary


def _metrics(losses, thresholds):
    metrics = {
        "mean": float(np.mean(losses)),
        "p50": float(np.percentile(losses, 50)),
        "p90": float(np.percentile(losses, 90)),
        "p95": float(np.percentile(losses, 95)),
        "p99": float(np.percentile(losses, 99)),
        "max": float(np.max(losses)),
        "probabilityOfLoss": float(np.mean(losses > 0)),
        "probabilityAbove50m": float(np.mean(losses > 50_000_000)),
        "probabilityAbove100m": float(np.mean(losses > 100_000_000)),
        "exceedance": [
            {"threshold": float(threshold), "probability": float(np.mean(losses > threshold))}
            for threshold in thresholds
        ],
    }
    positive = losses[losses > 0]
    metrics["meanGivenLoss"] = float(np.mean(positive)) if positive.size else 0.0
    return metrics


def _histogram(losses, edges):
    """Histogram of trials with a loss; zero-loss trials are reported separately so they do not hide the shape."""
    positive = losses[losses > 0]
    counts, _ = np.histogram(positive, bins=edges)
    return {
        "binEdges": [float(value) for value in edges],
        "counts": [int(value) for value in counts],
        "zeroCount": int(losses.size - positive.size),
        "zeroShare": float((losses.size - positive.size) / losses.size) if losses.size else 0.0,
    }


def _sensitivity(scenario, draws, losses):
    labels = {item["key"]: item["label"] for item in scenario["inputs"]}
    drivers = []
    for key, values in draws.samples.items():
        result = spearmanr(values, losses)
        correlation = 0.0 if np.isnan(result.statistic) else float(result.statistic)
        drivers.append({"key": key, "name": labels[key], "correlation": correlation})
    drivers.sort(key=lambda item: abs(item["correlation"]), reverse=True)
    return drivers[:TOP_DRIVERS]


def _tornado(scenario, draws):
    """One-at-a-time swing: mean loss with each input fixed at its low vs high value (others still sampled)."""
    labels = {item["key"]: item for item in scenario["inputs"]}
    rows = []
    for key, original in list(draws.samples.items()):
        item = labels[key]
        means = {}
        for point in ("low", "high"):
            draws.samples[key] = np.full(draws.trials, float(item[point]))
            losses, _, _, _ = _losses(draws, {})
            means[point] = float(np.mean(losses))
        draws.samples[key] = original
        rows.append({
            "key": key,
            "name": item["label"],
            "lowValue": item["low"],
            "highValue": item["high"],
            "meanAtLow": means["low"],
            "meanAtHigh": means["high"],
            "swing": means["high"] - means["low"],
        })
    rows.sort(key=lambda row: abs(row["swing"]), reverse=True)
    return rows[:TOP_DRIVERS]


def _check_trials(trials, seed):
    trials = int(trials)
    seed = int(seed)
    if trials < MIN_TRIALS or trials > MAX_TRIALS:
        raise ValueError(f"Trials must be between {MIN_TRIALS:,} and {MAX_TRIALS:,}")
    return trials, seed


def _scenario_or_error(scenario_id):
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    return scenario


def simulate_losses(scenario_id, control_ids=(), trials=DEFAULT_TRIALS, seed=DEFAULT_SEED):
    """Low-level helper used by tests and exports: returns baseline and residual loss arrays plus draws."""
    trials, seed = _check_trials(trials, seed)
    scenario = _scenario_or_error(scenario_id)
    controls = _validate_controls(list(dict.fromkeys(control_ids or [])), scenario_id)
    draws = _Draws(scenario, trials, seed)
    baseline, *_ = _losses(draws, {})
    residual, *_ = _losses(draws, _multipliers(scenario_id, controls, trials, seed))
    return baseline, residual, draws


def _economics(scenario, controls, baseline_metrics, residual_metrics):
    time_basis = scenario["timeBasis"]
    reduction = baseline_metrics["mean"] - residual_metrics["mean"]
    cost = sum(comparable_cost(control, time_basis) for control in controls)
    cost_low = sum(comparable_cost(control, time_basis, "low") for control in controls)
    cost_high = sum(comparable_cost(control, time_basis, "high") for control in controls)
    net = reduction - cost
    return {
        "selectedControlIds": [control["id"] for control in controls],
        "timeBasis": time_basis,
        "costBasisNote": (
            "Full first-year cost charged to the launch event (conservative)."
            if time_basis == "launch-event"
            else f"Annualized: annual cost + one-time cost / {AMORTIZATION_YEARS} years + per-launch cost x {LAUNCHES_PER_YEAR}."
        ),
        "estimatedCost": cost,
        "costRange": {"low": cost_low, "high": cost_high},
        "lossesAvoided": reduction,
        "costOfInaction": reduction,
        "netBenefit": net,
        "rosi": net / cost if cost else None,
        "p95Reduction": baseline_metrics["p95"] - residual_metrics["p95"],
    }


def run_simulation(
    scenario_id="launch-ddos",
    control_ids=None,
    mode=None,
    trials=DEFAULT_TRIALS,
    seed=DEFAULT_SEED,
    include_breakdown=True,
):
    """Run baseline and selected-control residual simulations for one scenario.

    `mode` is accepted for backward compatibility and ignored: each scenario has a fixed time basis.
    """
    trials, seed = _check_trials(trials, seed)
    scenario = _scenario_or_error(scenario_id)
    control_ids = list(dict.fromkeys(control_ids or []))
    controls = _validate_controls(control_ids, scenario_id)

    draws = _Draws(scenario, trials, seed)
    baseline_losses, baseline_events, _, _ = _losses(draws, {})
    residual_losses, residual_events, _, _ = _losses(draws, _multipliers(scenario_id, controls, trials, seed))

    maximum = max(float(np.max(baseline_losses)), float(np.max(residual_losses)), 1.0)
    edges = np.linspace(0, maximum * 1.001, HISTOGRAM_BINS + 1)
    thresholds = scenario["thresholds"]
    baseline_metrics = _metrics(baseline_losses, thresholds)
    residual_metrics = _metrics(residual_losses, thresholds)
    baseline_metrics["expectedEvents"] = float(np.mean(baseline_events))
    residual_metrics["expectedEvents"] = float(np.mean(residual_events))
    reduction = baseline_metrics["mean"] - residual_metrics["mean"]

    result = {
        "meta": {
            "scenarioId": scenario_id,
            "scenarioName": scenario["name"],
            "timeBasis": scenario["timeBasis"],
            "timeBasisLabel": TIME_BASES[scenario["timeBasis"]]["label"],
            "timeWindow": TIME_BASES[scenario["timeBasis"]]["window"],
            "analysisMode": scenario["timeBasis"],
            "trials": trials,
            "seed": seed,
            "currency": "USD",
            "thresholds": [float(value) for value in thresholds],
        },
        "baseline": {"metrics": baseline_metrics, "histogram": _histogram(baseline_losses, edges)},
        "residual": {"metrics": residual_metrics, "histogram": _histogram(residual_losses, edges)},
        "comparison": {
            "expectedLossReduction": reduction,
            "reductionPercent": reduction / baseline_metrics["mean"] if baseline_metrics["mean"] else 0.0,
            "p95Reduction": baseline_metrics["p95"] - residual_metrics["p95"],
            "p90Reduction": baseline_metrics["p90"] - residual_metrics["p90"],
        },
        "controlEconomics": _economics(scenario, controls, baseline_metrics, residual_metrics),
        "sensitivity": _sensitivity(scenario, draws, baseline_losses),
        "tornado": _tornado(scenario, draws),
        "readiness": readiness(control_ids_all_scenarios(control_ids)),
    }

    if include_breakdown:
        breakdown = []
        for control in controls:
            alone, _, _, _ = _losses(draws, _multipliers(scenario_id, [control], trials, seed))
            alone_mean = float(np.mean(alone))
            alone_cost = comparable_cost(control, scenario["timeBasis"])
            alone_reduction = baseline_metrics["mean"] - alone_mean
            breakdown.append({
                "controlId": control["id"],
                "standaloneLossReduction": alone_reduction,
                "standaloneP95Reduction": baseline_metrics["p95"] - float(np.percentile(alone, 95)),
                "comparableCost": alone_cost,
                "standaloneNetBenefit": alone_reduction - alone_cost,
                "standaloneRosi": (alone_reduction - alone_cost) / alone_cost if alone_cost else None,
            })
        result["controlBreakdown"] = breakdown
    return result


def control_ids_all_scenarios(control_ids):
    return [control_id for control_id in control_ids if get_control(control_id) is not None]


# ---------------------------------------------------------------------------
# Readiness index
# ---------------------------------------------------------------------------

def _band(score):
    for band in READINESS_MODEL["bands"]:
        if score >= band["min"]:
            return band["label"]
    return READINESS_MODEL["bands"][-1]["label"]


def readiness(control_ids=()):
    selected = set(control_ids or [])
    components = []
    current_total = 0.0
    proposed_total = 0.0
    for component in READINESS_MODEL["components"]:
        level = component["current"]
        drivers = []
        for control in CONTROLS:
            if control["id"] not in selected:
                continue
            for contribution in control.get("readiness", []):
                if contribution["component"] != component["id"]:
                    continue
                if not set(contribution.get("requires", [])).issubset(selected):
                    continue
                if contribution["level"] > level:
                    level = contribution["level"]
                if control["id"] not in drivers:
                    drivers.append(control["id"])
        current_points = component["weight"] * component["current"]
        proposed_points = component["weight"] * level
        current_total += current_points
        proposed_total += proposed_points
        components.append({
            "id": component["id"],
            "name": component["name"],
            "weight": component["weight"],
            "currentLevel": component["current"],
            "proposedLevel": level,
            "currentPoints": current_points,
            "proposedPoints": proposed_points,
            "drivers": drivers,
            "currentRationale": component["currentRationale"],
        })
    return {
        "current": {"score": round(current_total, 1), "band": _band(current_total)},
        "proposed": {"score": round(proposed_total, 1), "band": _band(proposed_total)},
        "components": components,
        "note": READINESS_MODEL["note"],
    }


# ---------------------------------------------------------------------------
# Cross-scenario views
# ---------------------------------------------------------------------------

def _heat_level(share):
    for minimum, label in HEAT_LEVELS:
        if share >= minimum:
            return label
    return "low"


def _feasibility(control):
    weeks = control["implementationWeeks"]["mode"]
    if weeks <= 4:
        return 1.0
    if weeks <= 8:
        return 0.6
    return 0.3


def _confidence_score(control):
    return {"high": 1.0, "medium": 0.6, "low": 0.3}.get(control["confidence"], 0.3)


@lru_cache(maxsize=8)
def _baseline_cache(trials, seed):
    output = {}
    for scenario in SCENARIOS:
        draws = _Draws(scenario, trials, seed)
        losses, events, _, _ = _losses(draws, {})
        output[scenario["id"]] = (draws, losses, _metrics(losses, scenario["thresholds"]), float(np.mean(events)))
    return output


@lru_cache(maxsize=8)
def _control_priorities_cached(trials, seed):
    baselines = _baseline_cache(trials, seed)
    rows = []
    for control in CONTROLS:
        per_scenario = {}
        for scenario_id in control["coverage"]:
            scenario = get_scenario(scenario_id)
            draws, baseline_losses, baseline_metrics, _ = baselines[scenario_id]
            alone, _, _, _ = _losses(draws, _multipliers(scenario_id, [control], trials, seed))
            reduction = baseline_metrics["mean"] - float(np.mean(alone))
            p95_reduction = baseline_metrics["p95"] - float(np.percentile(alone, 95))
            share = reduction / baseline_metrics["mean"] if baseline_metrics["mean"] else 0.0
            per_scenario[scenario_id] = {
                "scenarioId": scenario_id,
                "timeBasis": scenario["timeBasis"],
                "lossReduction": reduction,
                "p95Reduction": p95_reduction,
                "reductionShare": share,
                "level": _heat_level(share),
                "comparableCost": comparable_cost(control, scenario["timeBasis"]),
                "factors": list(control["effects"][scenario_id].keys()),
                "attackSteps": control["attackSteps"].get(scenario_id, []),
            }
        first_year_reduction = sum(item["lossReduction"] for item in per_scenario.values())
        p95_total = sum(max(item["p95Reduction"], 0.0) for item in per_scenario.values())
        cost = first_year_cost(control)
        rows.append({
            "controlId": control["id"],
            "name": control["name"],
            "shortName": control.get("shortName", control["name"]),
            "group": control["group"],
            "scenarios": per_scenario,
            "firstYearLossReduction": first_year_reduction,
            "firstYearCost": cost,
            "firstYearCostRange": {"low": first_year_cost(control, "low"), "high": first_year_cost(control, "high")},
            "firstYearNetBenefit": first_year_reduction - cost,
            "firstYearRosi": (first_year_reduction - cost) / cost if cost else None,
            "reductionPerDollar": first_year_reduction / cost if cost else 0.0,
            "p95ReductionTotal": p95_total,
            "scenariosHelped": sum(1 for item in per_scenario.values() if item["lossReduction"] > 0),
            "feasibility": _feasibility(control),
            "confidenceScore": _confidence_score(control),
        })

    max_reduction = max((row["firstYearLossReduction"] for row in rows), default=0.0) or 1.0
    max_per_dollar = max((row["reductionPerDollar"] for row in rows), default=0.0) or 1.0
    max_p95 = max((row["p95ReductionTotal"] for row in rows), default=0.0) or 1.0
    for row in rows:
        parts = {
            "expectedLossReduction": PRIORITY_WEIGHTS["expectedLossReduction"] * max(row["firstYearLossReduction"], 0) / max_reduction,
            "reductionPerDollar": PRIORITY_WEIGHTS["reductionPerDollar"] * max(row["reductionPerDollar"], 0) / max_per_dollar,
            "p95Reduction": PRIORITY_WEIGHTS["p95Reduction"] * row["p95ReductionTotal"] / max_p95,
            "scenarioCoverage": PRIORITY_WEIGHTS["scenarioCoverage"] * row["scenariosHelped"] / len(SCENARIOS),
            "feasibilityConfidence": PRIORITY_WEIGHTS["feasibilityConfidence"] * (row["feasibility"] + row["confidenceScore"]) / 2,
        }
        score = round(sum(parts.values()), 1)
        tier = next(item for item in PRIORITY_TIERS if score >= item[0])
        row["scoreBreakdown"] = {key: round(value, 1) for key, value in parts.items()}
        row["priorityScore"] = score
        row["priority"] = tier[1]
        row["priorityLabel"] = tier[2]
        row["elevated"] = False
        control = get_control(row["controlId"])
        if control.get("prerequisite") and row["priority"] > 1:
            row["priority"] = 1
            row["priorityLabel"] = PRIORITY_TIERS[0][2]
            row["elevated"] = True
            row["elevationReason"] = (
                "Elevated as a prerequisite: testing is what moves protection and failover from 'implemented' to "
                "'implemented and tested' in the readiness index, and it validates every other launch control."
            )

    rows.sort(key=lambda row: (row["priority"], -row["priorityScore"]))
    sequence = 1
    for row in sorted(rows, key=lambda r: (r["priority"], not get_control(r["controlId"]).get("prerequisite", False),
                                            get_control(r["controlId"])["implementationWeeks"]["mode"])):
        row["sequence"] = sequence
        sequence += 1
    return rows


def control_priorities(trials=DEFAULT_TRIALS, seed=DEFAULT_SEED):
    trials, seed = _check_trials(trials, seed)
    rows = _control_priorities_cached(trials, seed)
    heatmap = {
        "scenarios": [{"id": s["id"], "name": s["name"], "timeBasis": s["timeBasis"]} for s in SCENARIOS],
        "controls": [{"id": row["controlId"], "name": row["name"], "shortName": row["shortName"]} for row in rows],
        "cells": [
            {
                "controlId": row["controlId"],
                "scenarioId": scenario["id"],
                **(row["scenarios"].get(scenario["id"]) or {"level": "none", "lossReduction": 0.0, "reductionShare": 0.0,
                                                            "factors": [], "attackSteps": [], "timeBasis": scenario["timeBasis"]}),
            }
            for row in rows
            for scenario in SCENARIOS
        ],
        "levels": {"high": ">= 30% of scenario mean loss", "medium": "10-30%", "low": "< 10%", "none": "Not covered"},
    }
    return {
        "meta": {
            "trials": trials,
            "seed": seed,
            "basis": "First-year view: launch-event reduction for Launch-Day DDoS plus one year of annual reductions; full first-year control cost.",
            "weights": PRIORITY_WEIGHTS,
            "tiers": [{"minimum": t[0], "priority": t[1], "label": t[2]} for t in PRIORITY_TIERS],
        },
        "controls": rows,
        "heatmap": heatmap,
    }


def scenario_overview(trials=DEFAULT_TRIALS, seed=DEFAULT_SEED):
    """Baseline metrics for all four scenarios plus model-derived heat-map placement."""
    trials, seed = _check_trials(trials, seed)
    baselines = _baseline_cache(trials, seed)
    items = []
    for scenario in SCENARIOS:
        _, _, metrics, expected_events = baselines[scenario["id"]]
        probability = metrics["probabilityOfLoss"]
        impact = metrics["meanGivenLoss"]
        likelihood_level = 1 + sum(probability >= cut for cut in (0.05, 0.15, 0.30, 0.50))
        impact_level = 1 + sum(impact >= cut for cut in (2_000_000, 5_000_000, 15_000_000, 40_000_000))
        items.append({
            "scenarioId": scenario["id"],
            "name": scenario["name"],
            "severity": scenario["severity"],
            "timeBasis": scenario["timeBasis"],
            "timeBasisLabel": TIME_BASES[scenario["timeBasis"]]["label"],
            "metrics": metrics,
            "expectedEvents": expected_events,
            "likelihoodLevel": likelihood_level,
            "impactLevel": impact_level,
        })
    return {
        "meta": {
            "trials": trials,
            "seed": seed,
            "heatmapRule": (
                "Likelihood level from the probability of at least one loss event in the period "
                "(cuts at 5%, 15%, 30%, 50%); impact level from mean loss given a loss "
                "(cuts at $2M, $5M, $15M, $40M)."
            ),
        },
        "scenarios": items,
    }


def run_portfolio(control_ids=None, mode=None, trials=DEFAULT_TRIALS, seed=DEFAULT_SEED):
    """First-year portfolio: Launch-Day DDoS (one launch event) plus one year of each annual scenario."""
    trials, seed = _check_trials(trials, seed)
    control_ids = list(dict.fromkeys(
        control_ids if control_ids is not None else [control["id"] for control in CONTROLS]
    ))
    selected = []
    for control_id in control_ids:
        control = get_control(control_id)
        if control is None:
            raise ValueError(f"Unknown control: {control_id}")
        selected.append(control)

    summaries = []
    total_baseline = 0.0
    total_residual = 0.0
    for scenario in SCENARIOS:
        applicable = [control for control in selected if scenario["id"] in control["coverage"]]
        draws = _Draws(scenario, trials, seed)
        baseline_losses, _, _, _ = _losses(draws, {})
        residual_losses, _, _, _ = _losses(draws, _multipliers(scenario["id"], applicable, trials, seed))
        baseline_mean = float(np.mean(baseline_losses))
        residual_mean = float(np.mean(residual_losses))
        total_baseline += baseline_mean
        total_residual += residual_mean
        summaries.append({
            "scenarioId": scenario["id"],
            "scenarioName": scenario["name"],
            "timeBasis": scenario["timeBasis"],
            "timeBasisLabel": TIME_BASES[scenario["timeBasis"]]["label"],
            "baselineMean": baseline_mean,
            "residualMean": residual_mean,
            "lossesAvoided": baseline_mean - residual_mean,
            "baselineP95": float(np.percentile(baseline_losses, 95)),
            "residualP95": float(np.percentile(residual_losses, 95)),
            "selectedControlIds": [control["id"] for control in applicable],
        })

    cost = sum(first_year_cost(control) for control in selected)
    cost_low = sum(first_year_cost(control, "low") for control in selected)
    cost_high = sum(first_year_cost(control, "high") for control in selected)
    avoided = total_baseline - total_residual
    net = avoided - cost
    return {
        "meta": {
            "analysisMode": "first-year",
            "basis": "First-year view: one GTA VI launch event plus 12 months of the three annual scenarios. Shared controls are costed once at full first-year cost.",
            "trialsPerScenario": trials,
            "seed": seed,
            "currency": "USD",
            "scenarioCount": len(summaries),
        },
        "portfolio": {
            "baselineMean": total_baseline,
            "residualMean": total_residual,
            "expectedLossReduction": avoided,
            "reductionPercent": avoided / total_baseline if total_baseline else 0.0,
        },
        "controlEconomics": {
            "selectedControlIds": control_ids,
            "estimatedCost": cost,
            "costRange": {"low": cost_low, "high": cost_high},
            "lossesAvoided": avoided,
            "netBenefit": net,
            "rosi": net / cost if cost else None,
        },
        "scenarios": summaries,
        "readiness": readiness(control_ids),
    }

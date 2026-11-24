from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.stats import binom, poisson, spearmanr

from backend.data.config import CONTROLS, SCENARIOS, get_control, get_scenario

DEFAULT_TRIALS, DEFAULT_SEED, MAX_TRIALS = 10_000, 243, 100_000
THRESHOLDS = (10_000_000, 25_000_000, 50_000_000, 100_000_000)
ASSUMPTION_KEYS = ("threatEventFrequency", "vulnerability", "primaryLoss", "secondaryLoss")
ESTIMATE_KEYS = ("low", "mode", "high")


@dataclass(frozen=True)
class SimulationInputs:
    frequency: np.ndarray
    vulnerability: np.ndarray
    primary_loss: np.ndarray
    secondary_loss: np.ndarray


@dataclass(frozen=True)
class SimulationDraws:
    event: np.ndarray
    success: np.ndarray
    secondary: np.ndarray


def _profile(scenario, profile_id):
    profile_id = profile_id or scenario.get("defaultAssumptionProfileId", "evidence-anchored")
    profiles = scenario.get("assumptionProfiles", {})
    if profiles and profile_id not in profiles:
        raise ValueError(f"Unknown assumption profile: {profile_id}")
    if profiles:
        return profile_id, profiles[profile_id]
    return "configured", {"assumptions": scenario["assumptions"], "secondaryLossProbability": {"value": 1.0}}


def _validated_assumptions(profile, overrides):
    configured = profile["assumptions"]
    probability = float(profile["secondaryLossProbability"]["value"])
    if overrides is None:
        return configured, probability
    if not isinstance(overrides, dict):
        raise ValueError("Custom assumptions must be an object")
    unknown = set(overrides) - set(ASSUMPTION_KEYS) - {"secondaryLossProbability"}
    if unknown:
        raise ValueError(f"Unknown assumption: {sorted(unknown)[0]}")

    validated = {}
    for key in ASSUMPTION_KEYS:
        supplied = overrides.get(key, {})
        if not isinstance(supplied, dict):
            raise ValueError(f"{key} must contain low, mode, and high values")
        estimate = {}
        for point in ESTIMATE_KEYS:
            raw = supplied.get(point, configured[key][point])
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                raise ValueError(f"{key}.{point} must be numeric")
            estimate[point] = float(raw)
            if not math.isfinite(estimate[point]):
                raise ValueError(f"{key}.{point} must be finite")
        if not estimate["low"] <= estimate["mode"] <= estimate["high"]:
            raise ValueError(f"{key} must satisfy low <= mode <= high")
        if estimate["low"] < 0:
            raise ValueError(f"{key} cannot be negative")
        if key == "vulnerability" and estimate["high"] > 1:
            raise ValueError("vulnerability values must be between 0 and 1")
        validated[key] = estimate

    raw_probability = overrides.get("secondaryLossProbability", probability)
    if isinstance(raw_probability, dict):
        raw_probability = raw_probability.get("value", probability)
    if isinstance(raw_probability, bool) or not isinstance(raw_probability, (int, float)):
        raise ValueError("secondaryLossProbability must be numeric")
    probability = float(raw_probability)
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("secondaryLossProbability must be between 0 and 1")
    return validated, probability


def _sample(assumptions, trials, seed):
    rng = np.random.default_rng(seed)
    triangular = lambda key: rng.triangular(assumptions[key]["low"], assumptions[key]["mode"], assumptions[key]["high"], trials)
    inputs = SimulationInputs(triangular("threatEventFrequency"), triangular("vulnerability"), triangular("primaryLoss"), triangular("secondaryLoss"))
    return inputs, SimulationDraws(rng.random(trials), rng.random(trials), rng.random(trials))


def _effects(control_ids, scenario_id):
    combined = {"frequencyMultiplier": 1.0, "vulnerabilityMultiplier": 1.0, "primaryLossMultiplier": 1.0, "secondaryLossMultiplier": 1.0}
    controls = []
    for control_id in control_ids:
        control = get_control(control_id)
        if control is None:
            raise ValueError(f"Unknown control: {control_id}")
        if scenario_id not in control["coverage"]:
            raise ValueError(f"Control '{control['name']}' does not apply to scenario '{scenario_id}'")
        controls.append(control)
        for name in combined:
            combined[name] *= control["effects"][name]
    return combined, controls


def _losses(inputs, draws, mode, effects, secondary_probability):
    frequency = np.clip(inputs.frequency * effects["frequencyMultiplier"], 0, None)
    vulnerability = np.clip(inputs.vulnerability * effects["vulnerabilityMultiplier"], 0, 1)
    if mode == "launch-event":
        threats = (draws.event < np.clip(frequency, 0, 1)).astype(int)
        successes = threats * (draws.success < vulnerability).astype(int)
        secondary_events = successes * (draws.secondary < secondary_probability).astype(int)
    elif mode == "annual":
        threats = poisson.ppf(draws.event, frequency).astype(int)
        successes = binom.ppf(draws.success, threats, vulnerability).astype(int)
        secondary_events = binom.ppf(draws.secondary, successes, secondary_probability).astype(int)
    else:
        raise ValueError("Mode must be 'launch-event' or 'annual'")
    return successes * inputs.primary_loss * effects["primaryLossMultiplier"] + secondary_events * inputs.secondary_loss * effects["secondaryLossMultiplier"]


def _metrics(losses):
    result = {"mean": float(np.mean(losses)), "p50": float(np.percentile(losses, 50)), "p90": float(np.percentile(losses, 90)), "p95": float(np.percentile(losses, 95)), "p99": float(np.percentile(losses, 99))}
    result.update({f"probabilityAbove{int(value / 1_000_000)}m": float(np.mean(losses > value)) for value in THRESHOLDS})
    return result


def _histogram(losses, edges):
    counts, _ = np.histogram(losses, bins=edges)
    return {"binEdges": [float(value) for value in edges], "counts": [int(value) for value in counts]}


def _sensitivity(inputs, losses):
    candidates = {"Threat event frequency": inputs.frequency, "Vulnerability": inputs.vulnerability, "Primary loss": inputs.primary_loss, "Secondary loss": inputs.secondary_loss}
    drivers = []
    for name, values in candidates.items():
        result = spearmanr(values, losses)
        statistic = result.statistic if hasattr(result, "statistic") else result[0]
        drivers.append({"name": name, "correlation": 0.0 if np.isnan(statistic) else float(statistic)})
    return sorted(drivers, key=lambda item: abs(item["correlation"]), reverse=True)[:3]


def _tornado(assumptions, inputs, draws, mode, probability, scenario_id):
    no_effect, _ = _effects([], scenario_id)
    fields = {"Threat event frequency": ("frequency", "threatEventFrequency"), "Vulnerability": ("vulnerability", "vulnerability"), "Primary loss": ("primary_loss", "primaryLoss"), "Secondary loss": ("secondary_loss", "secondaryLoss")}
    original = {field: getattr(inputs, field) for field, _ in fields.values()}
    output = []
    for name, (field, key) in fields.items():
        low_inputs = SimulationInputs(**{**original, field: np.full_like(original[field], assumptions[key]["low"])})
        high_inputs = SimulationInputs(**{**original, field: np.full_like(original[field], assumptions[key]["high"])})
        low_mean = float(np.mean(_losses(low_inputs, draws, mode, no_effect, probability)))
        high_mean = float(np.mean(_losses(high_inputs, draws, mode, no_effect, probability)))
        output.append({"name": name, "lowMean": low_mean, "highMean": high_mean, "swing": abs(high_mean - low_mean)})
    return sorted(output, key=lambda item: item["swing"], reverse=True)


def _expected_cost(controls):
    return sum((item["cost"]["low"] + item["cost"]["mode"] + item["cost"]["high"]) / 3 for item in controls)


def _arrays(scenario, controls, mode, trials, seed, overrides, profile_id):
    resolved_id, profile = _profile(scenario, profile_id)
    assumptions, probability = _validated_assumptions(profile, overrides)
    inputs, draws = _sample(assumptions, trials, seed)
    baseline_effects, _ = _effects([], scenario["id"])
    residual_effects, selected = _effects(controls, scenario["id"])
    return resolved_id, assumptions, probability, inputs, draws, selected, _losses(inputs, draws, mode, baseline_effects, probability), _losses(inputs, draws, mode, residual_effects, probability)


def run_simulation(scenario_id="launch-ddos", control_ids=None, mode=None, trials=DEFAULT_TRIALS, seed=DEFAULT_SEED, assumptions=None, assumption_profile_id=None):
    controls = list(dict.fromkeys(control_ids or []))
    trials, seed = int(trials), int(seed)
    if trials < 1_000 or trials > MAX_TRIALS:
        raise ValueError(f"Trials must be between 1,000 and {MAX_TRIALS:,}")
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    mode = mode or scenario.get("analysisBasis", "annual")
    profile_id, model_inputs, probability, inputs, draws, selected, baseline, residual = _arrays(scenario, controls, mode, trials, seed, assumptions, assumption_profile_id)
    maximum = max(float(np.max(baseline)), float(np.max(residual)), 1.0)
    edges = np.linspace(0, maximum * 1.001, 31)
    baseline_metrics, residual_metrics = _metrics(baseline), _metrics(residual)
    reduction = baseline_metrics["mean"] - residual_metrics["mean"]
    cost = _expected_cost(selected)
    return {
        "meta": {"scenarioId": scenario_id, "analysisMode": mode, "naturalAnalysisBasis": scenario.get("analysisBasis"), "trials": trials, "seed": seed, "currency": "USD", "assumptionProfileId": profile_id, "assumptionsSource": "custom" if assumptions is not None else "configured", "secondaryLossProbability": probability},
        "baseline": {"metrics": baseline_metrics, "histogram": _histogram(baseline, edges)},
        "residual": {"metrics": residual_metrics, "histogram": _histogram(residual, edges)},
        "comparison": {"expectedLossReduction": reduction, "reductionPercent": reduction / baseline_metrics["mean"] if baseline_metrics["mean"] else 0.0},
        "controlEconomics": {"selectedControlIds": controls, "estimatedCost": cost, "costBasis": "expected triangular cost", "lossesAvoided": reduction, "netBenefit": reduction - cost, "rosi": (reduction - cost) / cost if cost else None},
        "sensitivity": _sensitivity(inputs, baseline),
        "tornadoSensitivity": _tornado(model_inputs, inputs, draws, mode, probability, scenario_id),
    }


def run_portfolio(control_ids=None, mode=None, trials=DEFAULT_TRIALS, seed=DEFAULT_SEED, assumption_profile_id=None):
    control_ids = list(dict.fromkeys(control_ids if control_ids is not None else [control["id"] for control in CONTROLS]))
    selected = []
    for control_id in control_ids:
        control = get_control(control_id)
        if control is None:
            raise ValueError(f"Unknown control: {control_id}")
        selected.append(control)
    total_baseline, total_residual, summaries = np.zeros(int(trials)), np.zeros(int(trials)), []
    for index, scenario in enumerate(SCENARIOS):
        basis = mode or scenario.get("analysisBasis", "annual")
        applicable = [control["id"] for control in selected if scenario["id"] in control["coverage"]]
        _, _, _, _, _, _, baseline, residual = _arrays(scenario, applicable, basis, int(trials), int(seed) + index * 9_973, None, assumption_profile_id)
        total_baseline += baseline
        total_residual += residual
        baseline_mean, residual_mean = float(np.mean(baseline)), float(np.mean(residual))
        summaries.append({"scenarioId": scenario["id"], "scenarioName": scenario["name"], "analysisBasis": basis, "baselineMean": baseline_mean, "residualMean": residual_mean, "lossesAvoided": baseline_mean - residual_mean, "selectedControlIds": applicable})
    baseline_metrics, residual_metrics = _metrics(total_baseline), _metrics(total_residual)
    maximum = max(float(np.max(total_baseline)), float(np.max(total_residual)), 1.0)
    edges = np.linspace(0, maximum * 1.001, 31)
    reduction = baseline_metrics["mean"] - residual_metrics["mean"]
    cost = _expected_cost(selected)
    return {
        "meta": {"analysisMode": mode or "mixed-natural-basis", "trialsPerScenario": int(trials), "seed": int(seed), "currency": "USD", "scenarioCount": len(summaries), "assumptionProfileId": assumption_profile_id or "evidence-anchored"},
        "portfolio": {"baselineMean": baseline_metrics["mean"], "residualMean": residual_metrics["mean"], "baselineMetrics": baseline_metrics, "residualMetrics": residual_metrics, "baselineHistogram": _histogram(total_baseline, edges), "residualHistogram": _histogram(total_residual, edges), "expectedLossReduction": reduction, "reductionPercent": reduction / baseline_metrics["mean"] if baseline_metrics["mean"] else 0.0},
        "controlEconomics": {"selectedControlIds": control_ids, "estimatedCost": cost, "costBasis": "expected triangular cost", "lossesAvoided": reduction, "netBenefit": reduction - cost, "rosi": (reduction - cost) / cost if cost else None},
        "scenarios": summaries,
    }

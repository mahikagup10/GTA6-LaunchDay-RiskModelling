from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import spearmanr

from backend.data.config import get_control, get_scenario


DEFAULT_TRIALS = 10_000
DEFAULT_SEED = 243
MAX_TRIALS = 100_000
THRESHOLDS = (50_000_000, 100_000_000)


@dataclass(frozen=True)
class SimulationInputs:
    frequency: np.ndarray
    vulnerability: np.ndarray
    primary_loss: np.ndarray
    secondary_loss: np.ndarray


def _triangular(rng, estimate, trials):
    return rng.triangular(estimate["low"], estimate["mode"], estimate["high"], trials)


def _sample_inputs(assumptions, trials, seed):
    rng = np.random.default_rng(seed)
    return SimulationInputs(
        frequency=_triangular(rng, assumptions["threatEventFrequency"], trials),
        vulnerability=_triangular(rng, assumptions["vulnerability"], trials),
        primary_loss=_triangular(rng, assumptions["primaryLoss"], trials),
        secondary_loss=_triangular(rng, assumptions["secondaryLoss"], trials),
    ), rng


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
        for effect_name in effects:
            effects[effect_name] *= control["effects"][effect_name]

    return effects, controls


def _losses(inputs, uniform_draws, mode, effects):
    frequency = np.clip(inputs.frequency * effects["frequencyMultiplier"], 0, None)
    vulnerability = np.clip(inputs.vulnerability * effects["vulnerabilityMultiplier"], 0, 1)
    primary = inputs.primary_loss * effects["primaryLossMultiplier"]
    secondary = inputs.secondary_loss * effects["secondaryLossMultiplier"]

    if mode == "launch-event":
        event_probability = np.clip(frequency, 0, 1)
        successful_events = (uniform_draws[:, 0] < event_probability) & (
            uniform_draws[:, 1] < vulnerability
        )
        event_count = successful_events.astype(int)
    elif mode == "annual":
        rng = np.random.default_rng(int(uniform_draws[0, 0] * 10**9))
        threat_events = rng.poisson(frequency)
        event_count = rng.binomial(threat_events, vulnerability)
    else:
        raise ValueError("Mode must be 'launch-event' or 'annual'")

    return event_count * (primary + secondary)


def _metrics(losses):
    return {
        "mean": float(np.mean(losses)),
        "p50": float(np.percentile(losses, 50)),
        "p90": float(np.percentile(losses, 90)),
        "p95": float(np.percentile(losses, 95)),
        "probabilityAbove50m": float(np.mean(losses > THRESHOLDS[0])),
        "probabilityAbove100m": float(np.mean(losses > THRESHOLDS[1])),
    }


def _histogram(losses, edges):
    counts, _ = np.histogram(losses, bins=edges)
    return {
        "binEdges": [float(value) for value in edges],
        "counts": [int(value) for value in counts],
    }


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
        correlation = 0.0 if np.isnan(result.statistic) else float(result.statistic)
        drivers.append({"name": name, "correlation": correlation})

    return sorted(drivers, key=lambda item: abs(item["correlation"]), reverse=True)[:3]


def run_simulation(
    scenario_id="launch-ddos",
    control_ids=None,
    mode="launch-event",
    trials=DEFAULT_TRIALS,
    seed=DEFAULT_SEED,
):
    control_ids = list(dict.fromkeys(control_ids or []))
    trials = int(trials)
    seed = int(seed)

    if trials < 1_000 or trials > MAX_TRIALS:
        raise ValueError(f"Trials must be between 1,000 and {MAX_TRIALS:,}")

    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    if scenario.get("modelStatus") != "implemented":
        raise ValueError(f"The {scenario['name']} quantitative model is not implemented yet")

    inputs, rng = _sample_inputs(scenario["assumptions"], trials, seed)
    shared_uniform_draws = rng.random((trials, 2))
    baseline_effects, _ = _combined_effects([], scenario_id)
    residual_effects, selected_controls = _combined_effects(control_ids, scenario_id)

    baseline_losses = _losses(inputs, shared_uniform_draws, mode, baseline_effects)
    residual_losses = _losses(inputs, shared_uniform_draws, mode, residual_effects)
    maximum = max(float(np.max(baseline_losses)), float(np.max(residual_losses)), 1.0)
    histogram_edges = np.linspace(0, maximum * 1.001, 31)

    baseline_metrics = _metrics(baseline_losses)
    residual_metrics = _metrics(residual_losses)
    expected_loss_reduction = baseline_metrics["mean"] - residual_metrics["mean"]
    control_cost = sum(control["cost"]["mode"] for control in selected_controls)
    net_benefit = expected_loss_reduction - control_cost

    return {
        "meta": {
            "scenarioId": scenario_id,
            "analysisMode": mode,
            "trials": trials,
            "seed": seed,
            "currency": "USD",
        },
        "baseline": {
            "metrics": baseline_metrics,
            "histogram": _histogram(baseline_losses, histogram_edges),
        },
        "residual": {
            "metrics": residual_metrics,
            "histogram": _histogram(residual_losses, histogram_edges),
        },
        "comparison": {
            "expectedLossReduction": expected_loss_reduction,
            "reductionPercent": (
                expected_loss_reduction / baseline_metrics["mean"]
                if baseline_metrics["mean"]
                else 0.0
            ),
        },
        "controlEconomics": {
            "selectedControlIds": control_ids,
            "estimatedCost": control_cost,
            "lossesAvoided": expected_loss_reduction,
            "netBenefit": net_benefit,
            "rosi": net_benefit / control_cost if control_cost else None,
        },
        "sensitivity": _sensitivity(inputs, baseline_losses),
    }


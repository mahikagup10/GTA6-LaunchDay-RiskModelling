import unittest

import numpy as np

from backend.data.config import (
    ATTACK_PATHS,
    CONTROLS,
    EVIDENCE_CLASSES,
    MODEL_SEED,
    MODEL_TRIALS,
    SCENARIOS,
    SOURCES,
    get_control,
    get_scenario,
)
from backend.model.fair import (
    comparable_cost,
    control_priorities,
    first_year_cost,
    readiness,
    run_portfolio,
    run_simulation,
    scenario_overview,
    simulate_losses,
)


def triangular_mean(item):
    return (item["low"] + item["mode"] + item["high"]) / 3


def analytic_expected_loss(scenario):
    """Independent closed-form expectation, valid because inputs are sampled independently."""
    inputs = scenario["assumptions"]
    model = scenario["model"]
    mean = {key: triangular_mean(value) for key, value in inputs.items()}
    primary = sum(mean[key] for key in model["primaryKeys"])
    if model["interruptionKeys"]:
        interruption = 1.0
        for key in model["interruptionKeys"]:
            interruption *= mean[key]
        primary += interruption
    secondary = mean[model["secondaryProbabilityKey"]] * sum(mean[key] for key in model["secondaryKeys"])
    expected_events = mean[model["frequencyKey"]] * mean[model["successKey"]]
    return expected_events * (primary + secondary)


class SimulationTests(unittest.TestCase):
    def test_defaults_match_plan(self):
        self.assertEqual(MODEL_SEED, 20261124)
        self.assertEqual(MODEL_TRIALS, 10_000)
        result = run_simulation(trials=2_000)
        self.assertEqual(result["meta"]["seed"], 20261124)

    def test_fixed_seed_is_reproducible(self):
        first = run_simulation(trials=2_000, seed=MODEL_SEED)
        second = run_simulation(trials=2_000, seed=MODEL_SEED)
        self.assertEqual(first["baseline"]["metrics"], second["baseline"]["metrics"])
        self.assertEqual(first["baseline"]["histogram"], second["baseline"]["histogram"])
        self.assertEqual(first["sensitivity"], second["sensitivity"])

    def test_time_basis_is_fixed_per_scenario(self):
        self.assertEqual(get_scenario("launch-ddos")["timeBasis"], "launch-event")
        for scenario_id in ("source-code-theft", "insider-leak", "fake-downloads"):
            self.assertEqual(get_scenario(scenario_id)["timeBasis"], "annual")
        ignored = run_simulation("launch-ddos", mode="annual", trials=2_000)
        default = run_simulation("launch-ddos", trials=2_000)
        self.assertEqual(ignored["meta"]["timeBasis"], "launch-event")
        self.assertEqual(ignored["baseline"]["metrics"], default["baseline"]["metrics"])

    def test_recommended_controls_reduce_loss_in_every_scenario(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario["id"]):
                result = run_simulation(scenario["id"], scenario["recommendedControlIds"], trials=5_000)
                self.assertGreater(result["baseline"]["metrics"]["mean"], result["residual"]["metrics"]["mean"])
                self.assertGreater(result["controlEconomics"]["netBenefit"], 0)

    def test_residual_never_exceeds_baseline_in_any_trial(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario["id"]):
                all_controls = [c["id"] for c in CONTROLS if scenario["id"] in c["coverage"]]
                baseline, residual, _ = simulate_losses(scenario["id"], all_controls, trials=5_000)
                self.assertTrue(np.all(residual <= baseline + 1e-6))

    def test_monte_carlo_mean_matches_independent_analytic_expectation(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario["id"]):
                baseline, _, _ = simulate_losses(scenario["id"], trials=200_000)
                expected = analytic_expected_loss(scenario)
                self.assertAlmostEqual(float(np.mean(baseline)) / expected, 1.0, delta=0.04)

    def test_displayed_statistics_match_the_distribution(self):
        baseline, _, _ = simulate_losses("launch-ddos", trials=MODEL_TRIALS)
        result = run_simulation("launch-ddos", trials=MODEL_TRIALS)
        metrics = result["baseline"]["metrics"]
        self.assertAlmostEqual(metrics["mean"], float(np.mean(baseline)), places=2)
        self.assertAlmostEqual(metrics["p95"], float(np.percentile(baseline, 95)), places=2)
        histogram = result["baseline"]["histogram"]
        self.assertEqual(sum(histogram["counts"]) + histogram["zeroCount"], MODEL_TRIALS)
        probabilities = [item["probability"] for item in metrics["exceedance"]]
        self.assertEqual(probabilities, sorted(probabilities, reverse=True))
        self.assertLessEqual(metrics["p50"], metrics["p90"])
        self.assertLessEqual(metrics["p90"], metrics["p95"])

    def test_response_is_compact(self):
        result = run_simulation(trials=2_000)
        self.assertNotIn("losses", result["baseline"])
        self.assertEqual(len(result["baseline"]["histogram"]["counts"]), 30)
        self.assertEqual(len(result["sensitivity"]), 5)
        self.assertEqual(len(result["tornado"]), 5)

    def test_unknown_control_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown control"):
            run_simulation(control_ids=["not-a-control"], trials=2_000)

    def test_unknown_scenario_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown scenario"):
            run_simulation(scenario_id="not-a-scenario", trials=2_000)

    def test_control_outside_scenario_coverage_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not apply"):
            run_simulation(scenario_id="insider-leak", control_ids=["managed-ddos-protection"], trials=2_000)

    def test_cost_time_basis_reconciliation(self):
        resilient = get_control("resilient-architecture")
        self.assertEqual(comparable_cost(resilient, "launch-event"), 3_000_000)
        self.assertEqual(comparable_cost(resilient, "annual"), 1_000_000)
        testing = get_control("launch-resilience-testing")
        self.assertEqual(comparable_cost(testing, "annual"), 500_000)

    def test_portfolio_counts_shared_cost_once(self):
        result = run_portfolio(trials=2_000)
        expected_cost = sum(first_year_cost(control) for control in CONTROLS)
        self.assertEqual(result["controlEconomics"]["estimatedCost"], expected_cost)
        self.assertEqual(len(result["scenarios"]), 4)
        for scenario in result["scenarios"]:
            self.assertGreater(scenario["baselineMean"], scenario["residualMean"])

    def test_priority_scores_and_prerequisite_elevation(self):
        result = control_priorities(trials=2_000)
        self.assertEqual(len(result["controls"]), len(CONTROLS))
        for row in result["controls"]:
            self.assertGreaterEqual(row["priorityScore"], 0)
            self.assertLessEqual(row["priorityScore"], 100)
            self.assertIn(row["priority"], (1, 2, 3))
        testing = next(row for row in result["controls"] if row["controlId"] == "launch-resilience-testing")
        self.assertEqual(testing["priority"], 1)
        self.assertEqual(len(result["heatmap"]["cells"]), len(CONTROLS) * len(SCENARIOS))

    def test_readiness_index(self):
        self.assertEqual(readiness([])["current"]["score"], 40.0)
        self.assertEqual(readiness([c["id"] for c in CONTROLS])["proposed"]["score"], 100.0)
        partial = readiness(["managed-ddos-protection"])
        component = next(c for c in partial["components"] if c["id"] == "ddosProtection")
        self.assertEqual(component["proposedLevel"], 0.5)
        tested = readiness(["managed-ddos-protection", "launch-resilience-testing"])
        component = next(c for c in tested["components"] if c["id"] == "ddosProtection")
        self.assertEqual(component["proposedLevel"], 1.0)

    def test_overview_covers_all_scenarios(self):
        result = scenario_overview(trials=2_000)
        self.assertEqual(len(result["scenarios"]), 4)
        for item in result["scenarios"]:
            self.assertTrue(1 <= item["likelihoodLevel"] <= 5)
            self.assertTrue(1 <= item["impactLevel"] <= 5)


class ConfigIntegrityTests(unittest.TestCase):
    def test_every_input_is_documented(self):
        source_ids = {source["id"] for source in SOURCES}
        for scenario in SCENARIOS:
            for item in scenario["inputs"]:
                with self.subTest(scenario=scenario["id"], key=item["key"]):
                    self.assertLessEqual(item["low"], item["mode"])
                    self.assertLessEqual(item["mode"], item["high"])
                    self.assertIn(item["evidenceType"], EVIDENCE_CLASSES)
                    self.assertTrue(item["sourceIds"])
                    self.assertTrue(set(item["sourceIds"]).issubset(source_ids))
                    for field in ("rationale", "confidence", "unit", "controlRelationship", "owner", "reviewer"):
                        self.assertTrue(item[field])

    def test_every_control_is_documented_and_consistent(self):
        source_ids = {source["id"] for source in SOURCES}
        for control in CONTROLS:
            with self.subTest(control=control["id"]):
                self.assertTrue(control["nist"])
                self.assertTrue(set(control["evidenceIds"]).issubset(source_ids))
                for field in ("problem", "rationale", "owner", "confidence"):
                    self.assertTrue(control[field])
                self.assertLessEqual(control["cost"]["low"], control["cost"]["likely"])
                self.assertLessEqual(control["cost"]["likely"], control["cost"]["high"])
                for scenario_id, effects in control["effects"].items():
                    keys = set(get_scenario(scenario_id)["assumptions"])
                    for factor, effectiveness in effects.items():
                        self.assertIn(factor, keys)
                        self.assertTrue(0 <= effectiveness["low"] <= effectiveness["likely"] <= effectiveness["high"] < 1)

    def test_attack_steps_and_controls_reference_each_other(self):
        for scenario_id, path in ATTACK_PATHS.items():
            step_ids = {step["id"] for step in path}
            for control in CONTROLS:
                for step_id in control["attackSteps"].get(scenario_id, []):
                    self.assertIn(step_id, step_ids)
                    step = next(item for item in path if item["id"] == step_id)
                    self.assertIn(control["id"], step["controlIds"], f"{control['id']} -> {step_id}")
            for step in path:
                for control_id in step["controlIds"]:
                    control = get_control(control_id)
                    self.assertIsNotNone(control)
                    self.assertIn(step["id"], control["attackSteps"].get(scenario_id, []), f"{step['id']} -> {control_id}")

    def test_ddos_chain_has_seven_steps(self):
        self.assertEqual(len(ATTACK_PATHS["launch-ddos"]), 7)


if __name__ == "__main__":
    unittest.main()

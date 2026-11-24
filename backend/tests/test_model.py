import unittest

from backend.data.config import CONTROLS
from backend.model.fair import run_portfolio, run_simulation


class SimulationTests(unittest.TestCase):
    def test_fixed_seed_is_reproducible(self):
        first = run_simulation(trials=2_000, seed=243)
        second = run_simulation(trials=2_000, seed=243)
        self.assertEqual(first["baseline"]["metrics"], second["baseline"]["metrics"])
        self.assertEqual(first["baseline"]["histogram"], second["baseline"]["histogram"])

    def test_controls_reduce_expected_loss(self):
        result = run_simulation(
            control_ids=["cdn-scrubbing", "rate-limiting"],
            trials=5_000,
        )
        baseline = result["baseline"]["metrics"]["mean"]
        residual = result["residual"]["metrics"]["mean"]
        self.assertGreater(baseline, residual)
        self.assertGreater(result["controlEconomics"]["netBenefit"], 0)

    def test_response_is_compact(self):
        result = run_simulation(trials=2_000)
        self.assertNotIn("losses", result["baseline"])
        self.assertEqual(len(result["baseline"]["histogram"]["counts"]), 30)
        self.assertEqual(len(result["sensitivity"]), 3)
        self.assertIn("p99", result["baseline"]["metrics"])
        self.assertEqual(len(result["tornadoSensitivity"]), 4)

    def test_unknown_control_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown control"):
            run_simulation(control_ids=["not-a-control"], trials=2_000)

    def test_custom_assumptions_change_results_and_are_reproducible(self):
        assumptions = {
            "threatEventFrequency": {"low": 0.8, "mode": 1.0, "high": 1.4},
            "vulnerability": {"low": 0.5, "mode": 0.7, "high": 0.9},
            "primaryLoss": {"low": 30_000_000, "mode": 55_000_000, "high": 90_000_000},
            "secondaryLoss": {"low": 15_000_000, "mode": 35_000_000, "high": 75_000_000},
        }
        configured = run_simulation(trials=2_000, seed=243)
        first = run_simulation(trials=2_000, seed=243, assumptions=assumptions)
        second = run_simulation(trials=2_000, seed=243, assumptions=assumptions)

        self.assertEqual(first["meta"]["assumptionsSource"], "custom")
        self.assertEqual(first["baseline"]["metrics"], second["baseline"]["metrics"])
        self.assertGreater(
            first["baseline"]["metrics"]["mean"],
            configured["baseline"]["metrics"]["mean"],
        )

    def test_invalid_custom_assumption_order_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "low <= mode <= high"):
            run_simulation(
                trials=2_000,
                assumptions={
                    "vulnerability": {"low": 0.6, "mode": 0.4, "high": 0.8},
                },
            )

    def test_vulnerability_above_one_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            run_simulation(
                trials=2_000,
                assumptions={
                    "vulnerability": {"low": 0.2, "mode": 0.8, "high": 1.2},
                },
            )

    def test_all_scenarios_are_reproducible_and_controls_reduce_loss(self):
        scenario_controls = {
            "launch-ddos": ["cdn-scrubbing", "rate-limiting"],
            "source-code-theft": ["repository-hardening", "least-privilege"],
            "insider-leak": ["least-privilege", "dlp-monitoring"],
            "fake-downloads": ["brand-monitoring", "phishing-resistant-mfa"],
        }

        for scenario_id, control_ids in scenario_controls.items():
            with self.subTest(scenario_id=scenario_id):
                first = run_simulation(
                    scenario_id=scenario_id,
                    control_ids=control_ids,
                    trials=3_000,
                    seed=243,
                )
                second = run_simulation(
                    scenario_id=scenario_id,
                    control_ids=control_ids,
                    trials=3_000,
                    seed=243,
                )
                self.assertEqual(first["baseline"]["metrics"], second["baseline"]["metrics"])
                self.assertGreater(
                    first["baseline"]["metrics"]["mean"],
                    first["residual"]["metrics"]["mean"],
                )

    def test_control_outside_scenario_coverage_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not apply"):
            run_simulation(
                scenario_id="insider-leak",
                control_ids=["cdn-scrubbing"],
                trials=2_000,
            )

    def test_all_control_portfolio_counts_shared_cost_once(self):
        result = run_portfolio(trials=2_000, seed=243)
        expected_cost = sum(
            (control["cost"]["low"] + control["cost"]["mode"] + control["cost"]["high"]) / 3
            for control in CONTROLS
        )

        self.assertEqual(result["controlEconomics"]["estimatedCost"], expected_cost)
        self.assertEqual(len(result["scenarios"]), 4)
        self.assertGreater(
            result["portfolio"]["baselineMean"],
            result["portfolio"]["residualMean"],
        )
        for scenario in result["scenarios"]:
            self.assertGreater(scenario["baselineMean"], scenario["residualMean"])

    def test_secondary_loss_probability_changes_results(self):
        without_secondary = run_simulation(trials=4_000, assumptions={"secondaryLossProbability": 0})
        always_secondary = run_simulation(trials=4_000, assumptions={"secondaryLossProbability": 1})
        self.assertGreater(always_secondary["baseline"]["metrics"]["mean"], without_secondary["baseline"]["metrics"]["mean"])

    def test_profiles_are_available_and_distinct(self):
        evidence = run_simulation(trials=3_000, assumption_profile_id="evidence-anchored")
        original = run_simulation(trials=3_000, assumption_profile_id="original-team")
        self.assertNotEqual(evidence["baseline"]["metrics"]["mean"], original["baseline"]["metrics"]["mean"])

    def test_portfolio_uses_natural_analysis_basis(self):
        result = run_portfolio(control_ids=[], trials=2_000)
        bases = {item["scenarioId"]: item["analysisBasis"] for item in result["scenarios"]}
        self.assertEqual(bases["launch-ddos"], "launch-event")
        self.assertTrue(all(bases[key] == "annual" for key in bases if key != "launch-ddos"))
        self.assertIn("p99", result["portfolio"]["baselineMetrics"])


if __name__ == "__main__":
    unittest.main()

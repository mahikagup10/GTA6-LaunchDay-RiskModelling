import unittest

from backend.data.config import CONTROLS
from backend.model.fair import expected_cost as expected_cost_fn, run_control_priorities, run_portfolio, run_simulation


class SimulationTests(unittest.TestCase):
    def test_fixed_seed_is_reproducible(self):
        first = run_simulation(trials=2_000, seed=20261124)
        second = run_simulation(trials=2_000, seed=20261124)
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

    def test_unknown_control_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown control"):
            run_simulation(control_ids=["not-a-control"], trials=2_000)

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
                    seed=20261124,
                )
                second = run_simulation(
                    scenario_id=scenario_id,
                    control_ids=control_ids,
                    trials=3_000,
                    seed=20261124,
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
        result = run_portfolio(trials=2_000, seed=20261124)
        expected_cost = sum(expected_cost_fn(control) for control in CONTROLS)

        self.assertAlmostEqual(result["controlEconomics"]["estimatedCost"], expected_cost, places=2)
        self.assertEqual(len(result["scenarios"]), 4)
        self.assertGreater(
            result["portfolio"]["baselineMean"],
            result["portfolio"]["residualMean"],
        )
        for scenario in result["scenarios"]:
            self.assertGreater(scenario["baselineMean"], scenario["residualMean"])

    def test_matches_workbook_at_plan_seed(self):
        """GTA6_FAIR_Monte_Carlo.xlsx (seed 20261124, 10,000 trials) is the reference."""
        ddos = run_simulation(
            scenario_id="launch-ddos",
            control_ids=["cdn-scrubbing", "rate-limiting", "incident-drills"],
            trials=10_000,
            seed=20261124,
        )
        self.assertAlmostEqual(ddos["baseline"]["metrics"]["mean"] / 1e6, 6.0851, places=3)
        self.assertAlmostEqual(ddos["baseline"]["metrics"]["p95"] / 1e6, 50.8916, places=3)
        self.assertAlmostEqual(ddos["residual"]["metrics"]["mean"] / 1e6, 1.1302, places=3)
        port = run_portfolio(trials=10_000, seed=20261124)
        self.assertAlmostEqual(port["portfolio"]["baselineMean"] / 1e6, 20.062, places=2)
        self.assertAlmostEqual(port["portfolio"]["residualMean"] / 1e6, 2.312, places=2)
        self.assertAlmostEqual(port["controlEconomics"]["rosi"], 3.458, places=2)

    def test_scenario_result_does_not_depend_on_run_order(self):
        alone = run_simulation(scenario_id="insider-leak", trials=3_000, seed=7)
        in_portfolio = next(s for s in run_portfolio(control_ids=[], trials=3_000, seed=7)["scenarios"] if s["scenarioId"] == "insider-leak")
        self.assertAlmostEqual(alone["baseline"]["metrics"]["mean"], in_portfolio["baselineMean"], places=4)

    def test_priority_scores_and_tiers(self):
        rows = run_control_priorities()["controls"]
        self.assertEqual(rows[0]["controlId"], "incident-drills")
        self.assertEqual(rows[0]["tier"], "Priority 1")
        self.assertEqual(len(rows), 9)

    def test_every_assumption_has_evidence_class_and_source(self):
        from backend.data.config import SCENARIOS
        allowed = {"public-fact", "derived-value", "team-estimate", "model-assumption"}
        for scenario in SCENARIOS:
            self.assertGreater(scenario["probabilitySecondary"], 0)
            for a in scenario["assumptions"].values():
                self.assertIn(a["evidenceType"], allowed)
                self.assertTrue(a["evidenceRef"].startswith("I"))


if __name__ == "__main__":
    unittest.main()

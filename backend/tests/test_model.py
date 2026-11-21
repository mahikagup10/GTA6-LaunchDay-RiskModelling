import unittest

from backend.model.fair import run_simulation


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


if __name__ == "__main__":
    unittest.main()

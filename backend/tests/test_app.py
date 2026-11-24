import unittest

from backend.app import app


class AppRoutingTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_react_routes_serve_the_app_shell(self):
        for path in ("/", "/attack-paths", "/risk-simulator", "/control-planner"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'<div id="root"></div>', response.data)
                response.close()

    def test_portfolio_endpoint_returns_four_scenarios(self):
        response = self.client.post(
            "/api/portfolio",
            json={"controlIds": [], "trials": 2_000, "seed": 243},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["scenarios"]), 4)

    def test_config_exposes_methodology_and_input_provenance(self):
        payload = self.client.get("/api/config").get_json()
        self.assertIn("methodology", payload)
        for scenario in payload["scenarios"]:
            self.assertEqual(scenario["defaultAssumptionProfileId"], "evidence-anchored")
            self.assertIn("original-team", scenario["assumptionProfiles"])
            for profile in scenario["assumptionProfiles"].values():
                self.assertIn("secondaryLossProbability", profile)
                for assumption in profile["assumptions"].values():
                    self.assertTrue(assumption["sources"])
                    self.assertTrue(assumption["sources"][0]["url"].startswith("https://"))
                    self.assertTrue(assumption["rationale"])
                    self.assertTrue(assumption["confidence"])

    def test_readiness_inputs_cover_all_four_dimensions(self):
        payload = self.client.get("/api/config").get_json()
        dimensions = {"prevent", "detect", "respond", "recover"}
        for scenario in payload["scenarios"]:
            self.assertEqual(set(scenario["readinessProfile"]), dimensions)
        for control in payload["controls"]:
            self.assertEqual(set(control["readinessImpact"]), dimensions)

    def test_control_effects_expose_estimate_provenance(self):
        payload = self.client.get("/api/config").get_json()
        for control in payload["controls"]:
            evidence = control["effectEvidence"]
            self.assertEqual(evidence["evidenceType"], "team-estimate")
            self.assertTrue(evidence["rationale"])
            self.assertTrue(evidence["confidence"])
            self.assertTrue(evidence["source"]["url"].startswith("https://"))
            self.assertTrue(evidence["source"]["accessDate"])
            self.assertIn("team-developed", evidence["source"]["scope"])

    def test_every_scenario_has_a_complete_attack_path(self):
        payload = self.client.get("/api/config").get_json()
        scenario_ids = {scenario["id"] for scenario in payload["scenarios"]}
        control_ids = {control["id"] for control in payload["controls"]}
        source_ids = {source["id"] for source in payload["sources"]}

        self.assertEqual(set(payload["attackChains"]), scenario_ids)
        for scenario_id, stages in payload["attackChains"].items():
            with self.subTest(scenario_id=scenario_id):
                self.assertEqual(len(stages), 4)
                self.assertEqual([stage["number"] for stage in stages], ["01", "02", "03", "04"])
                for stage in stages:
                    self.assertTrue(set(stage["controlIds"]).issubset(control_ids))
                    self.assertTrue(set(stage["sourceIds"]).issubset(source_ids))
                    self.assertTrue(stage["attackerAction"])
                    self.assertTrue(stage["businessEffect"])

    def test_ddos_has_deep_dive_content_without_expanding_other_paths(self):
        payload = self.client.get("/api/config").get_json()
        self.assertEqual(set(payload["attackPathDetails"]), {"launch-ddos"})
        details = payload["attackPathDetails"]["launch-ddos"]
        self.assertEqual(len(details["technicalFlow"]), 5)
        self.assertEqual(len(details["responseTimeline"]), 4)
        for stage in payload["attackChains"]["launch-ddos"]:
            self.assertGreaterEqual(len(stage["substeps"]), 3)
            self.assertGreaterEqual(len(stage["technicalIndicators"]), 4)
            self.assertTrue(stage["fairEffects"])
            self.assertTrue(stage["executiveDecision"])
        for scenario_id in ("source-code-theft", "insider-leak", "fake-downloads"):
            for stage in payload["attackChains"][scenario_id]:
                self.assertNotIn("substeps", stage)


if __name__ == "__main__":
    unittest.main()

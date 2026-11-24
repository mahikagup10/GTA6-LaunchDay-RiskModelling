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
            json={"controlIds": [], "trials": 2_000, "seed": 20261124},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["scenarios"]), 4)

    def test_config_exposes_methodology_and_input_provenance(self):
        payload = self.client.get("/api/config").get_json()
        self.assertIn("methodology", payload)
        for scenario in payload["scenarios"]:
            for assumption in scenario["assumptions"].values():
                self.assertTrue(assumption["source"]["url"].startswith("https://"))
                self.assertTrue(assumption["source"]["accessDate"])
                self.assertTrue(assumption["rationale"])
                self.assertTrue(assumption["confidence"])

    def test_readiness_inputs_cover_all_four_dimensions(self):
        payload = self.client.get("/api/config").get_json()
        dimensions = {"prevent", "detect", "respond", "recover"}
        for scenario in payload["scenarios"]:
            self.assertEqual(set(scenario["readinessProfile"]), dimensions)
        for control in payload["controls"]:
            self.assertEqual(set(control["readinessImpact"]), dimensions)


if __name__ == "__main__":
    unittest.main()

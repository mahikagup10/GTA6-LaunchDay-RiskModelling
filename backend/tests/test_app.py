import unittest

from backend.app import FRONTEND_DIST, app


class AppRoutingTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    @unittest.skipUnless(FRONTEND_DIST.exists(), "Run `npm run build` in frontend/ to test the production shell")
    def test_react_routes_serve_the_app_shell(self):
        for path in ("/", "/attack-paths", "/risk-simulator", "/control-planner"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'<div id="root"></div>', response.data)
                response.close()

    def test_unknown_api_route_returns_404(self):
        response = self.client.get("/api/not-a-route")
        self.assertEqual(response.status_code, 404)

    def test_simulate_endpoint(self):
        response = self.client.post(
            "/api/simulate",
            json={"scenarioId": "launch-ddos", "controlIds": ["managed-ddos-protection"], "trials": 2_000},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["meta"]["timeBasis"], "launch-event")
        self.assertIn("readiness", payload)
        self.assertIn("tornado", payload)

    def test_simulate_rejects_bad_input(self):
        response = self.client.post("/api/simulate", json={"scenarioId": "nope", "trials": 2_000})
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/simulate", json={"trials": 10})
        self.assertEqual(response.status_code, 400)

    def test_portfolio_endpoint_returns_four_scenarios(self):
        response = self.client.post("/api/portfolio", json={"controlIds": [], "trials": 2_000})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["scenarios"]), 4)

    def test_overview_and_priority_endpoints(self):
        overview = self.client.get("/api/overview?trials=2000")
        self.assertEqual(overview.status_code, 200)
        self.assertEqual(len(overview.get_json()["scenarios"]), 4)
        priority = self.client.get("/api/controls/priority?trials=2000")
        self.assertEqual(priority.status_code, 200)
        self.assertIn("heatmap", priority.get_json())

    def test_config_exposes_methodology_and_input_provenance(self):
        payload = self.client.get("/api/config").get_json()
        self.assertIn("methodology", payload)
        sources = {source["id"]: source for source in payload["sources"]}
        for source in sources.values():
            self.assertTrue(source["url"].startswith("https://"))
            self.assertTrue(source["accessDate"])
        for scenario in payload["scenarios"]:
            self.assertIn(scenario["timeBasis"], ("launch-event", "annual"))
            for item in scenario["inputs"]:
                self.assertTrue(item["rationale"])
                self.assertTrue(item["confidence"])
                for source_id in item["sourceIds"]:
                    self.assertIn(source_id, sources)

    def test_readiness_model_weights_sum_to_100(self):
        payload = self.client.get("/api/config").get_json()
        self.assertEqual(sum(c["weight"] for c in payload["readinessModel"]["components"]), 100)


if __name__ == "__main__":
    unittest.main()

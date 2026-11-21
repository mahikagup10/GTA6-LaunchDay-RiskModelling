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


if __name__ == "__main__":
    unittest.main()

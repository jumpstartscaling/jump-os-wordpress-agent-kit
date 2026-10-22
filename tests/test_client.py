import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "client"))
import tenantctl  # noqa: E402


class ClientTests(unittest.TestCase):
    def test_host_gateway_routes_are_generic(self):
        self.assertEqual(tenantctl.request_details("host-gateway", "status"), ("GET", "/v1/status"))
        self.assertEqual(
            tenantctl.request_details("host-gateway", "run", "plugin-elementor-update"),
            ("POST", "/v1/operations/plugin-elementor-update"),
        )

    def test_wordpress_bridge_routes_are_generic(self):
        self.assertEqual(tenantctl.request_details("wordpress-bridge", "capabilities"), ("GET", "/capabilities"))
        self.assertEqual(
            tenantctl.request_details("wordpress-bridge", "run", "plugin-elementor-activate"),
            ("POST", "/operations/plugin-elementor-activate"),
        )

    def test_client_rejects_unbounded_operation_names(self):
        with self.assertRaises(ValueError):
            tenantctl.request_details("host-gateway", "run", "shell;whoami")

    def test_v1_host_gateway_uses_only_known_legacy_operation_paths(self):
        self.assertEqual(
            tenantctl.request_details("host-gateway-v1", "run", "plugin-elementor-update"),
            ("POST", "/v1/operations/elementor/update"),
        )
        with self.assertRaises(ValueError):
            tenantctl.request_details("host-gateway-v1", "run", "plugin-unknown-update")


if __name__ == "__main__":
    unittest.main()

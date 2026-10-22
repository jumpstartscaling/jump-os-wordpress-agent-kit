import hashlib
import http.client
import json
import socket
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gateway"))
import tenant_gateway  # noqa: E402


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.viewer_token = "viewer-secret"
        self.operator_token = "operator-secret"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        policy = {
            "tenant_id": "test-tenant",
            "host": "127.0.0.1",
            "port": port,
            "audit_log": str(root / "audit.jsonl"),
            "token_hashes": {
                "viewer": [hashlib.sha256(self.viewer_token.encode()).hexdigest()],
                "operator": [hashlib.sha256(self.operator_token.encode()).hexdigest()],
            },
            "status": {
                "role": "viewer",
                "command": ["/usr/bin/sudo", sys.executable, "-c", "print('{\\\"state\\\":\\\"ok\\\"}')"],
            },
            "operations": {
                "plugin-elementor-update": {
                    "role": "operator",
                    "command": ["/usr/bin/sudo", sys.executable, "-c", "print('{\\\"version\\\":\\\"test\\\"}')"],
                },
                "plugin-elementor-activate": {
                    "role": "operator",
                    "command": ["/usr/bin/sudo", sys.executable, "-c", "print('{\\\"active\\\":true}')"],
                },
            },
        }
        config_path = root / "policy.json"
        config_path.write_text(json.dumps(policy), encoding="utf-8")
        self.config = tenant_gateway.GatewayConfig.load(config_path)
        # Production policy validation requires sudo wrappers. Unit tests then
        # replace only the already-validated argv with harmless local commands.
        object.__setattr__(self.config, "status", tenant_gateway.FixedOperation("viewer", self.config.status.command[1:]))
        object.__setattr__(
            self.config,
            "operations",
            {
                operation_id: tenant_gateway.FixedOperation(operation.role, operation.command[1:])
                for operation_id, operation in self.config.operations.items()
            },
        )
        self.server = tenant_gateway.build_server(self.config)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, method, path, token=None, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        payload = json.loads(response.read())
        connection.close()
        return response.status, payload

    def test_health_is_public_and_status_requires_a_token(self):
        self.assertEqual(self.request("GET", "/healthz")[0], 200)
        self.assertEqual(self.request("GET", "/v1/status")[0], 401)

    def test_viewer_can_read_status_but_cannot_operate(self):
        status, payload = self.request("GET", "/v1/status", self.viewer_token)
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(self.request("POST", "/v1/operations/plugin-elementor-update", self.viewer_token)[0], 401)

    def test_operator_can_run_only_named_argument_free_operation(self):
        status, payload = self.request("POST", "/v1/operations/plugin-elementor-update", self.operator_token)
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "plugin-elementor-update")
        self.assertEqual(self.request("POST", "/v1/operations/plugin-elementor-update", self.operator_token, body="{\"plugin\":\"other\"}")[0], 400)
        self.assertEqual(self.request("POST", "/v1/operations/shell", self.operator_token)[0], 404)

    def test_capabilities_are_policy_defined_not_elementor_hard_coded(self):
        status, payload = self.request("GET", "/v1/capabilities", self.viewer_token)
        self.assertEqual(status, 200)
        self.assertEqual([item["id"] for item in payload["operations"]], ["plugin-elementor-activate", "plugin-elementor-update"])


if __name__ == "__main__":
    unittest.main()

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
            "actions": {
                "status": [sys.executable, "-c", "print('{\\\"state\\\":\\\"ok\\\"}')"],
                "elementor_update": [sys.executable, "-c", "print('{\\\"version\\\":\\\"test\\\"}')"],
                "elementor_activate": [sys.executable, "-c", "print('{\\\"active\\\":true}')"],
            },
        }
        # Test policies use Python commands rather than production sudo wrappers.
        config_path = root / "policy.json"
        config_path.write_text(json.dumps(policy), encoding="utf-8")
        raw = json.loads(config_path.read_text())
        raw["actions"] = {key: ["/usr/bin/sudo", *value] for key, value in raw["actions"].items()}
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        self.config = tenant_gateway.GatewayConfig.load(config_path)
        # Production policy validation requires sudo wrappers. Unit tests then
        # replace only the already-validated argv with harmless local commands.
        object.__setattr__(self.config, "actions", {key: value[1:] for key, value in self.config.actions.items()})
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
        self.assertEqual(self.request("POST", "/v1/operations/elementor/update", self.viewer_token)[0], 401)

    def test_operator_can_run_only_named_argument_free_operation(self):
        status, payload = self.request("POST", "/v1/operations/elementor/update", self.operator_token)
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(self.request("POST", "/v1/operations/elementor/update", self.operator_token, body="{\"plugin\":\"other\"}")[0], 400)
        self.assertEqual(self.request("POST", "/v1/operations/shell", self.operator_token)[0], 404)


if __name__ == "__main__":
    unittest.main()

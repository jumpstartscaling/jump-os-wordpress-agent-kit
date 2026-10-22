import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RecipientPackTests(unittest.TestCase):
    def test_pack_contains_private_environment_and_agent_boundary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            gateway_token = root / "gateway.token"
            dashboard_password = root / "dashboard-password.token"
            app_password = root / "app-password.token"
            output = root / "recipient.zip"
            gateway_token.write_text("gateway-token-test-only\n", encoding="utf-8")
            dashboard_password.write_text("dashboard-password-test-only\n", encoding="utf-8")
            app_password.write_text("app-password-test-only\n", encoding="utf-8")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_recipient_pack.py"),
                    "--output", str(output),
                    "--tenant-label", "Test Tenant",
                    "--gateway-endpoint", "https://tenant.example/__tenant-gateway",
                    "--gateway-token-file", str(gateway_token),
                    "--wordpress-url", "https://tenant.example",
                    "--wordpress-username", "test-editor",
                    "--wordpress-dashboard-password-file", str(dashboard_password),
                    "--wordpress-application-password-file", str(app_password),
                ],
                check=True,
                cwd=ROOT,
            )
            with zipfile.ZipFile(output) as archive:
                names = archive.namelist()
                self.assertIn("tenant-access-pack/AGENTS.md", names)
                self.assertIn("tenant-access-pack/tenantctl.py", names)
                env = archive.read("tenant-access-pack/.env").decode("utf-8")
                self.assertIn("TENANT_GATEWAY_TOKEN=gateway-token-test-only", env)
                self.assertIn("WORDPRESS_DASHBOARD_PASSWORD=dashboard-password-test-only", env)
                self.assertIn("WORDPRESS_APPLICATION_PASSWORD=app-password-test-only", env)


if __name__ == "__main__":
    unittest.main()

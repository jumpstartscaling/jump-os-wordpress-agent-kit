import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WordPressBridgePackageTests(unittest.TestCase):
    def test_builds_a_standard_secret_free_wordpress_plugin_zip(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = Path(temporary) / "bridge.zip"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_wordpress_bridge_zip.py"), "--output", str(archive_path)],
                check=True,
                cwd=ROOT,
            )
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
                plugin_file = "jump-os-wordpress-agent-bridge/jump-os-wordpress-agent-bridge.php"
                self.assertIn(plugin_file, names)
                self.assertNotIn(".env", names)
                source = archive.read(plugin_file).decode("utf-8")
                self.assertIn("Plugin Name: Jump OS WordPress Agent Bridge", source)
                self.assertIn("Version: 0.3.1", source)
                self.assertIn("License: MIT", source)


if __name__ == "__main__":
    unittest.main()

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleasePackageTests(unittest.TestCase):
    def test_release_assets_are_secret_free_and_checksums_match(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_release_package.py"), "--version", "0.3.3", "--output", str(output)],
                check=True,
                cwd=ROOT,
            )
            manifest = json.loads((output / "release-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["version"], "0.3.3")
            self.assertEqual(len(manifest["artifacts"]), 2)
            for artifact in manifest["artifacts"]:
                path = output / artifact["name"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), artifact["sha256"])
                with zipfile.ZipFile(path) as archive:
                    self.assertNotIn(".env", [Path(name).name for name in archive.namelist()])
                    if artifact["name"].startswith("jump-os-agent-workspace-template"):
                        self.assertIn("docs/PAGE-BUILDERS-PLUGINS-THEMES.md", archive.namelist())
            self.assertIn("release-manifest.json", (output / "SHA256SUMS.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

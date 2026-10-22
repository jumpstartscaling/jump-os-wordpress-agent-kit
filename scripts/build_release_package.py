#!/usr/bin/env python3
"""Build secret-free release assets and a checksum manifest for one version."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
PLUGIN = ROOT / "wordpress-plugin" / "jump-os-wordpress-agent-bridge"
WORKSPACE_FILES = (
    ROOT / "client" / "tenantctl.py",
    ROOT / "templates" / "recipient-pack" / "AGENTS.md",
    ROOT / "templates" / "recipient-pack" / "START-HERE.md",
    ROOT / "docs" / "AGENT-RUNTIME-COMPATIBILITY.md",
    ROOT / "docs" / "PAGE-BUILDERS-PLUGINS-THEMES.md",
)
WORKSPACE_DIRS = (
    ROOT / "templates" / "agent-workspace",
    ROOT / "docs" / "agents",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_zip(destination: Path, roots: tuple[Path, ...], base: Path) -> None:
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for root in roots:
            sources = (root,) if root.is_file() else sorted(path for path in root.rglob("*") if path.is_file())
            for source in sources:
                relative = source.relative_to(base)
                if relative.name == ".env" or "private" in relative.parts:
                    raise ValueError(f"refusing private release input: {relative}")
                archive.write(source, relative.as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="semantic version without a leading v")
    parser.add_argument("--output", type=Path, required=True, help="new empty output directory")
    args = parser.parse_args()
    if not VERSION.fullmatch(args.version):
        parser.error("version must be a semantic version without a leading v")
    project_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if args.version != project_version:
        parser.error(f"requested version {args.version} does not match VERSION ({project_version})")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.mkdir(parents=True)

    plugin_zip = args.output / f"jump-os-wordpress-agent-bridge-{args.version}.zip"
    workspace_zip = args.output / f"jump-os-agent-workspace-template-{args.version}.zip"
    write_zip(plugin_zip, (PLUGIN,), PLUGIN.parent)
    write_zip(workspace_zip, WORKSPACE_FILES + WORKSPACE_DIRS, ROOT)
    artifacts = [plugin_zip, workspace_zip]
    manifest = {
        "schema_version": 1,
        "project": "jump-os-wordpress-agent-kit",
        "version": args.version,
        "artifacts": [
            {"name": artifact.name, "sha256": sha256(artifact), "bytes": artifact.stat().st_size}
            for artifact in artifacts
        ],
        "secret_policy": "Release artifacts contain no tenant URLs, credentials, private policies, or generated recipient packages.",
    }
    manifest_path = args.output / "release-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksums = args.output / "SHA256SUMS.txt"
    checksums.write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in [*artifacts, manifest_path]),
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

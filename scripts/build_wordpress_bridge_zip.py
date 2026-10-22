#!/usr/bin/env python3
"""Create an installable WordPress ZIP without including any tenant secret."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "wordpress-plugin" / "jump-os-wordpress-agent-bridge"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(PLUGIN.rglob("*")):
            if source.is_file() and "__pycache__" not in source.parts:
                archive.write(source, source.relative_to(PLUGIN.parent))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

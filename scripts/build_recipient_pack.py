#!/usr/bin/env python3
"""Build a private, shareable tenant operator package from public templates."""

from __future__ import annotations

import argparse
import shlex
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_secret(path: Path | None) -> str:
    if path is None:
        return ""
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise ValueError(f"secret file is empty: {path}")
    return value


def env_assignment(name: str, value: str) -> str:
    """Return a POSIX-shell-safe assignment for a private handoff .env file."""
    return f"{name}={shlex.quote(value)}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="private ZIP output path")
    parser.add_argument("--tenant-label", required=True)
    parser.add_argument("--gateway-endpoint", required=True)
    parser.add_argument("--access-mode", choices=("host-gateway", "host-gateway-v1", "wordpress-bridge"), default="host-gateway")
    parser.add_argument("--gateway-token-file", type=Path, required=True)
    parser.add_argument("--wordpress-url", required=True)
    parser.add_argument("--wordpress-username", required=True)
    parser.add_argument("--wordpress-dashboard-password-file", type=Path, required=True)
    parser.add_argument("--wordpress-application-password-file", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        package = Path(temporary) / "tenant-access-pack"
        package.mkdir()
        shutil.copy2(ROOT / "client" / "tenantctl.py", package / "tenantctl.py")
        shutil.copy2(ROOT / "templates" / "recipient-pack" / "AGENTS.md", package / "AGENTS.md")
        shutil.copy2(ROOT / "templates" / "recipient-pack" / "START-HERE.md", package / "START-HERE.md")
        shutil.copy2(ROOT / "docs" / "PAGE-BUILDERS-PLUGINS-THEMES.md", package / "PAGE-BUILDERS-PLUGINS-THEMES.md")
        shutil.copytree(ROOT / "templates" / "agent-workspace", package, dirs_exist_ok=True)
        shutil.copytree(ROOT / "docs" / "agents", package / "agent-guides")
        environment = {
            "TENANT_LABEL": args.tenant_label,
            "TENANT_GATEWAY_API_STYLE": args.access_mode,
            "TENANT_GATEWAY_ENDPOINT": args.gateway_endpoint.rstrip("/"),
            "TENANT_GATEWAY_TOKEN": read_secret(args.gateway_token_file),
            "WORDPRESS_URL": args.wordpress_url.rstrip("/"),
            "WORDPRESS_USERNAME": args.wordpress_username,
            "WORDPRESS_DASHBOARD_PASSWORD": read_secret(args.wordpress_dashboard_password_file),
            "WORDPRESS_APPLICATION_PASSWORD": read_secret(args.wordpress_application_password_file),
        }
        (package / ".env").write_text(
            "# PRIVATE: revoke and replace these credentials if this package is misdirected.\n"
            + "".join(env_assignment(name, value) for name, value in environment.items()),
            encoding="utf-8",
        )
        (package / "README-PRIVATE.txt").write_text(
            "This ZIP contains live tenant-scoped credentials. Store it only in a Drive folder shared with the intended recipient. "
            "Do not commit, email broadly, or upload it to an issue. Ask the platform owner to revoke and reissue both credentials if it is exposed.\n",
            encoding="utf-8",
        )
        archive_base = args.output.with_suffix("")
        shutil.make_archive(str(archive_base), "zip", temporary, package.name)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

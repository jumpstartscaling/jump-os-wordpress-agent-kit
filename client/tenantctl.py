#!/usr/bin/env python3
"""No-dependency client for a tenant-scoped host gateway or WordPress bridge."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request


OPERATION_ID = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
API_STYLES = {
    "host-gateway": {"status": "/v1/status", "capabilities": "/v1/capabilities", "operations": "/v1/operations/"},
    "wordpress-bridge": {"status": "/status", "capabilities": "/capabilities", "operations": "/operations/"},
}


def request_details(style: str, command: str, operation: str | None = None) -> tuple[str, str]:
    if style not in API_STYLES:
        raise ValueError(f"unsupported API style: {style}")
    if command in {"status", "capabilities"}:
        return "GET", API_STYLES[style][command]
    if command == "run" and operation and OPERATION_ID.fullmatch(operation):
        return "POST", API_STYLES[style]["operations"] + operation
    raise ValueError("operation must be a lowercase kebab-case capability identifier")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "capabilities", "run"))
    parser.add_argument("operation", nargs="?", help="required with the run command")
    parser.add_argument("--endpoint", default=os.environ.get("TENANT_GATEWAY_ENDPOINT"))
    parser.add_argument("--token", default=os.environ.get("TENANT_GATEWAY_TOKEN"))
    parser.add_argument("--api-style", choices=tuple(API_STYLES), default=os.environ.get("TENANT_GATEWAY_API_STYLE", "host-gateway"))
    args = parser.parse_args()
    if not args.endpoint or not args.token:
        parser.error("set TENANT_GATEWAY_ENDPOINT and TENANT_GATEWAY_TOKEN, preferably in your secret manager")
    try:
        method, path = request_details(args.api_style, args.command, args.operation)
    except ValueError as exc:
        parser.error(str(exc))
    request = urllib.request.Request(
        args.endpoint.rstrip("/") + path,
        method=method,
        data=b"{}" if method == "POST" else None,
        headers={
            "Authorization": f"Bearer {args.token}",
            "Accept": "application/json",
            "User-Agent": "JumpWordPressAgentKit/0.2 (+https://github.com/jumpstartscaling/jump-os-wordpress-agent-kit)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=310) as response:
            print(json.dumps(json.load(response), indent=2, sort_keys=True))
            return 0
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"gateway returned HTTP {exc.code}: {detail}", file=sys.stderr)
        return 2
    except urllib.error.URLError as exc:
        print(f"cannot reach tenant gateway: {exc.reason}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

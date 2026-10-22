#!/usr/bin/env python3
"""No-dependency client for a tenant-scoped maintenance gateway."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "capabilities", "elementor-update", "elementor-activate"))
    parser.add_argument("--endpoint", default=os.environ.get("TENANT_GATEWAY_ENDPOINT"))
    parser.add_argument("--token", default=os.environ.get("TENANT_GATEWAY_TOKEN"))
    args = parser.parse_args()
    if not args.endpoint or not args.token:
        parser.error("set TENANT_GATEWAY_ENDPOINT and TENANT_GATEWAY_TOKEN, preferably in your secret manager")
    paths = {
        "status": ("GET", "/v1/status"),
        "capabilities": ("GET", "/v1/capabilities"),
        "elementor-update": ("POST", "/v1/operations/elementor/update"),
        "elementor-activate": ("POST", "/v1/operations/elementor/activate"),
    }
    method, path = paths[args.command]
    request = urllib.request.Request(
        args.endpoint.rstrip("/") + path,
        method=method,
        data=b"{}" if method == "POST" else None,
        headers={
            "Authorization": f"Bearer {args.token}",
            "Accept": "application/json",
            "User-Agent": "JumpTenantGateway/0.1 (+https://github.com/jumpstartscaling/jump-os-tenant-gateway)",
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

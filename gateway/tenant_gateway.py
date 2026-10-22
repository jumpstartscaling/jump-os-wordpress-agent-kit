#!/usr/bin/env python3
"""A deliberately small, tenant-scoped maintenance gateway.

The gateway accepts only fixed operation names from a root-owned policy file.
It never accepts a shell command, a filesystem path, or an arbitrary plugin name
from a caller.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROLE_ORDER = {"viewer": 0, "operator": 1}
OPERATION_PATHS = {
    "/v1/operations/elementor/update": "elementor_update",
    "/v1/operations/elementor/activate": "elementor_activate",
}
REQUIRED_ACTIONS = {"status", *OPERATION_PATHS.values()}


class PolicyError(ValueError):
    """Raised when a policy is not safe enough to load."""


@dataclass(frozen=True)
class GatewayConfig:
    tenant_id: str
    host: str
    port: int
    audit_log: Path
    action_timeout_seconds: int
    token_hashes: dict[str, tuple[str, ...]]
    actions: dict[str, tuple[str, ...]]

    @classmethod
    def load(cls, path: Path) -> "GatewayConfig":
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PolicyError(f"cannot load policy: {exc}") from exc

        required = {"tenant_id", "host", "port", "audit_log", "token_hashes", "actions"}
        missing = required - raw.keys()
        if missing:
            raise PolicyError(f"policy is missing keys: {', '.join(sorted(missing))}")

        tenant_id = raw["tenant_id"]
        if not isinstance(tenant_id, str) or not tenant_id or len(tenant_id) > 64:
            raise PolicyError("tenant_id must be a non-empty short string")
        host = raw["host"]
        if host not in {"127.0.0.1", "::1"}:
            raise PolicyError("gateway must bind to loopback; publish it through a reverse proxy")
        port = raw["port"]
        if not isinstance(port, int) or not 1024 <= port <= 65535:
            raise PolicyError("port must be an unprivileged TCP port")
        audit_log = Path(raw["audit_log"])
        if not audit_log.is_absolute():
            raise PolicyError("audit_log must be an absolute path")

        hashes: dict[str, tuple[str, ...]] = {}
        for role, values in raw["token_hashes"].items():
            if role not in ROLE_ORDER or not isinstance(values, list) or not values:
                raise PolicyError("token_hashes must contain non-empty viewer/operator lists")
            if any(not isinstance(value, str) or len(value) != 64 for value in values):
                raise PolicyError("every token hash must be a SHA-256 hex digest")
            hashes[role] = tuple(values)
        if "viewer" not in hashes or "operator" not in hashes:
            raise PolicyError("policy must define both viewer and operator tokens")

        actions: dict[str, tuple[str, ...]] = {}
        for name in REQUIRED_ACTIONS:
            command = raw["actions"].get(name)
            if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
                raise PolicyError(f"action {name!r} must be a non-empty argv list")
            if command[0] != "/usr/bin/sudo":
                raise PolicyError(f"action {name!r} must begin with /usr/bin/sudo")
            actions[name] = tuple(command)

        timeout = raw.get("action_timeout_seconds", 180)
        if not isinstance(timeout, int) or not 1 <= timeout <= 900:
            raise PolicyError("action_timeout_seconds must be between 1 and 900")
        return cls(tenant_id, host, port, audit_log, timeout, hashes, actions)


class AuditLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = threading.Lock()

    def write(self, **event: Any) -> None:
        record = {"at": datetime.now(UTC).isoformat(), **event}
        line = json.dumps(record, separators=(",", ":"), sort_keys=True)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")


def token_role(config: GatewayConfig, header: str | None) -> str | None:
    if not header or not header.startswith("Bearer "):
        return None
    token = header.removeprefix("Bearer ").strip()
    if not token:
        return None
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    for role, known_hashes in config.token_hashes.items():
        if any(hmac.compare_digest(digest, known) for known in known_hashes):
            return role
    return None


def run_action(config: GatewayConfig, action: str) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(
        config.actions[action],
        check=False,
        shell=False,
        env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C.UTF-8"},
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=config.action_timeout_seconds,
    )
    stdout = completed.stdout[-8192:]
    stderr = completed.stderr[-4096:]
    try:
        output: Any = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        output = {"message": stdout}
    payload = {"ok": completed.returncode == 0, "action": action, "result": output}
    if completed.returncode != 0:
        payload["error"] = "action_failed"
        payload["detail"] = stderr or "wrapper returned a non-zero status"
    return (HTTPStatus.OK if completed.returncode == 0 else HTTPStatus.BAD_GATEWAY), payload


def make_handler(config: GatewayConfig):
    audit = AuditLog(config.audit_log)

    class TenantGatewayHandler(BaseHTTPRequestHandler):
        server_version = "JumpTenantGateway/0.1"
        protocol_version = "HTTP/1.1"

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def _send(self, status: int, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(data)

        def _client(self) -> str:
            return self.client_address[0]

        def _authorize(self, minimum_role: str) -> str | None:
            role = token_role(config, self.headers.get("Authorization"))
            if role is None or ROLE_ORDER[role] < ROLE_ORDER[minimum_role]:
                audit.write(event="denied", path=self.path, client=self._client())
                self._send(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
                return None
            return role

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/healthz":
                self._send(HTTPStatus.OK, {"ok": True, "service": "tenant-gateway"})
                return
            if path == "/v1/capabilities":
                role = self._authorize("viewer")
                if role:
                    self._send(HTTPStatus.OK, {"ok": True, "tenant": config.tenant_id, "operations": sorted(OPERATION_PATHS.values())})
                return
            if path == "/v1/status":
                role = self._authorize("viewer")
                if not role:
                    return
                status, payload = run_action(config, "status")
                audit.write(event="status", client=self._client(), role=role, ok=payload["ok"])
                self._send(status, payload)
                return
            self._send(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            action = OPERATION_PATHS.get(path)
            if action is None:
                self._send(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            role = self._authorize("operator")
            if not role:
                return
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 1024:
                self._send(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"ok": False, "error": "request_too_large"})
                return
            body = self.rfile.read(content_length) if content_length else b""
            if body not in {b"", b"{}"}:
                self._send(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "operation_accepts_no_arguments"})
                return
            try:
                status, payload = run_action(config, action)
            except subprocess.TimeoutExpired:
                status, payload = HTTPStatus.GATEWAY_TIMEOUT, {"ok": False, "action": action, "error": "action_timed_out"}
            audit.write(event="operation", action=action, client=self._client(), role=role, ok=payload["ok"])
            self._send(status, payload)

    return TenantGatewayHandler


def build_server(config: GatewayConfig) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((config.host, config.port), make_handler(config))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="root-owned JSON policy")
    args = parser.parse_args()
    try:
        config = GatewayConfig.load(args.config)
    except PolicyError as exc:
        print(f"policy error: {exc}", file=sys.stderr)
        return 2
    server = build_server(config)
    print(f"tenant gateway listening on {config.host}:{config.port} for {config.tenant_id}", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())

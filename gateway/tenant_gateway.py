#!/usr/bin/env python3
"""A small, tenant-scoped gateway for fixed host-maintenance operations.

The network API accepts a capability identifier only. Commands, plugin names,
paths, container names, and database credentials stay in an owner-controlled
policy and are never supplied by a recipient.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROLE_ORDER = {"viewer": 0, "operator": 1}
OPERATION_ID = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
LEGACY_OPERATION_IDS = {
    "elementor_update": "plugin-elementor-update",
    "elementor_activate": "plugin-elementor-activate",
}


class PolicyError(ValueError):
    """Raised when a policy is not safe enough to load."""


@dataclass(frozen=True)
class FixedOperation:
    role: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class GatewayConfig:
    tenant_id: str
    host: str
    port: int
    audit_log: Path
    action_timeout_seconds: int
    token_hashes: dict[str, tuple[str, ...]]
    status: FixedOperation
    operations: dict[str, FixedOperation]

    @staticmethod
    def _operation(raw: Any, name: str) -> FixedOperation:
        if not isinstance(raw, dict):
            raise PolicyError(f"{name!r} must be an object")
        role = raw.get("role")
        command = raw.get("command")
        if role not in ROLE_ORDER:
            raise PolicyError(f"{name!r} has an unsupported role")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            raise PolicyError(f"{name!r} command must be a non-empty argv list")
        if command[0] != "/usr/bin/sudo":
            raise PolicyError(f"{name!r} command must begin with /usr/bin/sudo")
        return FixedOperation(role=role, command=tuple(command))

    @classmethod
    def _legacy_actions(cls, raw_actions: Any) -> tuple[FixedOperation, dict[str, FixedOperation]]:
        """Translate the 0.1 policy format without widening its permissions."""
        if not isinstance(raw_actions, dict) or "status" not in raw_actions:
            raise PolicyError("legacy actions must include status")
        status = cls._operation({"role": "viewer", "command": raw_actions["status"]}, "status")
        operations: dict[str, FixedOperation] = {}
        for action_name, command in raw_actions.items():
            if action_name == "status":
                continue
            if not isinstance(action_name, str):
                raise PolicyError("legacy action names must be strings")
            operation_id = LEGACY_OPERATION_IDS.get(action_name, action_name.replace("_", "-"))
            if not OPERATION_ID.fullmatch(operation_id) or operation_id in operations:
                raise PolicyError("legacy action names must map to unique lowercase kebab-case identifiers")
            operations[operation_id] = cls._operation({"role": "operator", "command": command}, operation_id)
        if not operations:
            raise PolicyError("legacy actions must include at least one operation")
        return status, operations

    @classmethod
    def load(cls, path: Path) -> "GatewayConfig":
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PolicyError(f"cannot load policy: {exc}") from exc

        required = {"tenant_id", "host", "port", "audit_log", "token_hashes"}
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
            if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in values):
                raise PolicyError("every token hash must be a lowercase SHA-256 hex digest")
            hashes[role] = tuple(values)
        if "viewer" not in hashes or "operator" not in hashes:
            raise PolicyError("policy must define both viewer and operator tokens")

        if "status" in raw or "operations" in raw:
            if "status" not in raw or "operations" not in raw:
                raise PolicyError("canonical policies require both status and operations")
            status = cls._operation(raw["status"], "status")
            if status.role != "viewer":
                raise PolicyError("status must require viewer role")
            raw_operations = raw["operations"]
            if not isinstance(raw_operations, dict) or not raw_operations:
                raise PolicyError("operations must be a non-empty object")
            operations: dict[str, FixedOperation] = {}
            for operation_id, operation in raw_operations.items():
                if not isinstance(operation_id, str) or not OPERATION_ID.fullmatch(operation_id):
                    raise PolicyError("operation identifiers must be lowercase kebab-case")
                operations[operation_id] = cls._operation(operation, operation_id)
        elif "actions" in raw:
            status, operations = cls._legacy_actions(raw["actions"])
        else:
            raise PolicyError("policy must use canonical status/operations or legacy actions")

        timeout = raw.get("action_timeout_seconds", 180)
        if not isinstance(timeout, int) or not 1 <= timeout <= 900:
            raise PolicyError("action_timeout_seconds must be between 1 and 900")
        return cls(tenant_id, host, port, audit_log, timeout, hashes, status, operations)


class AuditLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = threading.Lock()

    def write(self, **event: Any) -> None:
        line = json.dumps({"at": datetime.now(UTC).isoformat(), **event}, separators=(",", ":"), sort_keys=True)
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


def run_operation(config: GatewayConfig, operation: FixedOperation, operation_id: str) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(
        operation.command, check=False, shell=False,
        env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C.UTF-8"},
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, timeout=config.action_timeout_seconds,
    )
    stdout, stderr = completed.stdout[-8192:], completed.stderr[-4096:]
    try:
        output: Any = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        output = {"message": stdout}
    payload = {"ok": completed.returncode == 0, "operation": operation_id, "result": output}
    if completed.returncode != 0:
        payload.update(error="operation_failed", detail=stderr or "wrapper returned a non-zero status")
    return (HTTPStatus.OK if completed.returncode == 0 else HTTPStatus.BAD_GATEWAY), payload


def make_handler(config: GatewayConfig):
    audit = AuditLog(config.audit_log)

    class TenantGatewayHandler(BaseHTTPRequestHandler):
        server_version = "JumpTenantGateway/0.2"
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

        def _authorize(self, minimum_role: str) -> str | None:
            role = token_role(config, self.headers.get("Authorization"))
            if role is None or ROLE_ORDER[role] < ROLE_ORDER[minimum_role]:
                audit.write(event="denied", path=self.path, client=self.client_address[0])
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
                    operations = [
                        {"id": operation_id, "method": "POST", "minimum_role": operation.role}
                        for operation_id, operation in sorted(config.operations.items())
                    ]
                    self._send(HTTPStatus.OK, {"ok": True, "tenant": config.tenant_id, "operations": operations})
                return
            if path == "/v1/status":
                role = self._authorize(config.status.role)
                if not role:
                    return
                try:
                    status, payload = run_operation(config, config.status, "status")
                except subprocess.TimeoutExpired:
                    status, payload = HTTPStatus.GATEWAY_TIMEOUT, {"ok": False, "operation": "status", "error": "operation_timed_out"}
                audit.write(event="status", client=self.client_address[0], role=role, ok=payload["ok"])
                self._send(status, payload)
                return
            self._send(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            prefix = "/v1/operations/"
            operation_id = path.removeprefix(prefix) if path.startswith(prefix) else ""
            operation = config.operations.get(operation_id)
            if operation is None:
                self._send(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            role = self._authorize(operation.role)
            if not role:
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                content_length = 1025
            if content_length > 1024:
                self._send(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"ok": False, "error": "request_too_large"})
                return
            body = self.rfile.read(content_length) if content_length else b""
            if body not in {b"", b"{}"}:
                self._send(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "operation_accepts_no_arguments"})
                return
            try:
                status, payload = run_operation(config, operation, operation_id)
            except subprocess.TimeoutExpired:
                status, payload = HTTPStatus.GATEWAY_TIMEOUT, {"ok": False, "operation": operation_id, "error": "operation_timed_out"}
            audit.write(event="operation", operation=operation_id, client=self.client_address[0], role=role, ok=payload["ok"])
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

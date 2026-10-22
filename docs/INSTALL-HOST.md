# Host installation

This is the optional, highest-privilege adapter for a platform owner who controls a VPS, VM, or container host. Shared-hosting and managed WordPress users should use [the WordPress Bridge](INSTALL-WORDPRESS-BRIDGE.md) instead. Run it only after replacing every placeholder with the current tenant's authority chain and rollback plan.

## 1. Create the service identity

```bash
sudo useradd --system --home /nonexistent --shell /usr/sbin/nologin tenant-gateway
sudo install -d -o tenant-gateway -g tenant-gateway -m 0750 /var/log/jump-tenant-gateway
sudo install -d -o root -g root -m 0755 /opt/jump-tenant-gateway
```

Copy the repository's `gateway/` directory to `/opt/jump-tenant-gateway/gateway/` as `root:root` with mode `0755` for directories and `0644` for files.

## 2. Install root-owned wrappers

Create one wrapper per approved operation under `/usr/local/libexec/`. A wrapper must:

1. load a root-owned tenant configuration with fixed container and plugin values;
2. take no arguments;
3. use `set -euo pipefail` and `flock` for a mutating operation;
4. back up the affected database and `wp-content` before updating a plugin;
5. run the WordPress updater as the web-server account inside the **one** configured container;
6. emit bounded JSON and exit non-zero on failure.

The policy must name every capability and call its wrapper through an exact argv array:

```json
"status": {
  "role": "viewer",
  "command": ["/usr/bin/sudo", "/usr/local/libexec/tenant-alpha-status"]
}
```

Do not put `sh -c`, user input, wildcards, or a dynamic plugin name in the policy.

## 3. Restrict sudo exactly

Create `/etc/sudoers.d/tenant-gateway` with `visudo -cf` validation:

```sudoers
Cmnd_Alias TENANT_GATEWAY = /usr/local/libexec/tenant-alpha-status, /usr/local/libexec/tenant-alpha-elementor-update, /usr/local/libexec/tenant-alpha-elementor-activate
tenant-gateway ALL=(root) NOPASSWD: TENANT_GATEWAY
```

Never add `ALL`, `docker`, `systemctl`, an editor, a shell, or a wildcard argument to this file.

## 4. Create the private policy

Use `examples/private-policy.template.json` as a starting point. Generate long random tokens locally, store only their SHA-256 hashes in the policy, and keep raw tokens solely in a recipient package or the recipient's secret manager.

```bash
python3 - <<'PY'
import hashlib, secrets
token = secrets.token_urlsafe(48)
print('raw token (store once):', token)
print('sha256 for private policy:', hashlib.sha256(token.encode()).hexdigest())
PY
```

Install the policy as `root:tenant-gateway`, mode `0640`. The service account needs to read hashes and action names, but must not be able to change them.

## 5. Install the systemd service and reverse-proxy route

Copy `deploy/systemd/jump-tenant-gateway.service`, set its config path, then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jump-tenant-gateway.service
sudo systemctl is-active jump-tenant-gateway.service
curl -fsS http://127.0.0.1:8789/healthz
```

Add the narrowly matched reverse-proxy route in `deploy/caddy/tenant-gateway.caddyfile.example` **before** the tenant's catch-all WordPress proxy. Validate and reload the existing Caddy service using your host's approved procedure.

## 6. Prove the boundary

Before issuing a recipient package, record all of these:

- `tenant-gateway` has no login shell, no Docker-group membership, and no general sudo permission;
- an anonymous `/v1/status` request is `401`;
- a viewer token can read status but gets `401` for every operator capability;
- an operator token can invoke only an empty-body named operation;
- a made-up operation or a JSON body containing a shell/path argument is rejected;
- public tenant pages and the WordPress API still work after the Caddy route is installed.

## Content-only WordPress account

Create a separate WordPress user with the `editor` role. Do not use an administrator account. Create an application password for REST-based agents and keep it in the private recipient package; revoke the password rather than recycling accounts when access ends.

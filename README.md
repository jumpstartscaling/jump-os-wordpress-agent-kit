# Jump OS Tenant Gateway

Tenant-scoped, auditable access for human and AI operators.

> Created by Christopher Amaya · a Jump OS Free Value project · MIT licensed

Giving an AI agent a normal SSH account, `sudo`, or Docker access is **not** tenant isolation. This project provides a small, explicit maintenance gateway and an onboarding package so an operator can work on one WordPress tenant without being able to browse or control the rest of a host.

## What it does

- exposes only named, allowlisted tenant operations over a bearer-token API;
- keeps host privileges in root-owned wrapper scripts, rather than in the gateway process;
- uses a dedicated non-sudo, non-Docker service account;
- records an audit event for every authenticated request without logging tokens;
- supports a separate WordPress Editor account for content and Elementor work;
- creates a shareable recipient package for Codex, ChatGPT, Claude, Cursor, and local agents.

The reference policy includes exactly these maintenance operations:

| Operation | Purpose |
| --- | --- |
| `GET /v1/status` | Read tenant health and Elementor state. |
| `POST /v1/operations/elementor/update` | Back up and update Elementor through WordPress's normal updater. |
| `POST /v1/operations/elementor/activate` | Restore Elementor activation when an authorized operator needs it. |

There is no generic shell endpoint, file browser, Docker socket, database console, or arbitrary plugin endpoint.

## Security model

The gateway service account may invoke only three exact root-owned wrappers through narrowly scoped `sudoers` rules. The wrappers contain no user-supplied command fragments. A gateway token is scoped to one tenant and may be revoked by removing its SHA-256 hash from the private policy and restarting the service.

For content changes, use a WordPress user with the `editor` role. Do **not** make the content operator a WordPress administrator merely to let an agent update plugins. Keep maintenance privileges in this gateway.

See [the architecture](docs/ARCHITECTURE.md), [host installation guide](docs/INSTALL-HOST.md), and [recipient handoff guide](docs/RECIPIENT-HANDOFF.md).

## Quick start (development)

```bash
python3 -m unittest discover -s tests -v
python3 gateway/tenant_gateway.py --config examples/dev-policy.json
curl http://127.0.0.1:8789/healthz
```

The example policy uses harmless commands. It is not a production configuration.

## Agent onboarding

The recipient package contains `AGENTS.md`, a no-dependency `tenantctl` client, capability boundaries, and product-specific setup notes:

- [Codex](docs/agents/CODEX.md)
- [ChatGPT](docs/agents/CHATGPT.md)
- [Claude](docs/agents/CLAUDE.md)
- [Cursor](docs/agents/CURSOR.md)
- [Local agents](docs/agents/LOCAL-AGENTS.md)

Create a package with `python3 scripts/build_recipient_pack.py --help`. Never commit a generated package containing credentials.

## Public-project boundaries

This repository deliberately does not contain tenant domains, client names, usernames, IP addresses, backups, production paths, API tokens, application passwords, or Caddy credentials. Use the templates under `examples/` to create private deployment material.

## License

[MIT](LICENSE)
Tenant-scoped, auditable access for human and AI operators.

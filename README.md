# Jump OS WordPress Agent Kit

Safe, tenant-scoped access for people and AI agents operating WordPress.

> Created by Christopher Amaya · a Jump OS Free Value project · MIT licensed

This is not a Jump OS-only product. It is a free, open-source kit designed for ordinary WordPress owners, agencies, shared hosting, managed WordPress, VPS deployments, and cloud-agent users. It gives every installation the same rule: an agent receives only the capabilities you deliberately grant to one WordPress site.

## Choose the installation path

| Situation | Use this path | What it provides |
| --- | --- | --- |
| Any normal WordPress site with an Editor account and application passwords | **Native WordPress REST** | Content, pages, media, and Elementor editing through the site's own role system. |
| Shared hosting or managed WordPress that permits a custom plugin | **WordPress Bridge** | Token-scoped status and activation of explicitly allowed installed plugins; no server access required. |
| VPS, Docker, or a host where the owner can install a local service | **Host Gateway** | Fixed, audited maintenance operations such as verified-backup plugin update. |
| Provider forbids custom plugins or server access | **Native REST or provider dashboard** | Content work only; maintenance stays with the owner/provider. |

The project does not emulate host privileges in WordPress, guess provider APIs, or supply a universal “update any plugin” endpoint. That would make a dangerous promise. [Provider compatibility](docs/PROVIDER-COMPATIBILITY.md) states the supported path for each hosting model.

## What every path protects

- one named WordPress tenant per package and per token;
- a least-privilege WordPress role for content work;
- no SSH, Docker, database console, filesystem browser, shell, or sibling-tenant discovery in a recipient package;
- capability discovery before an agent acts;
- no arbitrary plugin name, path, command, or request argument in maintenance calls;
- private secrets separated from the public repository and from agent instructions.

## Install

1. Start with [Provider compatibility](docs/PROVIDER-COMPATIBILITY.md), the [compatibility registry](docs/COMPATIBILITY-REGISTRY.md), and [installation topologies](docs/WORDPRESS-INSTALLATION-TOPOLOGIES.md).
2. For most ordinary sites, follow [WordPress Bridge installation](docs/INSTALL-WORDPRESS-BRIDGE.md).
3. For an owned VPS/container, follow [Host Gateway installation](docs/INSTALL-HOST.md).
4. Build a private agent/human handoff package with [Recipient handoff](docs/RECIPIENT-HANDOFF.md).

The bridge plugin is built locally so releases never contain tenant credentials:

```bash
python3 scripts/build_wordpress_bridge_zip.py --output private/jump-os-wordpress-agent-bridge.zip
```

## API contract

Both the Host Gateway and WordPress Bridge use a small capability model:

```text
GET  status
GET  capabilities
POST operations/<allowlisted-capability-id>   # empty body only
```

`tenantctl.py` has no provider SDK dependency:

```bash
python3 tenantctl.py capabilities
python3 tenantctl.py status
python3 tenantctl.py run plugin-elementor-activate
```

The capability list is authoritative. If it is not listed, the agent must stop and ask the site owner.

## Agent onboarding

The generated private package contains `AGENTS.md`, a no-dependency client, a private `.env`, and instructions for:

- [Codex](docs/agents/CODEX.md)
- [ChatGPT](docs/agents/CHATGPT.md)
- [Claude](docs/agents/CLAUDE.md)
- [Cursor](docs/agents/CURSOR.md)
- [Local agents](docs/agents/LOCAL-AGENTS.md)

Read the full [agent runtime compatibility guide](docs/AGENT-RUNTIME-COMPATIBILITY.md) before putting a private package into any local or cloud agent.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile gateway/tenant_gateway.py client/tenantctl.py scripts/build_recipient_pack.py scripts/build_wordpress_bridge_zip.py
php -l wordpress-plugin/jump-os-wordpress-agent-bridge/jump-os-wordpress-agent-bridge.php
```

See [architecture](docs/ARCHITECTURE.md) for the security boundary. The public repository never contains tenant domains, client names, host paths, backups, tokens, application passwords, or provider credentials.

## Community and security

- [Compatibility program](docs/PROVIDER-COMPATIBILITY.md) — report a tested host or agent runtime through the compatibility issue form.
- [Contributing](CONTRIBUTING.md) · [Support](SUPPORT.md) · [Security](SECURITY.md) · [Versioning](VERSIONING.md) · [Upgrading](docs/UPGRADING.md)

## License

[MIT](LICENSE)

# Architecture

## One capability contract, three adapters

```text
Human or AI agent
        |
        | private token or WordPress application password
        v
    tenantctl / WordPress REST client
        |
        +---------------- Native WordPress REST ----------------> Editor role, one site
        |
        +---------------- WordPress Bridge ---------------------> allowed plugin activation, one site
        |
        +---------------- Host Gateway -------------------------> fixed root-owned wrappers, one tenant
```

The product boundary is the same in each mode: the recipient can discover and use only capabilities the tenant owner configured. The adapter determines how much maintenance is possible; it does not broaden the recipient's authority.

## Adapter responsibilities

| Adapter | Runs where | Good for | Does not provide |
| --- | --- | --- | --- |
| Native WordPress REST | WordPress itself | Content and media work using WordPress roles | Plugin/core maintenance or host access. |
| WordPress Bridge | A custom WordPress plugin | Status plus activation of exact configured plugins | A claim that a provider backup exists; arbitrary plugin actions. |
| Host Gateway | Owner-controlled host | Verified-backup maintenance through root-owned fixed wrappers | A portable shared-hosting installation or generic shell. |

## Roles

| Role | Intended use | Can do |
| --- | --- | --- |
| WordPress Editor | Content owner or content-focused agent | Edit only the site's published content, media, and approved builder content. |
| Viewer token | Support/review agent | Read tenant status and listed capabilities. |
| Operator token | Explicit maintenance agent | Invoke only a listed, empty-body capability. |
| Site/host administrator | Owner only | Install/configure adapters, rotate tokens, and choose backup/recovery procedures. |

An Editor is not an administrator. An operator token is not a shell. A site administrator is not an invitation to hand the agent the hosting account.

## Host Gateway constraints

The Host Gateway binds to loopback, and the owner's reverse proxy provides TLS and routing. Its private policy maps each lower-case capability ID to an exact root-owned wrapper. It never accepts a command, path, plugin file, container name, SQL, or dynamic argument from the network.

- The service identity has no login shell, Docker group, or general sudo.
- Every sudoers entry is one exact wrapper with no wildcard arguments.
- A wrapper must hold its tenant identifier and backup process privately and take no arguments.
- Tokens are stored as SHA-256 hashes; audit logs never store bearer tokens or WordPress passwords.
- `NoNewPrivileges=true` cannot be used if the chosen Host Gateway design intentionally relies on exact sudo elevation; the exact sudoers allowlist is then the privilege boundary.

## WordPress Bridge constraints

The Bridge stores only password hashes in WordPress options. Its Settings screen is admin-only. It exposes only the exact plugin files the site owner listed, never a plugin path supplied by an API caller. The base bridge deliberately omits update operations because it cannot prove a portable, restorable pre-update backup across providers.

## Threat model and limits

This protects sibling tenants and the hosting account from a recipient package. It does not make unsafe page HTML, third-party plugins, or an over-privileged WordPress role harmless within the one tenant. Use revisions, staging, provider backups, and human approval according to the risk of the requested change.

A public repository has only source and templates. Tenant domains, customer names, host paths, backups, tokens, application passwords, provider credentials, and generated private handoff ZIPs remain private.

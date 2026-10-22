# Architecture

## Boundary map

```text
Recipient agent or human
        |
        | HTTPS + one tenant-scoped bearer token
        v
Reverse proxy path dedicated to one tenant
        |
        v
Rootless tenant-gateway service
        |                 \
        | exact sudoers    \ WordPress Editor credentials
        v                  v
Root-owned fixed wrappers  WordPress REST/dashboard
        |
        v
One named WordPress container and one mounted wp-content tree
```

The gateway never receives a command, plugin path, filesystem path, database query, or container name from the network. Its private JSON policy maps a fixed route to a fixed, root-owned wrapper.

## Roles

| Role | Intended use | Can do |
| --- | --- | --- |
| WordPress Editor | Content owner or content-focused agent | Edit published pages, posts, media, and Elementor content within one site. |
| Gateway viewer | Support agent | Read the tenant status and the approved capability list. |
| Gateway operator | Maintenance agent | Invoke the named Elementor update or activation wrapper. |
| Host administrator | Platform owner only | Install wrappers, rotate/revoke tokens, inspect the host, or change the policy. |

WordPress Editor and gateway operator are separate credentials. Neither one is a host administrator.

## Non-negotiable constraints

- The gateway binds only to `127.0.0.1` or `::1`; the reverse proxy owns TLS and public routing.
- The gateway service user is not in the `docker` group and has no general `sudo` or SSH shell privilege.
- Each `sudoers` entry names one wrapper with no wildcard arguments.
- Wrapper scripts use fixed `docker exec` targets supplied by a root-owned tenant configuration. They must not evaluate request input.
- Tokens are stored as SHA-256 hashes in the private policy. Audit events never store bearer tokens or WordPress passwords.
- A public repository contains templates only. Production domains, paths, usernames, tokens, backups, and Caddy credentials stay private.

## Threat model and limits

This protects sibling tenants from an operator or agent that has a recipient package. It does not turn a WordPress Editor into a safe reviewer of untrusted page code: content, HTML widgets, and third-party plugins still affect visitors to that one tenant. Use WordPress revision review and staging when content risk requires it.

The gateway itself is a privileged control surface. Keep it small, patch the host, put it behind HTTPS, use a long random token, rotate that token after sharing a package, and revoke it immediately if a package is lost.

# Public roadmap

This is the single public roadmap for the Jump OS WordPress Agent Kit. It keeps the public repository understandable without using automated dependency tickets or unsupported provider promises.

## Done — v0.3 baseline

- **Release package and verification:** public WordPress Bridge and agent-workspace ZIPs, secret-free manifests, SHA-256 checksums, package validation, and CI evidence.
- **Human and agent installation guidance:** provider-neutral installation instructions for site owners plus Codex, ChatGPT, Claude, Cursor, and local-agent users.
- **Public-surface cleanup:** one `main` branch, no open pull requests, no repository issue-form intake, one compatibility Discussion, private security reporting, and a documented release process.

## Next — evidence before claims

- **Compatibility evidence registry:** collect sanitized, reproducible results for a specific WordPress deployment class, hosting plan, and agent runtime. [Report in the compatibility Discussion](https://github.com/jumpstartscaling/jump-os-wordpress-agent-kit/discussions/4).
- **Provider adapters and capability matrix:** establish safe support boundaries for Native WordPress REST, WordPress Bridge, Host Gateway, WP-CLI, SFTP, panels, managed hosting, and multisite.
- **v1.0 release gate:** require stable contracts, backward-compatible migrations, security review, repeatable releases, and independently verified provider coverage. This is a gate, not a date promise.

## Evidence rule

A hosting provider is not “compatible” merely because its marketing page mentions WordPress. The [compatibility registry](COMPATIBILITY-REGISTRY.md) records the exact access path, deployment class, and evidence level. If an operation cannot be proven safe for that environment, the kit stops rather than guessing.

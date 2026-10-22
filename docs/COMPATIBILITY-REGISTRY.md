# Compatibility registry

This registry deliberately distinguishes an installation pattern from a provider marketing claim. A provider name is not proof that a particular plan, region, multisite setting, security plugin, or WAF will permit an adapter.

## Evidence levels

| Level | Meaning | May the README call it compatible? |
| --- | --- | --- |
| Reference-tested | Maintainer has a repeatable anonymized test receipt in this project’s supported deployment class. | Yes, with the exact class named. |
| Sandbox verified | A contributor supplied a reproducible staging/sandbox receipt that was reviewed. | Yes, as sandbox verified. |
| Documented candidate | Official documentation indicates the prerequisites, but this project has not independently tested it. | No; list only as a candidate. |
| Reported problem | A reproducible incompatibility or missing prerequisite was reported. | No; link the issue and workaround. |

## Current registry

| Installation/provider class | Suggested adapter | Evidence | Notes |
| --- | --- | --- | --- |
| Owner-managed Linux + Docker WordPress | Host Gateway | Reference-tested | Requires a root-owned tenant wrapper, verified backup, and explicit reverse-proxy route. |
| Standard self-hosted WordPress 6+ with custom-plugin install | WordPress Bridge | Local reproducible test | Requires site-owner setup and an exact plugin allowlist. |
| Standard WordPress REST with a scoped Editor and application password | Native REST | Documented candidate | Site/plugin policy may disable application passwords or REST routes. |
| Hostinger WordPress plans | WordPress Bridge or Native REST | Documented candidate | Confirm custom-plugin upload, application passwords, backups, and staging on the exact plan. |
| Bluehost WordPress plans | WordPress Bridge or Native REST | Documented candidate | Same four checks; report exact plan/installer behavior. |
| GoDaddy Managed WordPress | Native REST first; Bridge only after policy check | Documented candidate | Managed plan restrictions are authoritative. |
| SiteGround WordPress | WordPress Bridge or Native REST | Documented candidate | Confirm Site Tools backup/staging flow before maintenance. |
| DreamHost, Namecheap EasyWP, IONOS, A2 Hosting | WordPress Bridge or Native REST | Documented candidate | Confirm plugin install permission and application-password behavior. |
| Kinsta, WP Engine, Flywheel, Pressable, Cloudways | Native REST first; Bridge only after current provider policy check | Documented candidate | Use provider staging/backups and restricted-plugin policy as authority. |
| WordPress.com paid plans | Native REST; Bridge only if custom plugin upload is permitted on that site | Documented candidate | WordPress.com plan/eligibility controls apply. |
| WordPress.com free or locked-down hosted tier | Provider UI/content roles only | Documented limitation | Do not attempt to work around the provider’s plugin restrictions. |
| WordPress multisite | Native REST per site; Bridge/Host only after network-admin design review | Documented limitation | Never use a super-admin package as a shortcut. |

## Help us move a candidate to verified

Add a reply to the [compatibility discussion](https://github.com/jumpstartscaling/jump-os-wordpress-agent-kit/discussions/4) after testing. Include no tenant identity or secrets. The most useful reports state:

1. provider and exact plan class;
2. single site or multisite, WordPress/PHP version, and WAF/security plugin presence;
3. whether custom-plugin upload, REST application passwords, staging, and backup/restore were confirmed;
4. which adapter was tried and the anonymized result;
5. whether the test was local, sandbox, or production with anonymized evidence.

Maintainers will not mark a row verified merely from a comment; the report must include reproducible, sanitized evidence. The resulting work and evidence status are tracked in the [public roadmap](https://github.com/users/jumpstartscaling/projects/29).

# WordPress installation topologies

WordPress is not one deployment model. Choose the adapter by where authority actually resides.

| Topology | Who controls files/runtime? | Safe default | Escalation path | Do not assume |
| --- | --- | --- | --- | --- |
| Shared hosting with cPanel/Plesk/DirectAdmin | Site owner/provider | Native REST, then Bridge if custom plugin upload works | Provider backup/staging UI | SSH, WP-CLI, database access, or custom PHP settings. |
| One-click installer WordPress | Provider/site owner | Native REST or Bridge | Confirm ownership, plugin upload, and file permissions | The installer account equals server authority. |
| Managed WordPress | Provider plus site admin | Native REST first | Provider staging/backup/update workflow | A generic plugin, WP-CLI, or arbitrary filesystem access is allowed. |
| WordPress.com | WordPress.com | Provider roles/Native REST where supported | Plan-specific plugin management | WordPress.org filesystem or custom-plugin upload is available. |
| VPS/VM LAMP/LEMP | Infrastructure owner | Host Gateway plus separate Editor | Root-owned wrapper with verified backup | A recipient should receive SSH/sudo. |
| Docker/Compose/Kubernetes | Infrastructure owner | Host Gateway | Fixed workload identity and wrapper | Docker socket or cluster credential is tenant-scoped. |
| Bedrock/Composer deployment | Engineering owner | Native REST for content; Host Gateway for code/plugin maintenance | Build/deploy pipeline with lockfile/release evidence | WP Admin can safely mutate version-controlled plugins. |
| Git-deployed immutable WordPress | Engineering owner | Native REST for content | CI/CD release path | Filesystem-based plugin update will persist. |
| Multisite | Network admin and site admin differ | Native REST per site | Network review and a separate network-level design | Site admin should activate network plugins. |
| Headless WordPress | API/application owners | Native REST after API/auth verification | Application release pipeline | A page edit automatically changes every consumer safely. |

## Common blockers and correct responses

| Blocker | Correct response |
| --- | --- |
| REST API disabled or WAF blocks requests | Ask owner to permit only the canonical required route after staging verification; do not route around a WAF. |
| Application passwords disabled | Use an approved OAuth/provider method or human dashboard workflow; do not share an administrator password as a workaround. |
| Plugin installation disabled | Use Native REST/content only or the provider dashboard; do not upload through filesystem credentials unless the owner explicitly controls that host path. |
| No provider backup proof | Do not automate updates. Use human/provider backup and recovery workflow. |
| WordPress is version controlled | Treat plugin/code changes as source release changes, not dashboard operations. |
| Cloud agent cannot restrict egress or safely store a secret | Use it for planning/review; execute through a human or local agent. |

## Minimum discovery checklist

Before issuing a private package, a human owner must establish the canonical site URL, deployment topology, WordPress version, role model, REST availability, custom-plugin policy, backup/restore owner, staging availability, WAF behavior, and revocation path. Unknown is a valid answer; it means the higher-privilege adapter is not yet authorized.

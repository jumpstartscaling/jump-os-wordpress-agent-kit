# Provider compatibility

This project is compatible with WordPress deployment models, not with a made-up universal hosting-control API. Choose the least-powerful path that the provider and site actually support.

| Provider/setup | Content work | Bridge plugin | Host Gateway | Maintenance boundary |
| --- | --- | --- | --- | --- |
| Self-hosted WordPress.org, cPanel, Plesk, DirectAdmin | WordPress Editor + application password | Yes, if the site owner can upload/activate a plugin | Only if the owner operates the server | Owner verifies backup and filesystem behavior. |
| Hostinger, Bluehost, GoDaddy, SiteGround shared WordPress | Same | Usually the preferred portable path when custom plugins are allowed | Usually not applicable without separate VPS access | Use the host's own backup/restore control before an update. |
| Managed WordPress (Kinsta, WP Engine, Flywheel, Cloudways, etc.) | Same | Use only after checking the provider's current plugin policy and site plan | Only where the provider grants a supported server/runtime boundary | Provider-specific restrictions and staging/backup workflow remain authoritative. |
| VPS or Docker deployment | Same | Optional | Preferred for strict verified-backup maintenance | Root-owned fixed wrappers can run only named tenant actions. |
| WordPress.com paid site with plugin access | WordPress role/API subject to plan and site configuration | Only when the exact site can install this custom plugin | No | Use WordPress.com management and backup controls for updates. |
| WordPress.com free site or any locked-down hosted plan | Provider-supported content roles only | No | No | No maintenance automation; do not attempt a workaround. |

## Important limits

- **No provider is assumed.** A green cell means the path is technically possible after the owner verifies their plan, plugin policy, and site settings; it does not grant access by itself.
- **No generic backup claim.** The WordPress Bridge intentionally does not offer plugin updates. It cannot verify whether every provider created a restorable backup. Use a Host Gateway wrapper with a verified backup, or the provider's backup/update workflow.
- **Multisite is distinct.** Network plugin control and site-level content roles have different authority. Treat each network as a separate installation design, and do not hand an AI a super-admin credential.
- **WordPress.com is not self-hosted WordPress.** Its plan and product controls determine whether plugins are available. WordPress.com documents that plugin installation is available on paid plans and that users should check eligibility when plugin management is unavailable. [WordPress.com plugin installation](https://wordpress.com/support/plugins/install-a-plugin/)

## Verify before issuing a package

1. Confirm the canonical site URL and whether it is a single site or multisite.
2. Confirm the exact WordPress role, custom-plugin policy, application-password availability, and backup/restore owner.
3. Install the Bridge only on a staging site first when the provider offers staging.
4. Verify anonymous bridge requests are denied, a viewer can read only status/capabilities, and an operator cannot pass a request body or name an unlisted plugin.
5. Share only the private package, never a public Drive link or repository secret.

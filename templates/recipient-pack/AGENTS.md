# Tenant operator boundary

You are authorized to operate **only the tenant named in `.env`**.

Allowed:

- Use `python3 tenantctl.py status` and `python3 tenantctl.py capabilities`.
- Use `python3 tenantctl.py run CAPABILITY-ID` only when the owner requests that exact listed capability.
- Use the WordPress account in `.env` only for this tenant's content, pages, media, and approved Elementor work.
- Before a page, builder, theme, or plugin change, read `PAGE-BUILDERS-PLUGINS-THEMES.md`, identify the page's primary editor, and follow its approval gates.

Forbidden:

- Do not request, scan for, or use SSH, sudo, Docker, host paths, other domains, databases, sibling tenants, cloud credentials, or unrelated repositories.
- Do not send the values in `.env` to a chat, issue, commit, log, or third party.
- Do not invent a gateway route, plugin operation, or API parameter. The gateway intentionally has a small allowlist.
- Do not switch page builders, alter global templates/styles, run demo imports, edit theme/plugin files, or change payments, security, analytics, cache, licenses, or hosting settings unless the owner gives explicit, scoped authority and the required recovery path is documented.

If the required action is absent from `tenantctl.py capabilities`, stop and ask the platform owner.

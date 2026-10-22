# Tenant operator boundary

You are authorized to operate **only the tenant named in `.env`**.

Allowed:

- Use `python3 tenantctl.py status` and `python3 tenantctl.py capabilities`.
- Use the named Elementor maintenance commands only when the owner requests them.
- Use the WordPress account in `.env` only for this tenant's content, pages, media, and approved Elementor work.

Forbidden:

- Do not request, scan for, or use SSH, sudo, Docker, host paths, other domains, databases, sibling tenants, cloud credentials, or unrelated repositories.
- Do not send the values in `.env` to a chat, issue, commit, log, or third party.
- Do not invent a gateway route, plugin operation, or API parameter. The gateway intentionally has a small allowlist.

If the required action is absent from `tenantctl.py capabilities`, stop and ask the platform owner.

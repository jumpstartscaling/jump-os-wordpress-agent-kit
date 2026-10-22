# Start here

This package is a private credential bundle for one WordPress tenant.

1. Keep the folder and `.env` private. Do not commit it.
2. In a terminal, load the values: `set -a; source .env; set +a`.
3. Check the boundary: `python3 tenantctl.py capabilities` and `python3 tenantctl.py status`.
4. For page work, sign into the `WORDPRESS_URL` dashboard with `WORDPRESS_USERNAME` and `WORDPRESS_DASHBOARD_PASSWORD`. Use the application password only for WordPress REST clients, not for browser sign-in.
5. Before editing a page or builder layout, read `PAGE-BUILDERS-PLUGINS-THEMES.md`. Identify the page's actual editor and whether a template, global component, or dynamic field is involved. If it is unclear, stop and ask the owner.
6. Before running any maintenance capability, run status. After it, run status again and verify the public page the owner names. Only run a capability that appears in `tenantctl.py capabilities` and that the owner explicitly requested.

If this package is lost or sent to the wrong place, tell the platform owner immediately so they can revoke the gateway token and WordPress application password.

# WordPress Bridge installation

Use this path when a site supports custom plugins but you do not own or need host-level access. It is suitable for standard WordPress, shared hosting, and many managed providers after the site owner confirms their current plugin policy.

## 1. Build and install the plugin

From a clean clone:

```bash
python3 scripts/build_wordpress_bridge_zip.py --output private/jump-os-wordpress-agent-bridge.zip
```

In the target site's **WordPress Admin**, use Plugins → Add New → Upload Plugin, upload the ZIP, and activate it. The code is the same public source; the ZIP contains no tenant information or secrets.

## 2. Configure one site only

Open Settings → Jump OS Agent Bridge while logged in as the site owner. Generate a distinct viewer token and operator token with a password manager. Store them in the eventual private recipient package, enter them once in the settings screen, and add only exact installed plugin file paths, such as:

```text
elementor/elementor.php
woocommerce/woocommerce.php
```

The plugin stores password hashes, not recoverable tokens. It exposes activation for the exact plugins listed here; it does not accept a plugin name in an API request.

## 3. Test before sharing

The bridge endpoint is:

```text
https://YOUR-SITE.example/wp-json/jump-os-agent/v1
```

Set the private package mode to `wordpress-bridge`, then verify:

```bash
python3 tenantctl.py capabilities
python3 tenantctl.py status
```

An anonymous request must return `401`. A viewer token must not run an operation. An operator request with any JSON body other than `{}` must be rejected.

## 4. Updates and recovery

The base Bridge intentionally does not update WordPress or plugins. Shared and managed hosts differ too much for the plugin to prove it made a usable backup. Use the provider's backup/restore process, an approved staging workflow, or the [Host Gateway](INSTALL-HOST.md) only when you control the host and can verify the pre-update backup.

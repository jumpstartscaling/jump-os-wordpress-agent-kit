# Upgrading safely

## Before any upgrade

1. Record the installed tag/commit, active adapter, canonical tenant URL, and current `tenantctl.py capabilities` response.
2. Copy the private policy and recipient package to a protected rollback location. Do not commit either artifact.
3. For a host gateway, validate the policy with the new code before restarting the existing service.
4. For a WordPress Bridge, test the new ZIP on provider staging when available, then verify anonymous `401`, viewer read-only behavior, and the operator’s exact allowlist.

## v0.1 host gateway to v0.3+

The original policy used an `actions` object. The current gateway accepts it and translates only these legacy names:

```json
"actions": {
  "status": ["/usr/bin/sudo", "/usr/local/libexec/tenant-status"],
  "elementor_update": ["/usr/bin/sudo", "/usr/local/libexec/tenant-elementor-update"],
  "elementor_activate": ["/usr/bin/sudo", "/usr/local/libexec/tenant-elementor-activate"]
}
```

The canonical replacement is `status` plus `operations`, as shown in `examples/private-policy.template.json`. Translation does not add a command, plugin, or permission. A legacy running host may continue to use its existing client. A new client can reach that unmodified host only with:

```bash
export TENANT_GATEWAY_API_STYLE=host-gateway-v1
python3 tenantctl.py run plugin-elementor-update
```

After proving the canonical policy on staging, change the access mode to `host-gateway`. Keep the old policy backup until the public site and the authorization tests pass.

## Rollback

Rollback is the prior verified program/plugin version plus the prior private policy. Do not roll back by widening sudoers, disabling token checks, granting WordPress Administrator, or making a Drive link public.

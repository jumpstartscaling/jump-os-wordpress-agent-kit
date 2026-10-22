# Versioning and compatibility policy

## Versioning

This project follows [Semantic Versioning](https://semver.org/). Until `1.0.0`, a minor release may contain a documented breaking change; each such change must include an upgrade guide and a compatibility assessment. `1.0.0` will not be declared until the published compatibility program has reproducible evidence for each claimed installation class.

## Stable contracts

The following are public contracts:

- the private handoff environment variable names;
- `tenantctl.py` exit-code behavior and JSON output shape where documented;
- Host Gateway `/v1/status`, `/v1/capabilities`, and named-operation semantics;
- WordPress Bridge REST namespace and authorization behavior;
- no arbitrary command, plugin path, or request argument acceptance.

## Compatibility rules

1. Add a capability; do not change the meaning of an existing capability.
2. Keep a deprecated contract working for at least one minor release after its replacement, unless a security defect requires immediate removal.
3. Document the old form, replacement, removal target, migration steps, and rollback path in `docs/UPGRADING.md`.
4. A security fix may remove unsafe behavior immediately; the release notes must explain the impact.
5. Never silently broaden a recipient token, WordPress role, or host wrapper while preserving an interface name.

## Current migrations

| Legacy contract | Canonical contract | Support status |
| --- | --- | --- |
| Host policy `actions.status`, `actions.elementor_update`, `actions.elementor_activate` | `status` plus named `operations` | Supported by the gateway translation layer. |
| Host Gateway `elementor/update` and `elementor/activate` route shape | `operations/plugin-elementor-update` and `operations/plugin-elementor-activate` | Use `TENANT_GATEWAY_API_STYLE=host-gateway-v1` for an unchanged v0.1 host. |

Do not rename a tenant, change an endpoint, or rotate credentials as part of a software upgrade unless the owner explicitly chose that separate action.

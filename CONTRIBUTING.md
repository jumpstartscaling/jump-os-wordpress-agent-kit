# Contributing

Thank you for helping make WordPress access safer for people and agents.

## Contribution lanes

- **Compatibility evidence:** report a tested provider, WordPress deployment form, and agent runtime through the compatibility issue form.
- **Documentation:** clarify install, rollback, or agent instructions without adding unsupported provider claims.
- **Adapter/code:** add an isolated adapter or capability with tests, threat-model notes, upgrade behavior, and a rollback path.

## Required contribution standards

1. Preserve tenant isolation; never add arbitrary command, path, SQL, container, or plugin selection from network input.
2. Do not add real credentials, customer URLs, server paths, or private handoff artifacts.
3. Add or update a discriminating test for behavioral changes.
4. Update `VERSIONING.md`, `docs/UPGRADING.md`, and release notes when a public contract changes.
5. State the evidence level: documented-only, local reproducible test, provider sandbox verified, or production verified with anonymized evidence.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile gateway/tenant_gateway.py client/tenantctl.py scripts/build_recipient_pack.py scripts/build_wordpress_bridge_zip.py
php -l wordpress-plugin/jump-os-wordpress-agent-bridge/jump-os-wordpress-agent-bridge.php
git diff --check
```

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

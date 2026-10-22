# Recipient handoff

Build a private package after the host boundary and WordPress Editor account have passed their tests:

```bash
python3 scripts/build_recipient_pack.py \
  --output private/tenant-access.zip \
  --tenant-label "Client tenant" \
  --access-mode host-gateway \
  --gateway-endpoint "https://client.example/__tenant-gateway" \
  --gateway-token-file private/gateway-token.txt \
  --wordpress-url "https://client.example" \
  --wordpress-username "content-operator" \
  --wordpress-dashboard-password-file private/wordpress-dashboard-password.txt \
  --wordpress-application-password-file private/wordpress-app-password.txt
```

The generated ZIP contains live credentials. Upload it only to a Drive folder whose sharing list has been reviewed for the intended recipient. It is not appropriate for a public GitHub release.

For the WordPress Bridge, use `--access-mode wordpress-bridge` and set `--gateway-endpoint` to `https://client.example/wp-json/jump-os-agent/v1`. The package is agent-neutral: it includes `AGENTS.md`, `tenantctl.py`, and the guides under `agent-guides/`. For a cloud agent, store the gateway token and WordPress application password as that recipient's private secrets, not in a repository. For Codex Cloud specifically, shared environments share required secrets rather than another person's personal secret values; configure only the canonical WordPress site domain as an additional permitted domain.

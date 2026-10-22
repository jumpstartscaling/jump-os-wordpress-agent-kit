# Recipient handoff

Build a private package after the host boundary and WordPress Editor account have passed their tests:

```bash
python3 scripts/build_recipient_pack.py \
  --output private/tenant-access.zip \
  --tenant-label "Client tenant" \
  --gateway-endpoint "https://client.example/__tenant-gateway" \
  --gateway-token-file private/gateway-token.txt \
  --wordpress-url "https://client.example" \
  --wordpress-username "content-operator" \
  --wordpress-application-password-file private/wordpress-app-password.txt
```

The generated ZIP contains live credentials. Upload it only to a Drive folder whose sharing list has been reviewed for the intended recipient. It is not appropriate for a public GitHub release.

The package is agent-neutral: it includes `AGENTS.md`, `tenantctl.py`, and the guides under `agent-guides/`. For a cloud agent, store the gateway token and WordPress application password as that recipient's private secrets, not in a repository. For Codex Cloud specifically, shared environments share required secrets rather than another person's personal secret values; configure the tenant gateway as the only additional permitted domain.

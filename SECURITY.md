# Security policy

## Supported versions

The latest tagged release and the `main` branch receive security fixes. Earlier releases are supported only when their release notes say so.

## Report a vulnerability privately

Do not open a public issue for a suspected token leak, authorization bypass, arbitrary command/path execution, cross-tenant access, WordPress privilege escalation, or private package exposure.

Use GitHub's **Report a vulnerability** flow in this repository's Security tab. Include a minimal reproduction, affected version or commit, adapter type, and impact. Do not attach real tenant URLs, tokens, credentials, database dumps, or customer content.

If GitHub private reporting is unavailable to you, contact the repository owner through the GitHub profile and ask for a private disclosure channel. Public issues are appropriate only after a fix is released and the maintainer agrees on disclosure.

## Security design commitments

- no raw tokens, dashboard passwords, application passwords, or provider credentials in the repository, issues, release assets, or examples;
- no arbitrary shell, database, plugin-path, filesystem, or container operation from a recipient request;
- least-privilege WordPress roles and separate content versus maintenance credentials;
- revocation instructions in every private handoff package;
- security fixes may remove an unsafe compatibility behavior immediately.

## Response targets

The project aims to acknowledge a credible private report within five business days, assess severity before discussing public disclosure, and publish a mitigation or status update as soon as a fix path is known. These are project targets, not an SLA.

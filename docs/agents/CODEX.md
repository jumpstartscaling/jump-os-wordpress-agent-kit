# Codex

## Local Codex

Open the private recipient package as a project. Codex local environments can keep shared project setup in `.codex/`; do not check in the package `.env`. Run `python3 tenantctl.py capabilities` before asking Codex to work.

## Codex Cloud

Create a separate cloud environment from the public repository or a private recipient repository. Add the tenant gateway host as the only custom destination required for maintenance. Put the recipient's gateway token and WordPress application password in that person's private secrets, not in shared repository files. Codex Cloud tasks start in isolated workspaces, so repository access alone does not grant host access.

Use a prompt such as: “Read AGENTS.md. Work only on the named tenant. First call capabilities and status. Do not attempt SSH, Docker, filesystem, or any route not listed by the gateway.”

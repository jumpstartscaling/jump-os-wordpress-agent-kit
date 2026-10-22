# Agent runtime compatibility

This kit supports an agent only when its runtime can enforce the same tenant boundary a human would follow. The model name is not the security boundary; credential handling, filesystem scope, network egress, and tool approval are.

## The three runtime classes

| Runtime class | Examples | Can receive the private package? | Recommended access |
| --- | --- | --- | --- |
| Local terminal agent | Codex local, Claude Code, Cursor local, Cline, Roo Code, Continue, Aider, OpenCode, Gemini CLI, GitHub Copilot CLI, Windsurf local | Yes, in a dedicated private workspace on a trusted computer | Source `.env` only in that workspace; use `tenantctl.py` and WordPress Editor credentials only for the named site. |
| Isolated cloud coding agent | Codex Cloud, GitHub Copilot coding agent, provider-hosted background agents | Only when the platform supports repository-scoped secrets, isolated execution, and an explicit egress allowlist | Put secrets in that agent's own secret store; allow only the canonical site or named gateway host. |
| Browser/chat-only assistant | Standard ChatGPT, Claude, Gemini, or similar web chat without an approved tool runtime | No | Use for planning, copy, review, or human-executed instructions only. Never paste a private package or token into a normal conversation. |

## Universal setup for a local agent

1. Download the private package into a new, access-controlled workspace—not the public repository and not a synced shared folder.
2. Read `AGENTS.md` before any action. It is the cross-agent authority file.
3. Load secrets only for the active shell session: `set -a; source .env; set +a`.
4. Run `python3 tenantctl.py capabilities` and `python3 tenantctl.py status` first.
5. Use `python3 tenantctl.py run CAPABILITY-ID` only when the owner requested that exact capability.
6. Keep WordPress dashboard passwords for interactive dashboard login only; use application passwords only in a REST client.
7. Revoke the package’s access immediately if it is copied, attached, or pasted to an unapproved place.

The generated package includes ready-to-read instruction files for common project conventions: `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/`, and `.windsurfrules`. They restate the same boundary; they do not contain secrets.

## Cloud-agent rules

### Codex Cloud

Use a dedicated environment and the recipient's own private secrets. Restrict egress to the one canonical WordPress site for Native REST/Bridge mode or the one named Host Gateway. Shared environments do not automatically convey another person’s personal secret values. [OpenAI Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)

### GitHub Copilot coding agent

Use the repository’s dedicated **Agents** secrets, not Actions, Codespaces, or Dependabot secrets. GitHub documents that the cloud agent runs in an ephemeral environment and has its own secret class; scope a tenant secret only to the one private access repository that needs it. [GitHub Copilot cloud-agent secrets](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/configure-secrets-and-variables)

### Other hosted/background agents

Before giving direct access, verify all four controls in the provider’s current documentation: per-project secret storage, isolated runtime, visible network egress policy, and a way to prevent secrets from entering prompts/logs. If any control is absent or unclear, treat it as browser/chat-only and keep execution with a human or a local agent.

## Local-agent notes

- **Claude Code:** run in the dedicated package directory; do not use broad additional working directories or permission-bypass modes. Anthropic documents that `--add-dir` broadens accessible directories and `--dangerously-skip-permissions` skips prompts. [Claude Code CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage)
- **Gemini CLI:** use the package directory as the project root and keep the private `.env` local. Gemini CLI supports project configuration and environment loading, so ensure its project root does not include a parent directory containing unrelated secrets. [Gemini CLI configuration](https://geminicli.com/docs/reference/configuration/)
- **Editor agents:** Cursor, Cline, Roo Code, Continue, Windsurf, and VS Code-based agents should open only the recipient package as their workspace. Do not configure host SSH, Docker, broad shell profiles, or unrelated repository folders.

## What agents may and may not do

| Action | Native REST | WordPress Bridge | Host Gateway |
| --- | --- | --- | --- |
| Plan/review/copy | Yes | Yes | Yes |
| Edit pages/media as a WordPress Editor | Yes | Yes | Yes, through the separate WordPress role |
| Read allowlisted plugin status | No, unless WordPress role/API exposes it | Yes | Yes |
| Activate exact preconfigured plugin | No | Yes, with operator token | Yes, if capability exists |
| Update plugin with proven backup | Provider/human flow | No | Yes, only when the named wrapper verifies backup |
| SSH, Docker, database, hosting panel, sibling tenant | Never | Never | Never for package recipient |

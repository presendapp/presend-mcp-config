# Connect Presend's MCP Server to Your AI Client

Presend's MCP server (`https://presend.pages.dev/mcp`, Streamable HTTP, no signup, no API key) works with any MCP-compatible client. This repo has exact, per-client setup instructions.

**Only want the dependency checks?** Use `https://presend.pages.dev/mcp-deps` instead: the same server limited to the five tools an agent needs before installing an npm or PyPI package (`supply_chain_check`, `typosquat_check`, `maintainer_change_check`, `vulnerability_check`, `repo_health_check`). Fewer tools make it easier for the model to pick the right one. Replace the URL in any example below.

**If you write code**, see [presend-examples](https://github.com/presendapp/presend-examples) instead -- runnable Python for LangChain, CrewAI, LlamaIndex, OpenAI Agents SDK, and Google ADK.

**If you use an app** (Claude Desktop, Cursor, Windsurf, VS Code), this repo is for you.

## Important: use each app's own "Add MCP Server" UI when it has one

MCP config field names (`url` vs `serverUrl`, `type` vs `transport`) genuinely differ between apps and change between versions. Rather than hand-editing JSON and risking a typo, use each app's built-in form -- it always writes the correct format for whatever version you're running. JSON snippets are included below as a fallback for apps without a UI, or if you prefer editing config files directly.

| Client | Guide | Method |
|---|---|---|
| Claude (claude.ai, Desktop, mobile) | [claude-desktop.md](claude-desktop.md) | Settings → Connectors (paid plans) |
| Claude Code (CLI) | [claude-code.md](claude-code.md) | One command |
| Cursor | [cursor.md](cursor.md) | Settings UI or JSON |
| Windsurf | [windsurf.md](windsurf.md) | Settings UI or JSON |

## Claude (claude.ai, Desktop, mobile): add it as a connector

On Pro, Max, Team and Enterprise plans, Claude adds remote MCP servers from **Settings → Connectors → Add custom connector** ([Anthropic's guide](https://support.claude.com/en/articles/11503834-building-custom-connectors-via-remote-mcp-servers)). No bridge and no config file.

It is also listed in Claude's connector directory as a Community connector: [Presend package checks](https://claude.ai/directory/connectors/presend-package-checks).

1. Name: `Presend package checks`. URL: `https://presend.pages.dev/mcp-deps`.
2. Authentication: **No connection** (open server, no account, no API key).
3. Claude lists the five tools as read-only.

Then try:

- *"Before I run npm install expres, check that package."* `expres` is flagged as a near-miss of `express`.
- *"Is the PyPI package reqeusts safe to install?"* The name does not exist on PyPI.
- *"Check lodash 4.17.15 on npm for known vulnerabilities."* 6 OSV.dev advisories, with the fixed versions.

Tested on 5 October 2026 in Claude (Pro plan) with `/mcp-deps`.

Limits: Presend is not a malware scanner; the typosquat check compares names against a list of popular packages; a clean result does not prove a package is safe; per-minute rate limits apply. Data: the tools receive only the package names, versions and repository names you ask about, which Presend passes to npm, PyPI, OSV.dev and GitHub ([privacy policy](https://presend.pages.dev/privacy)).

## ⚠️ Claude Desktop config file: known bug

As of writing, some Claude Desktop versions have a **data-loss bug**: adding a remote MCP server directly via a `url` field in `claude_desktop_config.json` can silently wipe your *entire* existing `mcpServers` section (and some other settings) on the next app restart, with no error shown. This is reported behavior, not something we've been able to independently verify by running the app ourselves.

This only concerns editing that file by hand. On paid plans, add Presend from Settings → Connectors instead (section above). If you do edit the file, use the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) bridge: see [claude-desktop.md](claude-desktop.md) for the exact config. It's one extra line and avoids the risk.

## Verify it worked

Once connected, ask your AI assistant: *"What tools do you have from Presend?"* -- it should list tools like `whois_lookup`, `vulnerability_check`, `maintainer_change_check`. Then try: *"Use Presend to check if the npm package lodash has a suspicious maintainer change."*

## For teams

We are testing a paid offer for teams: the same dependency checks on every pull request that changes a dependency and for AI coding agents before they install a package, with false-positive rates measured and published. Nothing is for sale yet. If your team would use it, [join the waitlist](https://presend.pages.dev/teams).

## What is Presend?

A free security/utility API and MCP server, no signup, no API key. [presend.pages.dev](https://presend.pages.dev) · [Main repo](https://github.com/presendapp/presend-source)

## Claude Code and Cursor: check packages before the agent installs them

A hook blocks `npm install` / `pip install` of a name that does not exist on the registry and asks you to confirm a package that is new, close to a popular name or vulnerable: see [claude-code.md](claude-code.md#check-packages-before-claude-code-installs-them) and [cursor.md](cursor.md#check-packages-before-cursors-agent-installs-them) (Cursor reliably enforces only the block).

## License

MIT

# Claude (claude.ai, Desktop, mobile)

## Recommended: add it as a connector (paid plans)

On Pro, Max, Team and Enterprise plans, Claude adds remote MCP servers from **Settings → Connectors → Add custom connector** ([Anthropic's guide](https://support.claude.com/en/articles/11503834-building-custom-connectors-via-remote-mcp-servers)). No bridge and no config file.

1. Name: `Presend package checks`. URL: `https://presend.pages.dev/mcp-deps` (or `https://presend.pages.dev/mcp` for all 40 tools).
2. Authentication: **No connection** (open server, no account, no API key).
3. Claude lists the tools as read-only.

Then try: *"Before I run npm install expres, check that package."*

Tested on 5 October 2026 in Claude (Pro plan) with `/mcp-deps`. More examples and limits: [README](README.md#claude-claudeai-desktop-mobile-add-it-as-a-connector).

## Free plan or config file: mcp-remote bridge

⚠️ **Read the warning in the main README first**: some Claude Desktop versions have a bug that can wipe your MCP config if you add a remote server directly in `claude_desktop_config.json`. The bridge below avoids it.

Requires [Node.js](https://nodejs.org) installed.

1. Open Claude Desktop → Settings → Developer → Edit Config
2. This opens `claude_desktop_config.json`. Add:

```json
{
  "mcpServers": {
    "presend": {
      "command": "npx",
      "args": ["mcp-remote", "https://presend.pages.dev/mcp-deps"]
    }
  }
}
```

If you already have other servers listed under `mcpServers`, add `"presend": {...}` as an additional entry, don't replace the whole file.

3. Restart Claude Desktop.
4. Ask Claude: *"What tools do you have from Presend?"*

This spawns a small local process that bridges Claude Desktop's stdio-based connector to Presend's remote HTTP server.

Not independently tested by us against a live Claude Desktop install: this is the documented `mcp-remote` usage pattern, not something we ran ourselves.

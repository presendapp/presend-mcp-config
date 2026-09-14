# Claude Desktop

⚠️ **Read the warning in the main README first** -- some versions have a bug that can wipe your MCP config if you add a remote server directly.

## Safe method: mcp-remote bridge

Requires [Node.js](https://nodejs.org) installed.

1. Open Claude Desktop → Settings → Developer → Edit Config
2. This opens `claude_desktop_config.json`. Add:

```json
{
  "mcpServers": {
    "presend": {
      "command": "npx",
      "args": ["mcp-remote", "https://presend.pages.dev/mcp"]
    }
  }
}
```

If you already have other servers listed under `mcpServers`, add `"presend": {...}` as an additional entry, don't replace the whole file.

3. Restart Claude Desktop.
4. Ask Claude: *"What tools do you have from Presend?"*

This spawns a small local process that bridges Claude Desktop's stdio-based connector to Presend's remote HTTP server -- not as direct as a native connection, but avoids the bug entirely.

Not independently tested by us against a live Claude Desktop install -- this is the documented `mcp-remote` usage pattern, not something we ran ourselves. If it doesn't work for your version, check [Anthropic's own MCP docs](https://docs.claude.com) for the current recommended method.

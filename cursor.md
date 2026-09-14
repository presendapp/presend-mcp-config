# Cursor

## Recommended: Settings UI

1. Open Cursor Settings (`Cmd+,` / `Ctrl+,`)
2. Go to **Tools & MCP** (or **Features → MCP** on older versions)
3. Click **+ New MCP Server** / **+ Add New MCP Server**
4. Name: `presend`. Transport: `streamable-http` (or `sse` if that's the only remote option shown). URL: `https://presend.pages.dev/mcp`
5. Save, then fully quit and restart Cursor -- MCP servers only load at startup.

## Alternative: edit mcp.json directly

`.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "presend": {
      "url": "https://presend.pages.dev/mcp",
      "type": "streamable-http"
    }
  }
}
```

Some Cursor versions use `"transport"` instead of `"type"` as the field name -- if the server doesn't connect, try switching to `"transport": "streamable-http"`, or just use the Settings UI instead, which always matches your installed version.

Verify: green dot next to `presend` in Settings → Tools & MCP means it's connected.

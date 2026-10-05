# Windsurf

For remote servers, Windsurf's documentation uses `serverUrl` in its examples and accepts `serverUrl` or `url` ([Windsurf MCP docs](https://docs.windsurf.com/windsurf/cascade/mcp), checked on 5 October 2026). The simplest route is Windsurf's own MCP settings UI.

## Config file

`~/.codeium/windsurf/mcp_config.json` (note: `.codeium/windsurf/`, not `.windsurf/`):

```json
{
  "mcpServers": {
    "presend": {
      "serverUrl": "https://presend.pages.dev/mcp"
    }
  }
}
```

Save, then reload the server from Windsurf's MCP panel (or restart the app).

To expose only the five dependency-check tools, use `https://presend.pages.dev/mcp-deps` instead.

Not independently tested by us against a live Windsurf install -- this is the documented config format, not something we ran ourselves.

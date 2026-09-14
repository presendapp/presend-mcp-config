# Windsurf

Windsurf uses a **different field name** than Cursor for the same thing -- `serverUrl`, not `url`. Copying a Cursor config as-is will silently fail with no error.

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

Not independently tested by us against a live Windsurf install -- this is the documented config format, not something we ran ourselves.

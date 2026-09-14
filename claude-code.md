# Claude Code (CLI)

Claude Code's CLI supports remote Streamable HTTP servers natively -- no bridge needed.

## One command

```bash
claude mcp add presend --type http --url https://presend.pages.dev/mcp
```

## Or edit the config file directly

`.mcp.json` (project-level) or `~/.claude.json` (user-level):

```json
{
  "mcpServers": {
    "presend": {
      "type": "http",
      "url": "https://presend.pages.dev/mcp"
    }
  }
}
```

`streamable-http` also works as an alias for `http` in the `type` field.

Verify with `claude mcp list` -- `presend` should show as connected.

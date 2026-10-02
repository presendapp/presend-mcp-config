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
      "url": "https://presend.pages.dev/mcp"
    }
  }
}
```

A remote server only needs `url` ([Cursor MCP docs](https://cursor.com/docs/mcp)). If it does not connect, use the Settings UI above, which always matches your installed version.

Verify: green dot next to `presend` in Settings → Tools & MCP means it's connected.

## Check packages before Cursor's agent installs them

The script used for Claude Code, [`hooks/presend_preinstall.py`](hooks/presend_preinstall.py) (Python 3.8+, standard library only), also works as a Cursor `beforeShellExecution` hook. Copy it to `.cursor/hooks/presend_preinstall.py` in your project and add `.cursor/hooks.json`:

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      {
        "command": "python3 .cursor/hooks/presend_preinstall.py",
        "matcher": "npm|pnpm|yarn|bun|npx|bunx|pip|uv|poetry|pipx|python",
        "timeout": 150
      }
    ]
  }
}
```

The `matcher` limits the hook to commands that may install a package; the script ignores everything else. For each package named on an install command it asks Presend's supply-chain check:

| Presend verdict | Hook response |
|---|---|
| The name does not exist on npm or PyPI (`package_not_found`) | `deny`: the command is blocked, with the reason |
| First published less than 30 days ago, close to a popular name, known vulnerabilities in the requested version, recent publisher change (npm), or archived repository | `ask`, or `deny` with `PRESEND_HOOK_STRICT=1` |
| No signal, or not an install command | `allow` |

**Cursor reliably enforces `deny`, not `ask`.** According to [Cursor's team on its forum](https://forum.cursor.com/t/the-cursor-hooks-did-not-execute-as-expected/155711/4) (September 2026), a hook's `allow` never auto-approves a command (your own approval settings still apply), but `ask` may not prompt, in particular when commands run automatically. To make the warnings stop the command, block instead of asking:

```json
"command": "PRESEND_HOOK_STRICT=1 python3 .cursor/hooks/presend_preinstall.py"
```

New or suspicious packages are then blocked with the reason, and you can install them yourself after checking.

What is sent, what is checked and the limits are the same as for Claude Code: see [claude-code.md](claude-code.md#check-packages-before-claude-code-installs-them).

**Try it without Cursor:**

```bash
echo '{"hook_event_name":"beforeShellExecution","command":"npm install presend-nonexistent-name-20261002"}' | python3 .cursor/hooks/presend_preinstall.py
```

It prints `{"permission": "deny", ...}`. Tested with hook input in the format documented by Cursor, against the live API; not yet in a live Cursor session. If it behaves differently there, please open an issue.

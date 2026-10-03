# Claude Code (CLI)

Claude Code's CLI supports remote Streamable HTTP servers natively -- no bridge needed.

## One command

```bash
claude mcp add --transport http presend https://presend.pages.dev/mcp
```

To expose only the five dependency-check tools:

```bash
claude mcp add --transport http presend-deps https://presend.pages.dev/mcp-deps
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

## Check packages before Claude Code installs them

The MCP tool `supply_chain_check` only helps when the agent decides to call it. A **PreToolUse hook** runs the check every time Claude Code is about to run an install command, whatever the agent decides.

[`hooks/presend_preinstall.py`](hooks/presend_preinstall.py) (Python 3.8+, standard library only) reads the command Claude Code is about to run. For `npm`, `pnpm`, `yarn` and `bun` install or add, `npx`, `bunx` and `dlx`, `pip`, `pip3` and `python -m pip`, `uv add` and `uv pip install`, `poetry add`, `pipx` and `uvx`, it asks Presend's supply-chain check about each package named on the command line:

| Presend verdict | Hook decision |
|---|---|
| The name does not exist on npm or PyPI (`package_not_found`) | **deny**: the command is blocked and Claude is told why |
| First published less than 30 days ago, close to a popular name, known vulnerabilities in the requested version, recent publisher change (npm), or archived repository | **ask**: you confirm or refuse, with the reasons shown |
| No signal | nothing: the normal permission flow applies |
| Presend unreachable, or a check could not run | nothing by default; set `PRESEND_HOOK_FAIL_CLOSED=1` to be asked instead |

To block instead of asking, set `PRESEND_HOOK_STRICT=1`. The same script also works as a Cursor hook: see [cursor.md](cursor.md#check-packages-before-cursors-agent-installs-them).

**Setup.** Copy the script to `.claude/hooks/presend_preinstall.py` in your project, then add this to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/presend_preinstall.py"],
            "timeout": 150
          }
        ]
      }
    ]
  }
}
```

Committed to the repository, the hook applies to everyone who opens the project in Claude Code. Cloud sessions run project hooks too; allow `presend.pages.dev` in the environment's network settings, otherwise the check cannot reach Presend and the install goes ahead.

**What is sent.** Package names, plus the version when the command pins an exact one (`lodash@4.17.21`, `requests==2.32.3`), to `presend.pages.dev`. Never your code or files.

**Limits.** It is a triage signal before installing, not a malware scanner. Only names written on the command line are checked: installs from a lockfile, a `requirements.txt` (`-r`), a local path or a git URL are not. A name invented by a model and registered more than 30 days ago passes. The API is free with per-minute rate limits; at most 8 packages per command are checked and the rest are reported as not checked. If the hook times out, Claude Code lets the command run.

**Try it without Claude Code:**

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"npm install presend-nonexistent-name-20261002"}}' | python3 .claude/hooks/presend_preinstall.py
```

It prints a `deny` decision. The command parsing has its own tests: `python3 hooks/test_extract.py`.

Tested with hook input in the format documented by Anthropic, against the live API; not yet in a live Claude Code session. If it behaves differently there, please open an issue.

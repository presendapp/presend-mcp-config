#!/usr/bin/env python3
"""Presend pre-install check for Claude Code (PreToolUse hook on the Bash tool).

Before Claude Code runs `npm install <pkg>`, `pip install <pkg>` and similar commands, this hook asks
Presend's supply-chain check about each named package:
- a name that does not exist on npm or PyPI: the command is denied (the name may be invented by a model);
- a package first published less than 30 days ago, a likely typosquat, known vulnerabilities of the
  version, a recent publisher change (npm) or an archived repository: you are asked to confirm;
- otherwise the hook stays silent and the normal permission flow applies.

Only package names (and an exact version when one is given) are sent to presend.pages.dev, never your code.
If Presend cannot be reached, the install goes ahead; set PRESEND_HOOK_FAIL_CLOSED=1 to be asked instead.
Free API, per-minute rate limits apply. Not a malware scanner. Python 3.8+, standard library only. MIT.
"""
import json, os, re, shlex, sys, urllib.parse, urllib.request

API = os.environ.get("PRESEND_API", "https://presend.pages.dev/api/supply-chain-check")
UA = "presend-claude-hook/1 (+https://github.com/presendapp/presend-mcp-config)"
MAX_PACKAGES = 8
SEP = re.compile(r"&&|\|\||;|\||\n")
VALUE_FLAGS = {"-r", "--requirement", "-c", "--constraint", "-e", "--editable", "-i", "--index-url",
               "--extra-index-url", "-f", "--find-links", "-t", "--target", "--prefix", "--root",
               "--registry", "-w", "--workspace", "--cache", "--python", "--group", "-G", "--filter",
               "--dir", "-C", "--cwd", "--source"}
NPM_VERSION = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?")

def strip_prefix(t):
    while t and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t[0]) or t[0] in ("sudo", "command", "exec", "time", "nohup")):
        t = t[1:]
    return t

def classify(t):
    """(ecosystem, args, first_positional_only) for an install-like command, else None."""
    if len(t) >= 3 and re.fullmatch(r"python[0-9.]*|py", t[0]) and t[1] == "-m" and t[2] in ("pip", "pip3"):
        t = ["pip"] + t[3:]
    head = t[0].rsplit("/", 1)[-1]
    if head in ("pip", "pip3") and t[1:2] == ["install"]: return "pypi", t[2:], False
    if head == "uv" and t[1:3] == ["pip", "install"]: return "pypi", t[3:], False
    if head == "uv" and t[1:2] == ["add"]: return "pypi", t[2:], False
    if head == "poetry" and t[1:2] == ["add"]: return "pypi", t[2:], False
    if head == "pipx" and t[1:2] in (["install"], ["run"]): return "pypi", t[2:], t[1] == "run"
    if head == "uvx": return "pypi", t[1:], True
    if head in ("npm", "pnpm", "yarn", "bun") and t[1:2] in (["install"], ["i"], ["add"]): return "npm", t[2:], False
    if head in ("npx", "bunx"): return "npm", t[1:], True
    if head in ("pnpm", "yarn") and t[1:2] == ["dlx"]: return "npm", t[2:], True
    if head == "npm" and t[1:2] in (["exec"], ["x"]): return "npm", t[2:], True
    return None

def is_spec(a):
    return not (a.startswith((".", "/", "~")) or "://" in a or a.endswith((".whl", ".tar.gz", ".tgz", ".zip"))
                or a.startswith(("git+", "github:", "file:", "link:", "workspace:")))

def parse_npm(a):
    m = re.fullmatch(r"(@[a-z0-9][\w.~-]*/[a-z0-9][\w.~-]*|[a-z0-9][\w.~-]*)(?:@(.*))?", a, re.I)
    if not m: return None
    v = m.group(2)
    return m.group(1), (v if v and NPM_VERSION.fullmatch(v) else None)

def parse_pypi(a):
    m = re.match(r"([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)(\[[^\]]*\])?(.*)$", a)
    if not m: return None
    pin = re.fullmatch(r"==\s*([0-9][0-9A-Za-z.+!-]*)\s*(?:;.*)?", m.group(3).strip())
    return m.group(1), (pin.group(1) if pin else None)

def extract(command):
    found, seen = [], set()
    for seg in SEP.split(command or ""):
        try:
            t = strip_prefix(shlex.split(seg))
        except ValueError:
            continue
        c = classify(t) if t else None
        if not c: continue
        eco, args, first_only = c
        skip = False
        for a in args:
            if skip:
                skip = False; continue
            if a in (">", ">>", "<", "2>", "&>") or a.startswith((">", "<", "2>", "&>")): break
            if a.startswith("-"):
                skip = a in VALUE_FLAGS; continue
            p = (parse_npm(a) if eco == "npm" else parse_pypi(a)) if is_spec(a) else None
            if p and (eco, p[0].lower()) not in seen:
                seen.add((eco, p[0].lower())); found.append((eco, p[0], p[1]))
            if first_only: break
    return found

def check(eco, name, version):
    q = {"ecosystem": eco, "package": name}
    if version: q["version"] = version
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": UA, "Accept": "application/json"})
    if os.environ.get("PRESEND_TEST") == "1": req.add_header("X-Presend-Test", "1")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception as e:
        return {"overall_risk": "unreachable", "error": str(e)[:120]}

def reasons(d):
    flags, checks, out = d.get("flags") or [], d.get("checks") or {}, []
    if "new_package" in flags:
        out.append(d.get("age_note") or "first published %s days ago" % d.get("package_age_days"))
    if "possible_typosquat" in flags:
        sim = [s.get("name") for s in (checks.get("typosquat") or {}).get("similar_to") or []][:3]
        out.append("name close to " + ", ".join(sim) if sim else "possible typosquat")
    if "known_vulnerabilities" in flags:
        n = len((checks.get("vulnerability") or {}).get("vulnerabilities") or [])
        out.append("%d known vulnerabilit%s in version %s" % (n, "y" if n == 1 else "ies", d.get("version_checked")))
    if "maintainer_change" in flags: out.append("recent change of publisher after a long dormancy (npm)")
    if "repo_archived" in flags: out.append("source repository is archived")
    return out

def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    if event.get("tool_name") != "Bash": return 0
    pkgs = extract((event.get("tool_input") or {}).get("command"))
    if not pkgs: return 0
    deny, ask, unchecked = [], [], [n for _, n, _ in pkgs[MAX_PACKAGES:]]
    for eco, name, ver in pkgs[:MAX_PACKAGES]:
        d = check(eco, name, ver)
        label = "%s%s (%s)" % (name, (("@" if eco == "npm" else "==") + ver) if ver else "", "npm" if eco == "npm" else "PyPI")
        risk = d.get("overall_risk")
        if risk == "package_not_found":
            deny.append(label + ": does not exist; the name may be invented. Check it against the project's own documentation.")
        elif risk == "review_recommended":
            ask.append(label + ": " + "; ".join(reasons(d) or ["review recommended"]))
        elif risk != "no_signals_found":
            unchecked.append(label)
    if deny:
        decision, lines = "deny", deny + ask
    elif ask or (unchecked and os.environ.get("PRESEND_HOOK_FAIL_CLOSED") == "1"):
        decision, lines = "ask", ask
    else:
        return 0
    if unchecked: lines = lines + ["not checked: " + ", ".join(unchecked)]
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                             "permissionDecisionReason": "Presend pre-install check: " + " | ".join(lines)}}))
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)

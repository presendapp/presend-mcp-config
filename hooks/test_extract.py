from presend_preinstall import extract
cases = [
 ("npm install expres", [("npm", "expres", None)]),
 ("npm i -D @types/node@20.1.0 lodash", [("npm", "@types/node", "20.1.0"), ("npm", "lodash", None)]),
 ("cd app && pnpm add react@^18 --save", [("npm", "react", None)]),
 ("pip install requests==2.19.0 'uvicorn[standard]>=0.30'", [("pypi", "requests", "2.19.0"), ("pypi", "uvicorn", None)]),
 ("python3 -m pip install -r requirements.txt flask", [("pypi", "flask", None)]),
 ("uv add httpx", [("pypi", "httpx", None)]),
 ("npx -y create-vite@5.2.0 my-app", [("npm", "create-vite", "5.2.0")]),
 ("npm install", []),
 ("npm install ./local-pkg git+https://example.com/x.git", []),
 ("npm install lodash > install.log 2>&1", [("npm", "lodash", None)]),
 ("ls -la; echo npm install x", []),
 ("FOO=1 sudo pip3 install pikobs", [("pypi", "pikobs", None)]),
 ("pip install --index-url https://example.com/simple simple-pkg", [("pypi", "simple-pkg", None)]),
]
bad = 0
for cmd, exp in cases:
    got = extract(cmd)
    ok = got == exp; bad += not ok
    print(("OK   " if ok else "ECHEC") + " " + cmd + ("" if ok else "\n      attendu %s\n      obtenu  %s" % (exp, got)))
print("%d/%d" % (len(cases) - bad, len(cases))); raise SystemExit(1 if bad else 0)

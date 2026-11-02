"""Shared helpers: send one chat request to a Strata server, read the speeds from the engine log."""
import json, os, re, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results", "strata")
STAT = re.compile(r"prompt (\d+) tokens(?: = (\d+) reused)? \+ (\d+) read in (\d+) ms \(([\d.]+) tok/s\), "
                  r"(\d+) generated in (\d+) ms \(([\d.]+) tok/s\)")
DRAFTS = re.compile(r"drafts accepted (\d+) of (\d+)")


def ask(port, log, prompt, max_tokens, timeout=3600):
    """One request at temperature 0, thinking off. Returns the engine's own numbers for that request."""
    body = {"model": "x", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens,
            "temperature": 0, "reasoning_effort": "none"}
    req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    n0 = sum(1 for _ in open(log, errors="ignore"))
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=timeout))
    except Exception as e:  # a 503 is a result too
        return {"error": f"{type(e).__name__}: {e}"[:200], "wall": round(time.time() - t, 1)}
    wall = round(time.time() - t, 1)
    time.sleep(1)
    lines = [l for l in open(log, errors="ignore").read().splitlines()[n0:] if "prompt " in l and " tokens" in l]
    m = STAT.search(lines[-1]) if lines else None
    a = DRAFTS.search(lines[-1]) if lines else None
    out = {"wall": wall, "text": r["choices"][0]["message"]["content"]}
    if m:
        out |= {"pp_tok": int(m[1]), "reused": int(m[2] or 0), "pp": float(m[5]), "pp_ms": int(m[4]),
                "tg_n": int(m[6]), "tg": float(m[8])}
    if a:
        out["drafts"] = f"{a[1]}/{a[2]}"
    return out


def save(label, kind, res):
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, f"{label}-{kind}-{time.strftime('%Y%m%d-%H%M')}.json")
    json.dump(res, open(path, "w"), indent=1)
    print("saved", path)

"""Write speed: three long, deterministic generations (prose, new code, rewrite of a file), 700 tokens max,
a random nonce per request so the prompt cache never helps. Median of R passes.

    python3 bench_decode.py <port> <engine.log> <label> [--reps 3]
"""
import os, statistics, sys, uuid
from _common import HERE, ask, save

PORT, LOG, LABEL = int(sys.argv[1]), sys.argv[2], sys.argv[3]
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 3
SRC = open(os.path.join(HERE, "rewrite-source.py"), encoding="utf-8").read()
TESTS = {
    "prose": "Write a detailed essay of about 600 words on the history of the printing press in Europe, "
             "in plain paragraphs, no headings.",
    "code": "Write a complete Python module (about 150 lines) implementing an LRU cache with TTL expiry, "
            "thread safety, statistics counters and a small CLI demo. Output only the code in one ```python block.",
    "rewrite": "Rewrite the whole file below, unchanged except for one thing: rename the function `ask` to "
               "`ask_strata` everywhere. Output only the complete file in one ```python block.\n\n```python\n"
               + SRC + "```",
}

ask(PORT, LOG, "Say hi.", 8)  # warm-up: the adaptive expert cache is cold right after start
res = {"label": LABEL, "reps": REPS, "runs": []}
for rep in range(REPS):
    for name, prompt in TESTS.items():
        r = ask(PORT, LOG, f"[{uuid.uuid4().hex[:8]}] " + prompt, 700)
        r.pop("text", None)
        r |= {"test": name, "rep": rep}
        res["runs"].append(r)
        print(r, flush=True)
for name in TESTS:
    v = [r["tg"] for r in res["runs"] if r["test"] == name and "tg" in r]
    if v:
        print(f"== {name}: {statistics.median(v):.1f} t/s (median of {len(v)}, min {min(v)}, max {max(v)})")
save(LABEL, "decode", res)

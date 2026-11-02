"""Prompt read speed at several depths: the frozen document repeated up to N thousand tokens, a fresh nonce on
every request (nothing reused from the cache), then a two-sentence summary.

    python3 bench_ctx.py <port> <engine.log> <label> [--reps 1] [15 40 82 180]
"""
import os, random, sys
from _common import HERE, ask, save

args = sys.argv[1:]
PORT, LOG, LABEL = int(args[0]), args[1], args[2]
rest, REPS, TARGETS = args[3:], 1, []
i = 0
while i < len(rest):
    if rest[i] == "--reps":
        REPS = int(rest[i + 1]); i += 2
    else:
        TARGETS.append(int(rest[i])); i += 1
TARGETS = TARGETS or [15, 40, 82]
DOC = open(os.path.join(HERE, "prompt-benchmark.md"), errors="ignore").read()
CHARS_PER_TOKEN = 24000 / 7893

res = {"label": LABEL, "reps": REPS, "runs": []}
for k in TARGETS:
    need = int(k * 1000 * CHARS_PER_TOKEN)
    body = (DOC * (need // len(DOC) + 1))[:need]
    for rep in range(REPS):
        nonce = "".join(random.choice("abcdefgh0123456789") for _ in range(8))
        r = ask(PORT, LOG, f"Document {nonce}. Summarize the following document in two sentences.\n\n" + body, 200)
        r["text"] = r.get("text", "")[:80]
        r |= {"target_k": k, "rep": rep}
        res["runs"].append(r)
        print(r, flush=True)
save(LABEL, "ctx", res)

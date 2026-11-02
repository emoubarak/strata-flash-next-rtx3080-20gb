"""Agent-style file edit: rewrite the whole of rewrite-source.py with one rename, 2,500 tokens max.
Shows draft acceptance on near-copy output (the MTP head guesses almost every token).

    python3 bench_rewrite.py <port> <engine.log> <label>
"""
import os, sys
from _common import HERE, ask, save

PORT, LOG, LABEL = int(sys.argv[1]), sys.argv[2], sys.argv[3]
code = open(os.path.join(HERE, "rewrite-source.py"), encoding="utf-8").read()
prompt = ("Rewrite the whole file below, unchanged except for one thing: rename the function `ask` to "
          "`ask_strata` everywhere. Output only the complete file in one ```python block.\n\n```python\n" + code + "```")
r = ask(PORT, LOG, prompt, 2500)
r["faithful"] = r.get("text", "").count("ask_strata(") >= 2 and "def ask(" not in r.get("text", "")
print({k: v for k, v in r.items() if k != "text"})
save(LABEL, "rewrite", {"label": LABEL, "runs": [r]})

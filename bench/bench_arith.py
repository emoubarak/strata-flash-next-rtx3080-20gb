"""Cold accuracy check for approximate settings (STRATA_ROUTE_TAIL_SKIP, quantization): 40 two-digit
multiplications, thinking off, temperature 0, run right after the server starts. Q2_0 scores 38/40 at the
default rank 7 and at rank 4 (misses 36x59 and 71x86: model errors, same at every safe setting).

    python3 bench_arith.py <port>
"""
import json, random, sys, urllib.request

port = int(sys.argv[1]); random.seed(7); ok = 0; n = 40; bad = []
for i in range(n):
    a, b = random.randint(12, 99), random.randint(12, 99)
    body = {"model": "x", "messages": [{"role": "user", "content": f"[{i}] {a} x {b} ? Réponds juste le nombre."}],
            "max_tokens": 20, "temperature": 0, "reasoning_effort": "none"}
    r = json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/v1/chat/completions",
        json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=120))
    text = r["choices"][0]["message"]["content"]
    if "".join(c for c in text if c.isdigit()) == str(a * b):
        ok += 1
    else:
        bad.append(f"{a}x{b} -> {text[:30]!r}")
print(f"{ok}/{n} correct", bad)

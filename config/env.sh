# Environment for the Strata server (source it before serve/server.py). Measured on this machine, see README.
export STRATA_PREFILL_CPU_SHARE=1   # the CPU computes the experts that are not on the card while a prompt is read
export STRATA_KV_PREFETCH=1         # streamed KV uploaded while the previous layer computes (+2.5 to +4.8 % read)
export STRATA_PREFILL_MMQ=0         # FP16 prompt path instead of int8 MMQ: avoids NaN loops on some long agent prompts (#879)
export STRATA_ROUTE_TAIL_SKIP=4     # skip an off-card expert ranked 4th or worse by every token in the window (default 7)

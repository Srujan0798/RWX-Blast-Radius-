You are the harness, loop, and scheduling implementation agent for RWX. Produce executable cycles and measured candidates, not a proposal.

Root: `/Users/srujansai/Desktop/RWX - Blast Radius`. Read `src/worker_scheduler.py`, `tests/test_worker_scheduler.py`, `Makefile`, `SCORING.md`, and the ledgers.

Current scheduler uses deterministic adaptive LPT, exact `max_load_ms + 2000*k`, k=1..8, and cost-neutral catalog free filling. Do not replace it without a measured reason.

Execute one of these:

1. Build a one-command candidate harness that runs unit tests, clean amd64 build, constrained sample, independent mutation comparison, hashes, and ledger fields.
2. Test an exact/mip-free makespan improvement using stdlib only; fall back to LPT at a deterministic node/time cap.
3. Improve free-fill insurance without increasing maximum load or worker count.

Use the `re0-loop` cycle: frame the gate, build one vertical slice, drive the real Docker scorer, write a memo, and choose keep/iterate/restart. Every cycle must introduce outside truth or a structurally different mechanism; repeated wording and identical candidates do not count.

Measure CPU, wall, memory, stdout bytes, three hash-seed outputs, base score, misses, and total. Preserve deterministic ties and exact-once assignments. Accept only lower total cost with zero misses and no compliance regression. Return code, commands, results, and the next hypothesis.

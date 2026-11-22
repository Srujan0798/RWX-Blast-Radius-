# RWX executable continuation pack

Use these as paste-ready assignments from the repository root:

`/Users/srujansai/Desktop/RWX - Blast Radius`

The product is the repository root itself. `Dockerfile`, `src/`, and `maps/` are top-level. Do not copy an archive or old checkpoint over them.

## Current truth

- Best candidate: v18.1, **167.612 simulated seconds, zero missed sample commits**.
- 95 unit tests pass after the parser fix; v18.1 previously passed three constrained hash-seed runs.
- Output: `experiments/OUTPUT.v18.jsonl`; SHA-256 `f338131730298cd0b9b2370d77616ab704e3396b3bd5db42888074fd0c3ba97f`.
- Malformed-patch widening is fixed and verified; four independent mutation misses remain release-blocking. Check the latest ledger before work.
- The existing ZIP is the last packaged fallback, not proof that v18.1 is packaged.
- The 99.9-second target remains open. No ranking or prize claim is supported.

For immediate manual delegation, use **`LOCAL_AGENT_EXECUTION_HANDOFF.md`**: it contains the exact current state, isolated assignments, commands, and accept/revert gates. Read `ULTIMATE_EXECUTION_PROTOCOL.md` for the full phase-one/phase-two research execution assignment. Then read `experiments/state/PROJECT_STATE.md`, both ledgers, and `docs/RE0_EXECUTION_MEMO.md`. Phase-one P01–P11 is preserved at `docs/L1-11_combined_phase-1.md`; restored archives and extractions are under `research/` and must remain available during the research execution audit.

## Assignments

1. Paste `ULTIMATE_EXECUTION_PROTOCOL.md` into the coordinating agent first, followed by `01_MASTER_ORCHESTRATOR.md` for its detailed operating rules.
2. Assign `02_ZERO_MISS_RESCUE_PROMPT.md` and `03_AST_CHANGE_ANALYSIS_PROMPT.md` sequentially if they touch the same source.
3. Assign `04_SELECTOR_ABLATION_PROMPT.md` for dialect, fixture, serde, and runtime-reader gaps.
4. Assign `05_INDEPENDENT_MUTATION_VALIDATION_PROMPT.md` for outside-truth validation. Do not use the official answers as product input.
5. Assign `06_SCHEDULER_PROMPT.md` for benchmark automation and scheduler experiments.
6. Assign `07_RESEARCH_MERGE_AUDIT_PROMPT.md` for development-harness and product-internal integration.
7. Assign `08_COMPLIANCE_AND_DETERMINISM_PROMPT.md` before promoting any candidate.
8. Use `09_RELEASE_PACKAGING_PROMPT.md` only after a candidate clears every gate.

Agents may explore candidates independently, but only the orchestrator merges into the root product. Every candidate needs a real Docker sample score; a design, summary, import check, or unit test alone is not progress.

## Non-negotiable gates

- Zero known missed failing commits on every promoted candidate.
- No `answers.json`, patch IDs, edit-kind outcome maps, or sample-outcome tables in selection logic.
- Unknowns and parse/apply failures widen conservatively.
- Accept only measured score improvements with equal or stronger evidence.
- Keep a compact negative corpus; do not rerun rejected ideas unchanged.
- External push and submission require separate owner authorization.

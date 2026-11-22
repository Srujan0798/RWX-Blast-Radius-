You are the outside-truth validation agent for RWX. Generate and execute independent evidence; do not validate the selector using only its own map or the sample answers.

Root: `/Users/srujansai/Desktop/RWX - Blast Radius`. Read `SCORING.md`, `build/generate_maps.py`, `src/coverage_selector.py`, and `protocols/01_MASTER_ORCHESTRATOR.md`.

Create deterministic source mutations from the pinned sqlglot checkout covering condition flips, constant changes, function bodies, class/module assignments, imports, fixtures, comments, serde, and dialect code. Apply each mutation to a clean independent checkout, run the real tests with locked requirements and `SKIP_INTEGRATION=0`, then compare actual failing test IDs with the candidate's selection.

Run containers sequentially with at most 4 CPUs and 8 GB each. Four concurrent 4 GB suites previously produced exit 137; those killed runs are invalid evidence and must not be counted as passes or failures. Preserve a compact summary; raw logs stay under git-ignored `experiments/`.

Use only source-derived mutations, never copied sample patch outcome mappings. Include at least one no-op and one malformed/uncertain input. Verify fallback behavior and stable test-ID renumbering.

Deliver:

1. Mutation generation and execution method.
2. Number executed, invalid/killed runs excluded, and real failures observed.
3. Exact missed-failure analysis, if any.
4. Smallest generic correction for a miss.
5. A clear pass/fail verdict for the candidate.

Do not edit root product code unless the orchestrator assigns a specific fix. Do not claim hidden-set safety from a finite mutation set.

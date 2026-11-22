# Local agent execution handoff

Repository: `/Users/srujansai/Desktop/RWX - Blast Radius`  
GitHub: https://github.com/Srujan0798/RWX-Blast-Radius-.git

Use the repository root as the natural product layout. Do not move the product into another single container folder. Do not push or submit externally.

## Current verified state

- Accepted candidate: **v18.1, 167.612 simulated seconds, zero official sample misses**.
- Accepted output: `experiments/OUTPUT.v18.jsonl`, SHA-256 `f338131730298cd0b9b2370d77616ab704e3396b3bd5db42888074fd0c3ba97f`.
- Existing `release/RWX_BLAST_RADIUS_FINAL.zip` is the older verified **v17** fallback. Never replace it until the new candidate passes every gate.
- Malformed-patch fallback is fixed: **95 tests pass**, the official sample is unchanged at 167.612 seconds with zero misses, and a real constrained garbage-patch run selected all 1,620 tests.
- Remaining independent blockers: protocol-05 misses **169, 218, 1106, 1167**.
- **99.9 seconds is not reached.** Do not claim it, first place, or a prize.

Read first: `experiments/state/PROJECT_STATE.md`, `experiments/EXPERIMENT_LEDGER.csv`, `experiments/BENCHMARK_LEDGER.csv`, `SCORING.md`, `docs/L1-11_combined_phase-1.md`, `docs/L01-L08_COMBINED_PROTOCOLS.md`, and `protocols/ULTIMATE_EXECUTION_PROTOCOL.md`.

All eight supplied ZIPs and both checksum files are preserved in `research/archives/` and extracted under `research/extracted/`. CRC and supplied SHA-256 checks passed. Start navigation at `research/extracted/BUILDATHON_ALL_FILES_MASTER/MASTER_INDEX.md`. Use these as executable references; do not delete them until every distinct mechanism has an evidence-backed execution status. They are excluded from Git and Docker.

## Non-negotiable rules

1. Never read `evaluation/sample/answers.json` in selection logic or derive lookup tables from it. Official scoring may consume it only through the provided scorer.
2. No patch-ID, patch-text, test-number, or sample-outcome exceptions. Relations must come from source structure, imports, fixtures, dynamic dispatch, or real patched execution.
3. Unknown files, malformed patches, parse/apply failures, and unsupported operations widen conservatively.
4. Every candidate works in its own directory. Never overwrite root with an entire candidate. Merge only reviewed files.
5. Accept only with zero known misses, all tests passing, deterministic output, compliant CPU/memory/runtime, and a lower verified score. Otherwise reject and preserve root.
6. One failing or missing test is a correctness blocker. A lower score with a miss is not an improvement.
7. Record every trial in `experiments/EXPERIMENT_LEDGER.csv` and benchmark evidence in `experiments/BENCHMARK_LEDGER.csv`.

## Assignment A — adjudicate exact scheduler

An isolated worker owns `experiments/candidates/v19-scheduler`. Check whether it has finished before starting duplicate work. Its candidate predates the parser fix; never copy the whole directory into root.

Paste this into a local agent only if that worker has not completed:

```text
Work only in experiments/candidates/v19-scheduler. Implement deterministic exact scheduling for selected tests using official integer millisecond durations. For k=1 and k=2, compute the true minimum maximum load using bounded dynamic programming/subset sum. For k=3..8, use deterministic bounded improvement over LPT with explicit time and iteration caps; never claim exactness there. Minimize max_load + 2000*k, tie by fewer workers then lexicographic workers. Preserve free-fill invariants: add unselected zero-duration tests and any catalog test fitting existing slack without increasing max load or worker count. Keep output deterministic and scheduling below 5 ms/commit. Add exhaustive small-case oracle tests, ties, skewed durations, empty input, exact-once assignment, free-fill cost invariants, and runtime tests. Run the candidate test suite and real official Docker sample. Return score, misses, hashes, runtime, and changed files. Do not edit root, read answers.json, or use sample-specific logic.
```

Integration gate after completion:

```bash
diff -u src/worker_scheduler.py experiments/candidates/v19-scheduler/src/worker_scheduler.py
diff -u tests/test_worker_scheduler.py experiments/candidates/v19-scheduler/tests/test_worker_scheduler.py
python3 -m unittest discover -s experiments/candidates/v19-scheduler/tests -v
```

Merge only scheduler implementation and focused tests if correct. Then run from root:

```bash
python3 -m unittest discover -s tests -v
make sample SAMPLE="$PWD/evaluation/sample" IMAGE=rwx-v19-scheduler OUTPUT=/tmp/rwx-v19-scheduler.jsonl
python3 score.py evaluation/sample evaluation/sample/answers.json /tmp/rwx-v19-scheduler.jsonl
```

Reject any per-commit regression, nondeterminism, miss, duplicate test, invalid worker shape, or runtime-bound failure.

## Assignment B — close independent mutation misses

An isolated worker owns `experiments/candidates/v20-mutation-relations`. Check its result before duplicating work.

Required generic corrections:

- Dialect source edits must include the shared dialect contract suite `tests/dialects/test_dialect.py`, not only dialect-named suites. This addresses independent misses 169 and 218 without naming those numbers in product code.
- `sqlglot/helper.py::ensure_list` dynamic consumers missed executor and expression behavior. Trace actual source dispatch/imports and pinned test behavior to define the smallest complete generic relation. Do not special-case `ensure_list`, test 1106, or test 1167 merely because they failed.

Use real existing evidence in `experiments/mutations/logs/`, patches in `experiments/mutations/patches/`, and pinned source in `experiments/mutations/clean-sqlglot/`. Do not rerun all mutated suites unless the relation or execution environment changes; for selector-only changes, regenerate selection against the existing patches and compare to preserved real failures.

```text
Work only in experiments/candidates/v20-mutation-relations. Read the current candidate and root protocol-05 evidence. Finish generic dialect-contract and dynamic-dispatch relations for all four independent misses. Use live test IDs and synthetic maps in tests, including test renumbering. No numeric/test-ID allowlists and no patch-ID logic. Run candidate tests. Generate selections for the existing mutation patches using the candidate and compare with preserved real failures; report all misses, not only the original four. Also report the official sample score and per-commit cost deltas. Do not edit root.
```

After review, merge only `src/coverage_selector.py` and its focused tests. Run root unit tests and official sample. Then regenerate protocol-05 selections and run `python3 experiments/mutations/compare_p05.py`; update its stale malformed-patch comment/status to reflect the fixed full-suite fallback. A pass with missing logs or excluded chunks is indeterminate, not complete independent validation.

## Assignment C — measured optimization toward 99.9

Do not begin by deleting safety relations. Current major costs are visible from `experiments/OUTPUT.v18.jsonl` and official durations. The single `test_execute_tpcds` duration is 21.454 seconds, so commits requiring it have a hard scheduling lower bound above 23 seconds. Preserve unconditional TPC insurance for optimizer rule bodies: the planner-only 166.318-second variant was rejected after a real mutation produced 71 TPC subtest failures.

Use a fresh `experiments/candidates/v21-<hypothesis>` directory per hypothesis. The chief agent chooses one hypothesis at a time from measured cost deltas. Useful routes are better source-derived dynamic/call-graph evidence, fixture-to-test precision, structural AST classification, and exact scheduling. Do not use broader AI generation as a substitute for a falsifiable selector relation.

For each candidate:

1. State the missing/overbroad relation and predicted affected commits.
2. Add focused synthetic unit tests before integration.
3. Run the real official sample and compare per-commit cost and output.
4. Run targeted independent patched tests for every newly narrowed relation.
5. Accept only zero misses and lower cost; otherwise record the negative result and revert.

```text
Create one isolated candidate for the assigned selector/scheduling hypothesis. Do not edit root. Read the ledgers and preserve every existing safety relation unless new independent evidence proves it overbroad. Implement only the stated hypothesis with focused tests, run candidate tests and official Docker sample, and return per-commit deltas, total simulated seconds, misses, output hash, runtime, and independent patched-test evidence. Reject your own candidate if it cannot prove zero known misses. No sample-outcome or patch-specific shortcuts.
```

## Assignment D — final local release, only after A–C gates

Do not package while any independent miss remains. Once cleared:

```bash
python3 -m unittest discover -s tests -v
python3 build/candidate_harness.py --image rwx-vnext --output-dir experiments/runtime/harness-vnext --hash-seeds 1 31337 90210
make release
```

Require three byte-identical constrained outputs, zero misses, valid CPU/memory/runtime, clean Linux/amd64 build, and a clean extraction of the resulting ZIP passing the same tests and sample. Verify no answers, archives, credentials, caches, or experimental candidates enter the release. Record the release SHA-256 and provenance. Keep the v17 fallback until this complete verification passes.

## Suggested manual local routing

Run assignments in separate terminals, with disjoint ownership. Example command shape:

```bash
opencode run -m nvidia/nvidia/nemotron-3-ultra-550b-a55b --dir "$PWD" "<paste one assignment>"
```

Use a faster available NVIDIA model for focused tests or mechanical edits and a stronger model for dynamic-relation analysis. Model availability is environmental; do not invent a successful run. Return logs and candidate paths to the chief agent for adjudication.

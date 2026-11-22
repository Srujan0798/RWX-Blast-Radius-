# Re0 execution memo

## Decision

Iterate in place from the current v18.1 candidate at the repository root. Do not restart from an archive or build a parallel product. The current architecture, pinned map, tests, negative corpus, and release gates are reusable.

## Reusable contracts

- Reconstruct and validate the original-coordinate post-image before semantic analysis.
- Widen conservatively for malformed patches, parse/apply failures, unknown files, and unsupported behavior.
- Suppress all tests only when every changed file is proven AST-identical and no source-reader dependency remains.
- Keep coverage, imports, fixtures, dialect links, optimizer/planner links, serde safety, and dynamic readers as one impact graph.
- Use deterministic adaptive LPT scheduling and free filling only when worker count and maximum load do not increase.
- `evaluation/sample/answers.json` is evaluation-only. Never use patch identity, patch text, edit kind, or sample outcomes as a product lookup table.

## Rejected anti-patterns

- Narrow line/function selection alone: v1 missed four commits.
- Whole-file/import v2 and v3: one miss each.
- v5 and v7: one miss each.
- v10 (`rszg`) and v12 (`2jrq`): one miss each.
- Treating comment-only edits as automatically safe without AST and reader checks.
- Running many near-identical agents or benchmarks concurrently without memory limits; three later validation groups exited 137 and are not evidence.
- Counting research documents, proposed mechanisms, or model votes as execution.
- Deleting research references before every distinct mechanism has an execution-backed status, or mechanically rereading duplicate staged copies instead of using the canonical master index.

## Real-surface gates

Every promoted candidate must pass the complete unit suite (90 tests at v18.1), the constrained official Docker sample with zero misses, output comparison against its accepted parent, and focused independent real patched-test validation. Before release, require three byte-identical constrained runs across hash seeds, CPU/wall/memory/stdout checks, clean Linux/amd64 build, and a clean extracted-archive rerun.

Record base cost, misses, total, runtime evidence, hashes, and accept/revert rationale in `experiments/`. A nonzero pytest exit on an intentionally failing patched suite is expected; omission of an observed failing test from the selected set is a selector failure.

## Cycle note — protocol 02 (zero-miss graph rescue), current candidate

Baseline re-measured with a clean build: 166.318 simulated seconds, 0 misses, 3x byte-identical runs (sha 82ace0e...). This beats the ledger's v17 (171.626 s) and is deterministic.

Graph-impact analysis:
- Cost is dominated by 3utz (25.45 s) and 2jrq (25.45 s) — about 31% of the total.
- 3utz already selects exactly its 37 failing tests (serde whole-file coverage == affected set); at its cost floor.
- 2jrq changes `sqlglot.optimizer.eliminate_joins._should_eliminate_join`, which has zero direct test coverage in the pinned map, so graph expansion (importers + optimizer fixtures) is mandatory and cannot be pruned without the call graph the map does not carry.
- Every other commit is at or below ~10 s; narrowing any of them risks reintroducing a miss.

Decision: no graph-impact candidate is promoted this cycle. Any narrowing of 2jrq/3utz would violate the zero-miss hard gate; the current candidate (166.318 s, 0 misses) is retained as best safe option. Reaching 99.9 s requires a call-graph/symbol-impact mechanism beyond a single safe cycle.


## Protocol 06 harness cycle (B-H01)

- Built `build/candidate_harness.py` plus 9 focused tests: one command runs unit tests, clean amd64 build, constrained sample across three `PYTHONHASHSEED` values, CPU/RSS probe, score, hashes, and a canonical 15-field ledger row.
- Clean `--no-cache` amd64 build passed in 38.549 s. All 88 tests passed. The measured root tree produced 166.318 s base and simulated, zero misses, 6,186 selected tests, 29,090 stdout bytes, byte-identical output across seeds 1/31337/90210, median CPU 1.442 s, median wall 1.874 s, peak RSS 166.3 MB, total 167.760 s. SHA-256 `82ace0e9c869033a49169efa547aad88877e527ee21b895cb231b1894c0ec21a`.
- Lesson: root `src/` already differed from the accepted v17 state when this cycle ran, so the harness measured an unpromoted candidate. A harness reports reality; it does not promote. Keep orchestrator authority over root merges and ledger promotion.
- Anti-pattern eliminated: hand-assembled evidence with unverifiable wall/CPU/hash fields. The harness now emits the ledger row and JSON evidence directly.
- Keep decision: keep the harness as a reusable build utility. Iterate: attach outside-truth mutation evidence via `--mutation-evidence` before treating any lower score as promotable. Next hypothesis belongs to the orchestrator, not this harness cycle.

## Cycle note — protocol 02 candidate g3 (statement-scoped propagation)

Hypothesis: function-level coverage over-selects. A test can observe a change only if it executed the changed statement, so propagating impact at statement granularity should cut selection cost without losing failing tests.

Mechanism (isolated candidate `experiments/candidates/g3-statement-scope/`, parent = accepted v18.1):
- `src/change_analysis.py`: `ASTComparator.get_statement_ranges(tree)` collects statement spans; `ASTComparator.innermost_statement_span(ranges, line)` picks the smallest enclosing statement of a changed line.
- `src/coverage_selector.py`: `_statement_scope(path, changeset, analysis)` selects tests whose coverage hits any line of that statement. Preconditions: removed and added line sets are identical (same-coordinate replacement), pre-image AST parses, change is not structural, file is not `sqlglot/serde.py`.
- Fallbacks are explicit: empty statement coverage returns to the existing line+function path, an empty function path returns to whole file, serde and structural edits keep whole file.

Measured result (harness, constrained amd64, seeds 1/31337/90210): 163.942 s simulated, 0 misses, 6079 selected tests, output sha256 `52e4ac32...`, CPU 1.050 s, peak RSS 166.6 MB, 95 unit tests, byte-identical across seeds. Parent v18.1 was 167.612 s. Only two sample commits move: 2haz 95 to 80 selections, ary6 113 to 16.

Independent real-surface evidence (outside truth, real pytest runs on mutated source):
- Six mechanism-targeted mutations, each located where statement coverage is far below function coverage, including a short-circuit mutation (`parser.py` `_is_table_query`, 2 failing tests): candidate 0 misses everywhere. Selections collapse on three of them (15/5/40 versus parent 1564/1482/1517), while the short-circuit mutation keeps the full 1323-test scope, so the safety case that function coverage used to cover survives.
- Sample commits with real suites: ary6 fails 10 tests and the candidate covers all 10; 2haz fails none, so its dropped 15 selections were pure over-selection.
- P05 corpus: candidate selection equals parent selection, so the three pre-existing misses (169, 218, 1167) are unchanged and not caused by this mechanism.

Rejected this cycle: symbol/name-aware impact edges (textual symbol scan, 254.865 s, and it duplicates the concurrent name-usage index work).

Keep decision: the candidate stays isolated; the orchestrator owns root merges and ledger promotion because the root product moved during this cycle. If the merge changes the baseline lineage, the harness must re-run before promotion. Known limit: the 30-commit sample floor is 94.351 s at oracle selection and about 120 s practically, so 99.9 s is not reachable with this sample and a safe selector.

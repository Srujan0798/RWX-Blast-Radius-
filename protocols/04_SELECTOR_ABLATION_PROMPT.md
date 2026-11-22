You are the dynamic-coverage implementation agent for RWX. Execute one narrow candidate addressing dynamic behavior.

Root: `/Users/srujansai/Desktop/RWX - Blast Radius`. Read `build/generate_maps.py`, `src/coverage_selector.py`, `tests/test_coverage_selector.py`, and the experiment ledger.

Existing coverage already includes per-test dialect literals, fixture `# dialect:` metadata, optimizer fixture consumers, source readers, planner/executor links, dialect-specific typing links, and serde whole-file safety. Do not recreate these.

Select one falsifiable improvement: fixture-feature indexing, dialect-specific parser/generator impacts, serializer/type dependency precision, subprocess coverage propagation, or source-reader precision. Replace a measured broad dependency class rather than stacking more tests.

Known outside-truth constraints:

- `ary6` exposed BigQuery optimizer fixture dependencies.
- `2jrq` exposed optimizer fixtures and a second-hop executor dependency.
- `3utz` exposed broad serializer impacts.
- `rszg` exposed dialect typing/optimizer interaction.

These are diagnostic evidence, not keys for conditional code. Never reference commit IDs in product logic.

Run focused tests, the complete unit suite, and the official amd64 sample. Compare every per-commit selection and cost with v18.1. Any miss rejects the candidate. Add independent patched-suite evidence for the narrowed relation and record exact results. Return changes and measurements only; no research inventory.

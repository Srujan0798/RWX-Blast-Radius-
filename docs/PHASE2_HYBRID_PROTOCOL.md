# Phase 2 hybrid execution protocol

## Workspace contract

The repository root is the only product authority. `Dockerfile`, `src/`, `maps/`, `tests/`, and `build/` are top-level. Do not restore an old archive or copy a checkpoint over them.

- `docs/`: official brief, verbatim combined L01–L08, and execution lessons.
- `protocols/`: paste-ready executable assignments; start at `00_START_HERE.md`.
- `evaluation/sample/`: official sample inputs and evaluation-only answers.
- `experiments/`: current output, ledgers, runtime evidence, and project state; never shipped.
- `provenance/`: verified archive checksums and source-ingestion record.
- `release/`: local deterministic release ZIP and SHA-256 sidecar; never commit generated releases.

## Current hybrid: v18.1

The selector combines strict original-coordinate patch reconstruction, AST-identical no-op handling with source-reader retention, two-hop structural imports, direct optimizer/planner links, narrowed optimizer fixture consumers with unconditional TPC insurance, dialect-specific typing links, serde whole-file safety, dynamic coverage, and deterministic adaptive LPT/free fill. Unknown or unsupported changes must widen conservatively.

The verified sample result is 167.612 simulated seconds with zero missed commits; all 90 unit tests pass. Three constrained hash-seed runs were byte-identical. Independent mutation misses and malformed-patch widening remain release-blocking. Start with `../protocols/ULTIMATE_EXECUTION_PROTOCOL.md` for the phase-one research execution audit and prioritized assignments. The 99.9-second target remains open.

## Execution loop

For each bounded candidate:

1. State the mechanism, safety risk, parent hash, disjoint ownership, and falsifying experiment.
2. Implement the smallest complete vertical slice with focused tests in an isolated candidate, never concurrently in root.
3. From root run `python3 -m unittest discover -s tests -v`.
4. Run `make sample SAMPLE="$PWD/evaluation/sample" IMAGE=<candidate> OUTPUT=/tmp/<candidate>.jsonl`.
5. Record base cost, misses, simulated total, CPU/wall runtime, output size, memory, and hashes in the ledgers.
6. Compare independently observed real patched-suite failures with selected tests for affected candidates.
7. Accept only a measured improvement with zero misses and equal or stronger evidence; otherwise revert and record the negative result.
8. Update `RE0_EXECUTION_MEMO.md`, then choose a structurally different hypothesis. Never rerun a rejected configuration unchanged.

## Final gates

On the exact exported copy require:

- All unit tests pass.
- The official constrained sample has zero misses and byte-identical output to the accepted candidate.
- Independent mutation validation has no unresolved selector safety failure.
- Three repeated outputs are byte-identical across hash seeds.
- CPU, wall time, memory, read-only/nobody behavior, stdout size, clean Linux/amd64 build, and repository size pass.
- No answers, patch lookup tables, credentials, caches, development databases, logs, or sample outputs are packaged.
- The deterministic local ZIP, SHA-256 sidecar, and archive provenance are present.

Project repository: https://github.com/Srujan0798/RWX-Blast-Radius-.git. External push/submission and any ranking or prize claim remain outside autonomous completion.

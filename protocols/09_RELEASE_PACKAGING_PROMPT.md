You are the local release-packaging agent for RWX. Package only a candidate that cleared every correctness and compliance gate.

Root: `/Users/srujansai/Desktop/RWX - Blast Radius`. Read `protocols/08_COMPLIANCE_AND_DETERMINISM_PROMPT.md`, `experiments/state/PROJECT_STATE.md`, and the ledgers. The existing packaged fallback is v17 at 171.626 seconds. The current v18.1 candidate measures 167.612 seconds with zero official sample misses. Malformed-patch widening is fixed and verified with 95 tests and real constrained fallback execution; the four independent mutation misses must still be resolved before packaging it. The 99.9 target remains open.

The submission repository must have `Dockerfile` at its top. The natural root layout already satisfies this. Keep `evaluation/`, `experiments/`, and `release/` git-ignored. Ship only product source, top-level build files, `maps/maps.json.z`, its map build report, tests/build utilities, and concise documentation/protocols desired by the owner.

Create a deterministic ZIP under `release/` with a SHA-256 sidecar. Extract it into a clean temporary directory, run all unit tests, build its Dockerfile for Linux/amd64, run the constrained official sample, and require byte-identical output to the accepted candidate with zero misses. Verify archive integrity and repository size.

Update the state and ledgers with the exact candidate hash and evidence. Remove temporary extraction and caches after verification. Do not include original research archives, duplicate checkpoints, official answers, raw logs, or generated development databases.

Project repository: https://github.com/Srujan0798/RWX-Blast-Radius-.git. Do not initialize a remote, push, or submit unless the owner separately authorizes that action. Never claim first place, a prize, or hidden-set performance.

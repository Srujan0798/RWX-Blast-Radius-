# RWX ultimate execution protocol — paste this into the coordinating agent

Understood as: use the phase-one research and phase-two implementation protocols as executable inputs, delegate bounded labor, preserve all reference archives until their techniques are adjudicated, and improve the real product through measured zero-miss experiments rather than generating more research summaries.

## 1. Authority and current truth

Workspace: `/Users/srujansai/Desktop/RWX - Blast Radius`.

The repository root is the product. `Dockerfile`, `src/`, `maps/`, `tests/`, and `build/` are top-level. Do not restore an old project over this tree and do not put the product back inside a single container folder.

Project repository: https://github.com/Srujan0798/RWX-Blast-Radius-.git

Current measured candidate: **v18.1, 167.612 simulated seconds, zero official sample misses, 90 unit tests**. Accepted output: `experiments/OUTPUT.v18.jsonl`, SHA-256 `f338131730298cd0b9b2370d77616ab704e3396b3bd5db42888074fd0c3ba97f`.

The target is **99.9 simulated seconds with zero misses**. It is not achieved. No first-place, prize, or hidden-set claim is permitted.

Independent protocol-05 mutation validation found unresolved misses involving tests 169, 218, 1106, and 1167. Treat these as release-blocking correctness work, not as optional polish. Malformed nonempty patches now widen conservatively: the parser fix and adversarial regressions passed 95 tests plus the real constrained fallback workflow, while preserving byte-identical 167.612-second official sample output. Check current ledgers before acting because another agent may have fixed the remaining misses.

The existing local ZIP is a fallback artifact, not proof that the current root is packaged. Never overwrite the last verified ZIP until its replacement passes clean-archive verification.

## 2. Read these sources before assigning work

1. `README.md`, `SCORING.md`, `docs/OFFICIAL_CHALLENGE_BRIEF.md`.
2. `experiments/state/PROJECT_STATE.md`, both CSV ledgers under `experiments/`, and `docs/RE0_EXECUTION_MEMO.md`.
3. `docs/L1-11_combined_phase-1.md`: the preserved phase-one P01–P11 source protocol.
4. `docs/L01-L08_COMBINED_PROTOCOLS.md`: the eight phase-two protocol bodies, appended verbatim.
5. `protocols/00_START_HERE.md` and the specialized assignments in `protocols/`.
6. `research/extracted/BUILDATHON_ALL_FILES_MASTER/MASTER_INDEX.md`.
7. Canonical research under `research/extracted/BUILDATHON_ALL_FILES_MASTER/p11_build/AGENT_TEMPLATE/`, especially:
   - `05_RESEARCH_AND_ALGORITHMS/ALGORITHM_NOTES.md` and `RESEARCH_LIBRARY.md`.
   - `06_AGENTIC_HARNESS_ARCHITECTURE/NINE_PART_OPERATING_ARCHITECTURE.md` and `DEV_VS_PRODUCT_RUNTIME.md`.
   - `04_CAPABILITY_AND_RESOURCE_MAPPING/PHASE2_SKILL_ACTIVATION.md`.
   - `09_EXPERIMENTAL_VALIDATION/METRICS_AND_EXPERIMENT_STATUS.md`.
   - `11_PHASE2_ENGINEERING_HANDOFF/TASK_DAG.md`, `AGENT_ALLOCATION.md`, and `VALIDATION_GATES.md`.
   - `13_DECISIONS_AND_RISKS/` and `10_ADVERSARIAL_AUDIT/`.

The master archive also contains the original dossier, A1–A7 role archives, competitor research, papers, and experiment catalogues. Use `MASTER_INDEX.md` to find canonical copies. Do not read thousands of duplicate staged copies sequentially. Deduplicate by content hash, retain distinct variants, and record the canonical source path for every extracted hypothesis.

## 3. Archive preservation and execution audit

All eight supplied ZIPs and both loose checksum files are restored under `research/archives/`; safe extractions are under `research/extracted/`. CRC checks passed and both supplied SHA-256 sidecars match.

**Do not delete or archive-away these references during execution.** They are excluded from Git and Docker to protect submission size, not because they are useless.

For every distinct research mechanism, assign one status in the execution ledger:

- `IMPLEMENTED`: running product code and evidence path exist.
- `TESTED_ACCEPTED`: measured improvement passed every required gate.
- `TESTED_REJECTED`: real experiment failed; record score, miss, or complexity reason.
- `NOT_APPLICABLE`: explain the official-rule or technical mismatch.
- `HYPOTHESIS`: ready experiment with an owner and falsifying gate.

A document read, agent opinion, or skill invocation is not implementation. Do not declare research consolidation complete while unadjudicated hypotheses remain. When all mechanisms have evidence-backed statuses, the owner may separately authorize cleanup.

## 4. Nine-mode operating system

Run these as one coordinated system:

1. **Central command:** one root authority, one current candidate, append-only ledgers, one promotion owner.
2. **Independent council:** assign structurally different candidates, not paraphrased agreement. Preserve disagreement; no majority vote substitutes for execution.
3. **Hierarchical orchestration:** chief architect handles integration and adjudication; specialists own bounded modules and experiments.
4. **Research conversion:** translate each relevant paper into a map, algorithm, or harness experiment with transfer limitations and a real gate.
5. **Selective skills/tools:** use the applicable capability at the point of work. Do not invoke unrelated skills to inflate a count.
6. **Harness loop:** hypothesis → isolated implementation → unit tests → constrained Docker score → independent mutations → memo → promote/revert → next hypothesis.
7. **Graph engineering:** maintain product impact graphs and the development task DAG. Prefer build-time precomputation and deterministic runtime lookups.
8. **Dual-layer integration:** development intelligence may generate frozen maps and algorithms; runtime must never call agents, model APIs, skills, ledgers, answers, or development services.
9. **Deterministic control and memory:** explicit task states, disjoint ownership, hash-seed checks, same-session ledger updates, and a preserved last-known-good candidate.

## 5. Agent assignments and ownership

Use separate CLI windows, subagents, or available OpenCode processes. Only the coordinator writes the accepted root. Each worker uses `experiments/candidates/<candidate-id>/` or returns a patch for review.

### A1 — Chief architect / integrator

Read this whole protocol and `protocols/01_MASTER_ORCHESTRATOR.md`. Maintain the task DAG, route work, review diffs, run final gates, and accept/revert candidates. Do not perform mechanical inventory work that a worker can do.

### A2 — Static analysis and patch correctness

Own `src/patch_parser.py`, `src/changeset.py`, and `src/change_analysis.py` candidates. The no-header garbage-patch empty-plan issue is fixed: malformed nonempty patches widen to full-suite coverage, and 95 tests plus real constrained execution passed. Preserve those regressions. Extend adversarial coverage for bad counts, overlapping hunks, renames, additions/deletions, newline markers, parse failures, and unknown files without weakening fallback behavior.

Then evaluate STARTS/NameRTS-style declaration and name-element relations. Ambiguous bindings must widen. Do not enable function-level narrowing without independent recall evidence.

### A3 — Graph and metadata engineer

Own `build/generate_maps.py`, map-schema candidates, and graph evidence. Existing maps already contain coverage, AST spans, imports, fixtures, source readers, and dialect links; do not rebuild them as if absent.

Investigate the protocol-05 misses for tests 169, 218, 1106, and 1167. Determine the missing generic relation from real patched execution. Add the smallest complete relation, including dialect contract tests and dynamic executor paths where evidence supports them. Validate stable test-ID joins under renumbering.

Evaluate NameRTS module-level name propagation as a cross-check over coverage. Function-level name narrowing remains off until the research-specified precision and zero-miss gates pass.

### A4 — Selection and dynamic behavior

Own `src/coverage_selector.py` candidates, coordinated with A3. Preserve strict AST-no-op reader retention, two-hop structural imports, optimizer/planner links, serde whole-file safety, typing/dialect links, and conservative fallbacks.

Do not repeat rejected configurations v1, v2, v3, v5, v7, v10, or v12. Do not restore the planner-only TPC gate: the 166.318-second variant was rejected because independent mutation evidence showed missing TPC failures. v18.1 deliberately retains TPC insurance.

Use leave-one-change-kind-out analysis and independently generated mutations. No patch-ID, patch-text, edit-kind, or sample-outcome lookup tables.

### A5 — Scheduler and CPU engineer

Own `src/worker_scheduler.py` candidates. Implement the unexecuted research priority E-142/E-143:

- Exact two-worker partitioning using millisecond durations and deterministic subset-sum/bitset search.
- Fee-aware choice over 1–8 workers.
- Deterministic pass-bounded local search for 3–8 workers where it improves LPT.
- Preserve free filling only when maximum load and worker count do not increase.
- Target under 5 ms scheduling CPU per commit; fall back to LPT when a bound is reached.

This is selection-invariant and should be prioritized for safe score reduction. Compare every commit's makespan and total against LPT, test heavy-test dominance and rounding, and run three constrained hash-seed runs.

### A6 — Real execution and harness engineer

Own `build/candidate_harness.py` and execution evidence. Use the existing harness rather than creating a parallel benchmark system.

Required commands from root:

```sh
python3 -m unittest discover -s tests -v
make sample SAMPLE="$PWD/evaluation/sample" IMAGE=<candidate> OUTPUT=/tmp/<candidate>.jsonl
```

Record base cost, misses, simulated total, CPU, wall, peak RSS, stdout bytes, output SHA-256, and per-commit deltas. Run real patched sqlglot suites with locked requirements and `SKIP_INTEGRATION=0`. Execute suites sequentially; concurrent 4 GB groups previously exited 137 and are invalid evidence.

### A7 — Red-team, provenance, and release

Own independent mutation adjudication, compliance, leakage, and packaging review. Use `protocols/05_INDEPENDENT_MUTATION_VALIDATION_PROMPT.md`, `08_COMPLIANCE_AND_DETERMINISM_PROMPT.md`, and `09_RELEASE_PACKAGING_PROMPT.md`.

Include condition flips, constants, class/module assignments, imports, fixtures, comments, serde, dialects, source readers, malformed patches, no-op edits, and test renumbering. Never treat sample answers as independent ground truth. Package only after every release-blocking miss is resolved.

## 6. Research-to-code priorities

Execute in this order unless new evidence changes the critical path:

1. **Correctness unblock:** protocol-05 misses 169, 218, 1106, 1167. Malformed-patch widening is already fixed and verified.
2. **Exact scheduler:** E-142/E-143; selection-invariant savings with a CPU ceiling.
3. **NameRTS module graph:** build-time name-element map and safety cross-check; no narrow function policy yet.
4. **Dynamic dependency evidence:** dialect registry, executor, source-reader, fixture, serde, subprocess, and short-circuit mutation relations.
5. **Interprocedural impact:** build-time call/name reachability for uncovered optimizer and executor paths; conservative ambiguity fallback.
6. **Fine-grained precision:** FineRTS/STARTS-inspired declaration impact only after outside-truth recall gates.
7. **Robustness:** unseen-kind mutation fuzz, stable IDs, deterministic output, resource limits.
8. **Release:** clean extracted ZIP, full tests, official sample, independent evidence, three hash-seed runs, compliance and size audit.

Research anchors: NameRTS for Python name dependencies; Ekstazi for file dependency sets; STARTS for declaration changes; Weiser/Horwitz for slicing and interprocedural reachability; Graham/LPT only as a scheduling baseline, not proof of optimality. Paper results are not sqlglot results; every transferred mechanism needs local execution.

## 7. Skill routing that produces work

Use skills when available and applicable:

- `readchk` before bundled/ambiguous assignments; `modelchk` for model-tier selection.
- `graphify` for code/file relationship inspection; `nba` for the next highest-leverage action.
- `re0-loop` for real cycles; `re0-memo` after accept/reject cycles; `re0-work` only if the foundation is proven wrong.
- `deep-research` only for a named falsifiable technique; `factchk` for external factual claims.
- `mandela` to detect oracle leakage and self-confirming benchmarks.
- `review-bugbot` and `review-security` for integrated changes when available.
- `sip` and `shower` for artifact/instruction review; `detool` for portability; `ssotize` for approved deduplication.
- `docs` for documentation and `visualize` only when a diagram clarifies execution.

If a skill or connector is unavailable, record that and use the equivalent local mechanism. Never fabricate a skill run. Development skills never become runtime dependencies.

## 8. Model routing and resource discipline

Use high-capability reasoning for integration, ambiguous misses, and adversarial review. Use cheaper/flash models for isolated tests, inventory deduplication, and mechanical implementation. When OpenCode and credentials are available, candidate routes from the existing master protocol include NVIDIA Nemotron for difficult graph semantics and MiniMax/DeepSeek/GLM flash models for bounded labor. Verify actual availability; do not print credentials or claim a model ran without evidence.

Avoid concurrent memory-heavy full suites. Keep candidates isolated and root writes serialized. Do not spawn several agents to answer the same question.

## 9. Candidate contract and non-stall rule

Every worker must return:

1. Hypothesis and canonical research source path.
2. Owned files and parent candidate/output hash.
3. Exact implementation or experiment performed.
4. Unit-test and real Docker results.
5. Independent failures observed and missed-failure comparison.
6. Base cost, misses, total, CPU/wall/RSS/stdout and output hash as applicable.
7. Accept/reject recommendation and the next structurally different experiment.

Accept only measured improvements with zero known misses and equal or stronger independent evidence. Revert a rejected candidate, preserve the last-green root, append the negative result, and move to the next mechanism. Never stop merely because one variant fails; never repeat it unchanged. Do not stop at a plan while an executable hypothesis remains.

## 10. Hard compliance and release gates

- Runtime inputs are only `/data/tests.json` and `/data/commits/*.patch` plus pinned-source maps.
- `evaluation/sample/answers.json` is evaluation-only and never ships.
- No precomputed patch outcome tables, competitor answer artifacts, credentials, caches, or development logs in the product.
- Unknowns and malformed input widen conservatively.
- Require all unit tests, zero official sample misses, no unresolved independent selector miss, three byte-identical constrained runs, clean Linux/amd64 build, CPU/wall/RSS/stdout compliance, repository size below 20 MB, and clean extracted-archive reproduction.
- Regenerate the deterministic ZIP and SHA-256 sidecar only after these gates pass.
- Do not push or submit without separate owner authorization, even though the GitHub URL is known.

Continue until 99.9 is actually measured with zero misses, the owner stops the work, or every distinct safe hypothesis has an executed evidence-backed rejection. A time budget or a partially merged archive set is not proof of optimization exhaustion.

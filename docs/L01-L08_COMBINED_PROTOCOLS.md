# L01–L08 combined protocols

The eight protocol bodies below are appended verbatim in L01-to-L08 order. The supplied Untitled sources were consolidated here and verified byte-for-byte by section; the markers retain their original filenames for provenance. Use `../protocols/00_START_HERE.md` for current executable assignments.

<!-- BEGIN Untitled-1.md -->


# BUILDERS BUILDATHON 2026
# PHASE 2 — L01
# INTELLIGENCE INGESTION, OFFICIAL STARTER INSPECTION & BASELINE REPRODUCTION

PROTOCOL ID: L01
VERSION: 1.0
PHASE: Phase 2 — Local Engineering Execution
TARGET: RWX — BLAST RADIUS
ENVIRONMENT: MacBook Pro M4 Pro
AUTHORITY: Chief Engineering Architect
EXECUTION: Local IDE + available AI agents
PRIORITY: IMMEDIATE

---

# 1. MISSION

You are now the Chief Engineering Agent responsible for executing our RWX submission.

Phase 1 intelligence collection is complete or in the process of final delivery.

Your first responsibility is not to build an elaborate architecture.

Your responsibility is to establish a verified engineering environment.

You must:

1. Ingest the available seven independent Phase 1 research archives.
2. Inspect the actual official competition starter material.
3. Establish the authoritative project state.
4. Understand the actual execution and scoring environment.
5. Reproduce the official baseline or supplied reference implementation.
6. Establish a functioning benchmark workflow.
7. Prepare the first valid implementation architecture.

The ultimate goal is to win first place in RWX.

However, no optimization is valuable until the submission works correctly.

# 2. COMPETITION SCOPE

Exclusive target:

RWX — Blast Radius

Official challenge:
https://www.joinbuilders.org/buildathon/tracks/blast-radius

Official scoring:
https://www.joinbuilders.org/buildathon/tracks/blast-radius/files/SCORING.md?inline=1

No other buildathon tracks are in scope.

# 3. AVAILABLE INPUTS

The local engineering environment may receive:

## A. Seven independent research archives

AGENT_A1_PHASE1_FINAL.zip
AGENT_A2_PHASE1_FINAL.zip
AGENT_A3_PHASE1_FINAL.zip
AGENT_A4_PHASE1_FINAL.zip
AGENT_A5_PHASE1_FINAL.zip
AGENT_A6_PHASE1_FINAL.zip
AGENT_A7_PHASE1_FINAL.zip

These archives represent independent intelligence.

Do not assume all seven have arrived.

Inspect the files actually provided.

Record missing archives and continue with available materials.

## B. Official competition materials

The organizer-provided starter archive and any accompanying:

- README.
- SCORING.md.
- Source code.
- Docker configuration.
- Input examples.
- tests.json.
- Sample patches.
- Baseline implementation.
- Evaluator.
- Build instructions.
- Output examples.
- Dependency files.

These files must be supplied or otherwise made accessible to the local development environment.

Never invent their contents.

## C. Local hardware

MacBook Pro M4 Pro:

- 24 GB unified memory.
- 512 GB storage.
- Apple Silicon.

Use local resources intelligently.

Do not assume CUDA.

Do not confuse local ARM performance with the competition's x86 runtime performance.

# 4. AUTHORITY HIERARCHY

When information conflicts, follow this order:

1. Official current competition rules.
2. Official scoring implementation.
3. Official starter code and schemas.
4. Official organizer documentation.
5. Independently verified Phase 1 intelligence.
6. Research papers.
7. Agent architectural recommendations.
8. Unverified assumptions.

The seven research ZIPs do not override official requirements.

Do not silently accept an agent's proposed architecture as correct.

# 5. DIRECTORY AND FILE INGESTION

Create a clean workspace.

Suggested structure:

RWX_BUILDATHON/
│
├── 00_INPUTS/
│   ├── AGENT_ARCHIVES/
│   ├── OFFICIAL_STARTER/
│   └── OFFICIAL_DOCUMENTATION/
│
├── 01_PHASE1_INTELLIGENCE/
│   ├── A1/
│   ├── A2/
│   ├── A3/
│   ├── A4/
│   ├── A5/
│   ├── A6/
│   └── A7/
│
├── 02_COMPETITION_ANALYSIS/
│
├── 03_PROJECT/
│
├── 04_TESTS/
│
├── 05_BENCHMARKS/
│
├── 06_EXPERIMENTS/
│
├── 07_SUBMISSION/
│
├── 08_DOCUMENTATION/
│
└── PROJECT_STATE/

Adapt the structure to actual supplied files without losing provenance.

## Archive ingestion

For every ZIP:

1. Confirm the exact archive exists.
2. Calculate SHA-256.
3. Test archive integrity.
4. List contents.
5. Extract into its own isolated directory.
6. Inspect its manifest.
7. Verify checksums.
8. Identify missing files.
9. Identify duplicated documents.
10. Identify conflicting claims.
11. Preserve original archive unchanged.

Never overwrite one agent's research with another's.

Create a source-to-claim register.

# 6. SEVEN-AGENT INTELLIGENCE INTEGRATION

Use the following responsibilities when reviewing the archives.

A1 — Overall architecture and requirements.

A2 — Mathematical optimization.

A3 — Python static analysis and AST.

A4 — Graph engineering.

A5 — Research and scientific evidence.

A6 — Harnesses, skills, models and orchestration.

A7 — Red-team and compliance.

For every significant proposal extract:

- Recommendation.
- Supporting evidence.
- Originating agent.
- Original file and location.
- Official compatibility.
- Confidence.
- Implementation implications.
- Unresolved questions.

Compare competing recommendations.

Do not force consensus.

Identify the best-supported approach.

Create a consolidated decision register.

# 7. OFFICIAL STARTER INSPECTION

Inspect the actual supplied official kit.

Do not begin product implementation before understanding its structure.

Examine:

A. README and setup instructions.

B. SCORING.md.

C. Dockerfile and container configuration.

D. Existing source code.

E. Tests and metadata.

F. Patch input structure.

G. Output schema.

H. Existing baseline implementation.

I. Scoring and evaluation scripts.

J. Dependency files.

K. Build requirements.

L. Runtime restrictions.

Record the actual files inspected.

For each requirement identify its implementation location or the missing information.

# 8. OFFICIAL SCORING VERIFICATION

Independently reconstruct the actual scoring implementation.

Investigate:

- Per-test duration conversion.
- Worker assignment.
- Worker load.
- Two-second worker overhead.
- Missed-test penalty.
- CPU time.
- Repeated runs.
- Aggregate score.

Verify that our understanding matches the actual official scoring document and implementation.

Do not use a simplified scoring formula if the official evaluator contains additional details.

Record the exact formula and a reproducible calculation test.

# 9. ENVIRONMENT PREPARATION

Prepare a reproducible development environment.

Investigate and follow the official starter's documented requirements.

Verify:

- Required Python version.
- Docker availability.
- Docker architecture.
- Dependency installation.
- Build commands.
- Runtime commands.
- File permissions.
- Filesystem behaviour.
- Network restrictions.
- Runtime user.
- CPU and memory constraints.

Important:

The local MacBook uses Apple Silicon, while the final competition container may require linux/amd64.

Do not assume local native execution reproduces the official runtime.

Use an appropriate container or remote execution environment when required.

Do not invent installation or execution commands before inspecting the actual starter instructions.

# 10. BASELINE REPRODUCTION — FIRST MAJOR GATE

This is the highest-priority task.

Before introducing our sophisticated architecture:

1. Identify the supplied baseline implementation.
2. Reproduce its documented setup.
3. Execute the documented practice evaluation.
4. Capture the complete output.
5. Verify the scoring calculation.
6. Compare with the official reference score of 1,614.1 simulated seconds where the same evaluation conditions apply.
7. Investigate any discrepancy.
8. Save the exact source revision and configuration.

Measure separately:

- Official simulated CI score.
- CPU seconds.
- Wall-clock seconds.
- Peak memory.
- Build duration.
- Number of tests selected.
- Worker count.
- Missed failing commits.

Do not confuse wall-clock duration with the official simulated score.

Do not claim baseline reproduction succeeded without recorded evidence.

If the official baseline cannot be executed, document the exact blocker and continue with the smallest available valid conformance test.

# 11. FIRST WORKING SUBMISSION

Once the baseline has been reproduced or the official execution path has been verified:

Establish the smallest valid working submission.

Requirements:

- Correct input handling.
- Correct output format.
- Valid commit identifiers.
- Valid test identifiers.
- At most eight nonempty workers.
- Deterministic output.
- No prohibited network dependency.
- Valid container startup.
- No stdout contamination.
- Respect for all official restrictions.

Do not introduce complex algorithms before a valid end-to-end submission exists.

A valid working baseline is mandatory.

# 12. PROJECT STATE AND MEMORY

Create a central PROJECT_STATE.

PROJECT_STATE.md must include:

- Selected competition.
- Current source revision.
- Current working commit.
- Current implementation status.
- Baseline result.
- Latest official score.
- Outstanding failures.
- Active engineering decisions.
- Risks.
- Remaining time.
- Next critical task.

Create:

DECISION_LEDGER.md
EXPERIMENT_LEDGER.csv
BENCHMARK_LEDGER.csv
SOURCE_REGISTER.csv
TASK_GRAPH.json
RISK_REGISTER.md

Maintain one source of truth.

All agents must work from the documented project state.

# 13. LOCAL AGENT HIERARCHY

Use the seven engineering responsibilities:

A1 — Chief architecture and integration.

A2 — Scoring and optimization.

A3 — Static analysis and parsing.

A4 — Dependency graph and impact analysis.

A5 — Research and algorithm integration.

A6 — Harness and performance infrastructure.

A7 — Testing, compliance and adversarial verification.

The central architect controls:

- Shared interfaces.
- Task allocation.
- Main branch.
- Architecture decisions.
- Integration approvals.
- Submission readiness.

Use separate branches or worktrees where appropriate.

Do not let agents overwrite shared files without approval.

# 14. IMPLEMENTATION ORDER

Follow this initial sequence.

P0 — Official environment and baseline.

P0 — Input/output contract.

P0 — Minimal working submission.

P0 — Correctness validation.

P1 — Conservative test-selection architecture.

P1 — Baseline coverage and dependency intelligence.

P1 — AST and import analysis.

P1 — Graph-based impact analysis.

P1 — Safe selection and uncertainty fallback.

P1 — Worker scheduling.

P2 — Fine-grained symbol-level improvements.

P2 — Graph pruning and compact data structures.

P2 — CPU and memory optimization.

P3 — Optional advanced research techniques.

This is an initial priority structure, not a rigid requirement to implement every component.

The benchmark must decide what stays.

# 15. FIRST EXPERIMENTS

Establish these initial experiments:

EXP-001 — Environment validation.

EXP-002 — Baseline reproduction.

EXP-003 — Output contract validation.

EXP-004 — Minimal working submission.

EXP-005 — Correctness against official fixtures.

EXP-006 — Conservative selector validation.

EXP-007 — CPU and memory profiling.

Every experiment must record:

- Version.
- Input.
- Configuration.
- Reproduction command.
- Output.
- Result.
- Official score where applicable.
- Interpretation.
- Next action.

Unexecuted experiments remain PLANNED.

# 16. ACCEPTANCE CRITERIA FOR L01

L01 is complete only when:

1. All available archives are inspected.
2. Missing ZIPs are documented.
3. Official starter materials are inventoried.
4. Actual scoring rules are confirmed.
5. The build environment is operational.
6. The baseline is reproduced or its blocker is precisely documented.
7. The official input/output contract is understood.
8. A minimal valid submission exists or its implementation path is documented.
9. The benchmark and experiment ledgers exist.
10. The central project state is maintained.
11. The seven engineering responsibilities are allocated.
12. No unverified architectural assumption is treated as fact.

# 17. REQUIRED L01 DELIVERABLES

Produce:

1. Seven-archive intake report.
2. Archive integrity and checksum report.
3. Official starter inventory.
4. Official specification reconciliation.
5. Scoring formula verification.
6. Environment setup report.
7. Baseline reproduction report.
8. Input/output contract report.
9. Initial working submission.
10. Project state.
11. Decision ledger.
12. Experiment ledger.
13. Agent responsibility matrix.
14. Phase 2 task DAG.
15. Outstanding blocker register.

# FINAL DIRECTIVE

We now move from intelligence to execution.

Do not continue building documentation for its own sake.

Do not wait for every research question to be resolved.

Establish the official environment.

Reproduce the baseline.

Create a valid working submission.

Measure everything.

Only then introduce the strongest validated improvements.

The competition score, not the number of agents or complexity of the architecture, determines success.

L01 begins now.


Execute L01 now.

Use the actual official RWX starter files and available Phase 1 research archives. Start environment setup, inspect the competition files, verify the scoring mechanism, reproduce the baseline and establish a valid initial submission.

Do not wait for all seven ZIP archives. Process those already available while continuing baseline setup.

Do not invent execution results or claim success without evidence.

Maintain the project state, decision ledger, benchmark ledger and task DAG.

When L01 is complete, provide me with:
1. Environment setup report.
2. Official starter file inventory.
3. Seven-agent archive ingestion status.
4. Baseline reproduction results.
5. Initial submission status.
6. Current blockers and risks.
7. Recommended next implementation steps.

Stop before L02. Await the next engineering protocol.

<!-- END Untitled-1.md -->


<!-- BEGIN Untitled-2.md -->


# BUILDERS BUILDATHON 2026
# L02 — RWX CORE IMPLEMENTATION & SAFE TEST-SELECTION ENGINE

PROTOCOL ID: L02
VERSION: 1.0
PHASE: Phase 2 — Local Engineering
TARGET: RWX — BLAST RADIUS
RECIPIENT: Main IDE Chief Engineering Agent
AUTHORITY: Chief Architect
PRIORITY: HIGH

---

## 1. MISSION

Implement the first functional RWX solution using the official starter environment.

L01 established the environment, inspected the official materials and attempted baseline reproduction.

Now build the core execution pipeline.

The objective is to establish a valid, deterministic and independently testable submission that can:

1. Read competition inputs.
2. Parse commit patches.
3. Identify changed files.
4. Interpret test metadata.
5. Generate a defensible initial test-selection set.
6. Apply conservative fallback rules.
7. Assign selected tests to workers.
8. Generate valid official JSON output.
9. Pass the official evaluator.
10. Produce measurable benchmark results.

Do not attempt to implement every advanced research concept immediately.

Establish a reliable core before introducing advanced static analysis and graph engineering.

## 2. PRECONDITION — VERIFY L01

Before starting:

Inspect the latest PROJECT_STATE.md.

Confirm:

- Official starter files were inspected.
- The actual input/output contract is known.
- The official scoring implementation is understood.
- The baseline was reproduced or its blocker documented.
- The execution environment is operational.
- The project repository exists.

If L01 has not established these conditions, complete the missing foundational tasks first.

Do not invent missing file structures, APIs or commands.

Do not wait for research ZIPs that have not arrived if the official starter is already usable.

## 3. ARCHITECTURE AND MODULE OWNERSHIP

Implement the core components.

### MODULE A — INPUT VALIDATION

Responsibilities:
- Validate all expected input files.
- Load tests.json.
- Validate test identifiers.
- Validate test durations.
- Identify commit patches.
- Detect missing or malformed data.
- Establish consistent internal representations.

Define strict error handling.

### MODULE B — PATCH PROCESSING

Responsibilities:
- Read unified diffs.
- Identify changed files.
- Track file additions and deletions.
- Track removed and added lines.
- Handle supported rename formats.
- Detect unsupported patch structures.

Implement reliable patch parsing using the actual official input format.

Do not invent patch-specific failure-test answers.

### MODULE C — CHANGESET REPRESENTATION

Create a normalized ChangeSet representation.

Include appropriate fields such as:
- Commit identifier.
- Changed paths.
- Added lines.
- Removed lines.
- File operation type.
- Parse status.
- Unknown or unresolved information.

Ensure this representation can later support L03 static analysis without redesigning the entire application.

### MODULE D — INITIAL TEST-SELECTION ENGINE

Implement a conservative first selection policy.

Start with a simple, explainable approach using officially permitted information.

Potential evidence:
- Direct changed-file relationships.
- Officially permitted baseline coverage.
- Permitted import relationships.
- Available fixture mappings.

Do not prematurely use NameRTS, complex graphs or learned prediction.

Where dependency certainty is insufficient, conservatively expand the candidate selection.

Where the analysis cannot safely establish a useful subset, use a clearly defined fallback.

Any full-test fallback must be checked against runtime feasibility.

Document every selection decision.

### MODULE E — SELECTION VALIDATOR

Verify:
- All selected identifiers exist.
- No duplicate test identifiers.
- No unsupported test numbers.
- No invalid empty values.
- Deterministic output.
- Correct commit association.

Produce a structured SelectedTests representation.

### MODULE F — WORKER SCHEDULER

Implement an initial scheduling strategy.

Compare:
- One worker.
- A small fixed worker count.
- Duration-aware allocation.
- Greedy load balancing.

Account for:
- Two-second cost per nonempty worker.
- Maximum eight workers.
- Busiest-worker simulated duration.
- CPU usage.

Do not automatically create eight workers.

Choose the approach based on the official score.

### MODULE G — OUTPUT SERIALIZER

Implement the exact output contract established by L01.

Validate:
- JSON syntax.
- Exact field names.
- Correct commit identifiers.
- Correct worker structure.
- Valid test identifiers.
- One output line per commit.
- Maximum worker count.
- No empty workers.
- No diagnostic messages on stdout.

### MODULE H — ERROR AND FALLBACK MANAGEMENT

Implement predictable handling for:
- Invalid patches.
- Missing metadata.
- Unknown files.
- Incomplete dependency information.
- Invalid test identifiers.
- Internal parsing failures.
- Serialization failures.

Do not silently produce incorrect output.

Ensure fallback decisions preserve compliance and are tested.

## 4. INITIAL IMPLEMENTATION PRIORITY

Follow this order:

P0:
- Input reading.
- Input validation.
- Patch parsing.
- Normalized changeset.
- Initial selector.
- Worker scheduler.
- Output serialization.
- End-to-end execution.

P1:
- Better use of permitted baseline coverage.
- Import-map integration.
- Fixture-map integration.
- Improved candidate selection.
- More efficient scheduling.

P2:
- Interfaces ready for L03 static analysis.
- Interfaces ready for L04 graph engineering.
- Improved caching and compact data structures.

Do not implement P2 before P0 works.

## 5. TESTING REQUIREMENTS

Create tests for:

INPUT:
- Valid patch.
- Empty patch.
- Multiple-file patch.
- Deleted file.
- Added file.
- Rename.
- Malformed diff.

TEST METADATA:
- Valid identifiers.
- Duplicate identifiers.
- Missing values.
- Invalid durations.
- Empty test suite.

SELECTION:
- Direct changed-file relationships.
- Coverage matches.
- Missing coverage.
- Unknown dependencies.
- Conservative fallback.

SCHEDULING:
- Zero selected tests.
- One selected test.
- Unequal durations.
- Many short tests.
- A small number of long tests.
- Maximum worker boundary.

OUTPUT:
- Valid JSON.
- Exact schema.
- Correct ordering.
- No duplicates.
- Correct line count.

These tests must be grounded in the actual official contract.

## 6. OFFICIAL BENCHMARKING

Use the actual official evaluator.

For every experiment record:

- Source revision.
- Architecture version.
- Configuration.
- Dataset.
- Worker count.
- Selected test count.
- Missed failing tests.
- Simulated CI seconds.
- Worker overhead.
- CPU seconds.
- Wall-clock time.
- Peak memory.
- Official aggregate score.

Do not confuse local execution time with simulated CI time.

Run the same inputs and evaluation conditions when comparing architectures.

Do not claim zero misses unless verified by the available official evaluation.

## 7. AGENTIC DEVELOPMENT INTEGRATION

Use the nine-part operating architecture where it adds concrete value.

Allocate local agent responsibilities:

- Chief architect: controls interfaces and integration.
- Optimization agent: validates score calculations.
- Static-analysis agent: owns patch and Python analysis.
- Graph agent: prepares the later L03/L04 integration boundaries.
- Research agent: validates algorithmic choices.
- Harness agent: maintains execution and benchmark automation.
- Red-team agent: independently challenges implementation correctness.

Use high-capability models for architecture and difficult debugging.

Use execution-tier agents for bounded implementation and routine tests.

Every task must have an acceptance condition.

Use separate branches or worktrees where necessary.

## 8. REQUIRED PROJECT STRUCTURE

Follow the inspected official starter structure wherever possible.

Organize our implementation into clear modules for:

- Input validation.
- Patch processing.
- Changeset representation.
- Test selection.
- Worker scheduling.
- Output serialization.
- Error management.
- Tests and benchmark support.

Do not restructure the starter unnecessarily.

Keep all final submission files within the official repository restrictions.

## 9. L02 ACCEPTANCE GATE

L02 is complete when:

1. The application reads actual competition inputs.
2. Patches are parsed.
3. Changesets are created.
4. A valid initial test-selection policy operates.
5. Fallback behaviour is implemented.
6. Worker scheduling operates.
7. JSON output follows the exact official contract.
8. The official evaluator accepts the submission.
9. Benchmark results are recorded.
10. No known correctness or compliance failure is silently ignored.
11. The architecture provides clean interfaces for L03 and L04.

If a criterion cannot be met, document the exact blocker and evidence.

## 10. REQUIRED REPORT

Return:

- Implemented modules.
- File inventory.
- Source revision.
- Official command used.
- Successful and failed tests.
- Official score, if measured.
- CPU and memory measurements.
- Known limitations.
- Unresolved risks.
- L03 integration requirements.
- Updated PROJECT_STATE.md.

Do not claim completion based only on successful compilation.

A successful official evaluation is stronger evidence than an agent's code review.

---

# FINAL DIRECTIVE

Build the smallest complete, compliant and measurable RWX system.

Make every module deterministic.

Keep the implementation understandable.

Preserve a conservative fallback.

Prepare clean interfaces for the advanced static-analysis and graph architectures.

Do not let sophisticated optimization compromise the correctness of the first working submission.

L02 begins after the L01 prerequisites are satisfied.

<!-- END Untitled-2.md -->


<!-- BEGIN Untitled-3.md -->


# BUILDERS BUILDATHON 2026
# L03 — PYTHON STATIC ANALYSIS, AST INTELLIGENCE & SYMBOL-LEVEL DEPENDENCY ENGINE

PROTOCOL ID: L03
VERSION: 1.0
PHASE: Phase 2 — Local Engineering
TARGET: RWX — BLAST RADIUS
RECIPIENT: MAIN IDE CHIEF ENGINEERING AGENT
AUTHORITY: CENTRAL ARCHITECT
PRIORITY: HIGH

---

## 1. MISSION

Develop the Python static-analysis subsystem that understands code changes at a more precise level than changed-file identification.

Our objective is to establish relationships between:

- Python modules.
- Classes.
- Functions.
- Methods.
- Symbols.
- Names.
- Imports.
- Definitions.
- References.
- Available test metadata.

This subsystem must analyze the actual pinned sqlglot source code and produce structured dependency evidence.

It will provide the foundation for L04 graph engineering and subsequent safe test selection.

Do not assume AST analysis alone can completely resolve Python dependencies.

Handle uncertainty explicitly.

Preserve the existing working L02 implementation.

Use a separate development branch or worktree where appropriate.

---

## 2. PRECONDITIONS

Before implementation:

1. Inspect the actual L02 project.
2. Read its PROJECT_STATE.md.
3. Identify existing patch-parser interfaces.
4. Identify existing changeset structures.
5. Inspect the actual pinned Python version and sqlglot source.
6. Identify currently available metadata and coverage artifacts.
7. Review the seven Phase 1 research packages that have actually arrived.
8. Confirm official rules governing baseline-derived metadata.

Do not invent filenames or module interfaces.

Adapt the proposed design to the existing working repository.

If L02 has not passed its acceptance criteria, preserve the working implementation and repair essential prerequisites first.

---

## 3. PYTHON AST ENGINE

Implement a lightweight source-analysis engine.

Use the actual Python environment specified by the official starter.

Investigate Python's standard-library AST facilities before adding dependencies.

Required capabilities:

### A. Module extraction

Identify:
- Module name.
- Source path.
- Package relationship.
- Relative imports.
- Absolute imports.
- Module definitions.

### B. Class extraction

Identify:
- Class name.
- Parent classes.
- Class attributes.
- Methods.
- Decorators.
- Nested definitions where relevant.
- Source locations.

### C. Function extraction

Identify:
- Function name.
- Parameters.
- Return annotations.
- Decorators.
- Nested functions.
- Source line ranges.
- Containing module or class.

### D. Import extraction

Identify:
- Import statements.
- Imported modules.
- Aliases.
- From-import relationships.
- Relative imports.
- Wildcard imports.
- Imports inside functions.
- Conditional imports where detectable.

### E. Name and symbol extraction

Investigate:
- Name definitions.
- Name references.
- Assignment targets.
- Function calls.
- Attribute access.
- Global declarations.
- Nonlocal declarations.
- Scope relationships.

Record source locations and structural context.

Do not equate every textual name match with a real semantic dependency.

---

## 4. SYMBOL INTELLIGENCE MODEL

Define a normalized internal representation.

Possible structures:

Symbol:
- symbol_id
- qualified_name
- symbol_type
- module_path
- parent_symbol
- start_line
- end_line
- definition_location
- decorators
- confidence
- analysis_status

Definition:
- defining_symbol
- defined_name
- scope
- source_location

Reference:
- referencing_symbol
- referenced_name
- source_location
- reference_type
- resolution_status

Import:
- importing_module
- imported_module
- imported_name
- alias
- import_type
- source_location

These are proposed schemas.

Refine them to avoid unnecessary fields and excessive memory consumption.

Use deterministic identifiers and stable serialization.

---

## 5. SCOPE AND NAME RESOLUTION

Investigate correct handling of:

- Module scope.
- Class scope.
- Function scope.
- Nested function scope.
- Local variables.
- Global variables.
- Nonlocal variables.
- Shadowed names.
- Imported aliases.
- Re-exported symbols.
- Inherited methods.
- Assignment-based definitions.

Where resolution is impossible, preserve an unresolved reference rather than inventing a target.

Distinguish:
- Resolved dependency.
- Potential dependency.
- Textual reference.
- Unknown dependency.

Do not build an unreliable full Python semantic analyzer just to produce more edges.

---

## 6. PYTHON DYNAMIC BEHAVIOUR

Explicitly detect or flag potentially problematic constructs.

Investigate:

- getattr.
- setattr.
- Dynamic imports.
- importlib.
- Reflection.
- Monkey patching.
- Decorators.
- Metaclasses.
- Descriptors.
- Dynamic attribute access.
- Inheritance.
- Callbacks.
- Dynamic dispatch.
- Shared mutable variables.
- Import-time side effects.

These are not necessarily implementation errors.

They represent cases where static inference may be incomplete.

For every detected dynamic construct:

1. Record its location.
2. Identify its potential dependency implications.
3. Mark the analysis uncertainty.
4. Provide structured evidence to the impact engine.
5. Allow the downstream safety policy to decide how broadly to select tests.

Do not silently discard unresolved dynamic relationships.

---

## 7. IMPORT AND MODULE DEPENDENCY ANALYSIS

Build a baseline module dependency index.

Investigate:
- Direct imports.
- Relative imports.
- Re-exports.
- Aliases.
- Transitive imports.
- Cycles.
- Import-time execution.

Produce both forward and reverse indexes where useful.

Avoid assuming that importing a module means every function in that module is necessarily affected by every change.

The final dependency semantics must be conservative but computationally efficient.

---

## 8. CHANGE-TO-SYMBOL MAPPING

Integrate with the L02 patch parser.

The input is the normalized ChangeSet.

Investigate how to map:

- Added lines.
- Removed lines.
- Modified lines.
- Added functions.
- Modified functions.
- Deleted functions.
- Modified classes.
- Modified imports.
- Module-level changes.

Use the original pinned source as the baseline for mapping removed and modified lines.

Consider how added code can be associated with its containing structural element.

Return:

ChangedSymbolEvidence:
- commit_id
- changed_file
- affected_symbols
- changed_imports
- module_level_changes
- unresolved_ranges
- dynamic_analysis_flags
- confidence
- analysis_status

Use only information derived from permitted source and patch analysis.

Do not construct or store mappings from specific competition patches to their known failing tests.

---

## 9. NAMERTS-INSPIRED ANALYSIS

Use the P05 research investigation of:

Names Are All You Need: Effective and Safe Regression Test Selection for Python.

https://arxiv.org/abs/2605.25356

Investigate the feasibility of adapting its name-definition and name-usage approach.

Potential relationships:

- Code element defines name.
- Code element uses name.
- Test accesses name.
- Module imports name.
- Code elements share a dependency through a name.

Determine which parts should be implemented in L03 and which should wait for L04 graph engineering.

Do not copy the entire research implementation blindly.

Do not assume its published 99.6% safety result transfers to RWX.

Do not introduce expensive bytecode instrumentation without a demonstrated need and an official-rule audit.

The immediate goal is to generate reliable structured symbol and reference information.

---

## 10. BUILD-TIME METADATA GENERATION

Determine which metadata should be generated from the permitted pinned baseline during the official build phase.

Potential artifacts:

- module_index.json
- symbol_index.json
- import_index.json
- name_definition_index.json
- name_usage_index.json
- dynamic_feature_index.json

These are proposed examples, not mandatory filenames.

For every artifact specify:

- Generation command.
- Input files.
- Data schema.
- Serialization.
- Expected size.
- Runtime consumer.
- Compliance basis.

Use deterministic generation.

Do not include patch-specific test failure answers.

Ensure all artifact sizes remain compatible with the official repository limit.

---

## 11. CHANGE IMPACT EVIDENCE INTERFACE

L03 must produce structured evidence for L04.

Proposed interface:

StaticAnalyzer.analyze_repository(source_root) -> BaselineMetadata

StaticAnalyzer.analyze_change(changeset, baseline_metadata) -> ChangeEvidence

The output should identify:

- Changed modules.
- Changed symbols.
- Changed imports.
- Direct definitions.
- Potential references.
- Unresolved references.
- Dynamic constructs.
- Uncertainty indicators.
- Relevant baseline metadata identifiers.

A downstream graph engine must be able to consume the result without understanding internal AST implementation details.

Keep interfaces deterministic and versioned.

---

## 12. PERFORMANCE REQUIREMENTS

Optimize for the official build and runtime environment.

Investigate:

- AST traversal cost.
- Symbol extraction cost.
- Import resolution cost.
- Memory usage.
- Index size.
- Serialization overhead.
- Startup cost.
- Patch-specific analysis cost.

Prefer:

- Standard-library parsing where sufficient.
- Single-pass AST traversal where practical.
- Compact identifiers.
- Efficient reverse indexes.
- Avoidance of repeated parsing.
- Deterministic ordering.

Do not parse the entire repository repeatedly for every commit when suitable permitted baseline metadata can be generated once.

Do not assume that a more detailed semantic model automatically creates a better competition score.

---

## 13. STATIC-ANALYSIS TEST SUITE

Create tests for:

### AST extraction
- Simple functions.
- Nested functions.
- Classes and methods.
- Inheritance.
- Decorators.
- Async functions.
- Multiple assignments.

### Imports
- Absolute imports.
- Relative imports.
- Aliases.
- Re-exports.
- Wildcard imports.
- Circular imports.
- Conditional imports.

### Scope
- Shadowed names.
- Local and global variables.
- Nonlocal declarations.
- Class attributes.
- Nested scopes.

### Dynamic constructs
- getattr and setattr.
- Dynamic import.
- Reflection.
- Monkey patching.
- Descriptors.
- Inherited method resolution.

### Patch mapping
- Added function.
- Deleted function.
- Modified signature.
- Modified method.
- Changed imports.
- Multi-file changes.
- Renamed files.
- Changes outside recognizable definitions.

### Reliability
- Malformed source.
- Unsupported syntax.
- Corrupt files.
- Unresolved names.
- Missing metadata.

Clearly distinguish tests of AST correctness from tests of actual test-selection safety.

---

## 14. L03 ACCEPTANCE GATE

Complete only when:

1. The actual pinned source can be analyzed.
2. AST extraction works.
3. Module and symbol indexes are generated.
4. Import relationships are extracted.
5. Scope-sensitive references are represented.
6. Unresolved relationships are recorded.
7. Dynamic behaviour is flagged.
8. Patch changes are mapped to structural elements.
9. Baseline metadata generation is deterministic.
10. Artifact sizes are measured.
11. CPU and memory are profiled.
12. L04 interfaces are implemented and documented.
13. Existing L02 functionality remains intact.
14. All changes pass the relevant tests.

Do not claim full semantic dependency resolution.

---

## 15. REQUIRED DELIVERABLES

Provide:

- Implemented static-analysis module.
- AST extraction.
- Module index.
- Symbol index.
- Import index.
- Name definition/reference representation.
- Changed-symbol analysis.
- Dynamic uncertainty report.
- Build-time metadata generator.
- L04 interface specification.
- Unit-test report.
- Performance measurements.
- Compliance assessment.
- Updated PROJECT_STATE.md.
- Updated decision and experiment ledgers.
- L03 completion report.

---

# FINAL DIRECTIVE

Build a lightweight but structurally intelligent Python analysis subsystem.

Its purpose is not merely to understand source code.

Its purpose is to identify which parts of the source have changed and provide reliable dependency evidence for subsequent test-impact analysis.

Be precise about resolved and unresolved relationships.

Do not confuse names with semantic dependencies.

Do not compromise safety to create an impressive graph.

Maintain the working L02 submission throughout implementation.

L03 begins now.

<!-- END Untitled-3.md -->


<!-- BEGIN Untitled-4.md -->


# BUILDERS BUILDATHON 2026
# L04 — GRAPH ENGINEERING, DEPENDENCY PROPAGATION & TEST-IMPACT INTELLIGENCE

PROTOCOL ID: L04
VERSION: 1.0
PHASE: Phase 2 — Local Engineering
TARGET: RWX — BLAST RADIUS
RECIPIENT: MAIN IDE CHIEF ENGINEERING AGENT
AUTHORITY: CENTRAL ARCHITECT
PRIORITY: HIGH

---

## 1. MISSION

Develop the graph-based dependency and impact-analysis subsystem for the RWX submission.

The subsystem must connect:

- Changed source files.
- Python modules.
- Functions and methods.
- Classes.
- Names and symbols.
- Import relationships.
- Baseline test coverage.
- Test files.
- Fixture relationships.

The purpose is to determine which tests may be affected by a code change.

Use the actual outputs of L03.

Do not independently rebuild an incompatible duplicate of the static-analysis subsystem.

Design graph representations that are computationally efficient, deterministic, compact and compatible with the official execution environment.

L04 must produce structured impact evidence for L05.

Do not independently make the final test-selection decision here.

---

## 2. PRECONDITIONS

Before starting:

1. Read PROJECT_STATE.md.
2. Inspect the current L02 implementation.
3. Verify L02 acceptance status.
4. Inspect the actual L03 implementation.
5. Verify AST extraction and metadata generation.
6. Examine the real generated metadata schemas.
7. Identify the actual available coverage and fixture mappings.
8. Verify the official rules governing every precomputed artifact.
9. Review the P07 and P08 graph architecture decisions.
10. Identify existing data structures and interfaces.

If L03 is incomplete, do not assume its proposed interfaces are operational.

Repair essential interfaces or isolate the graph module behind an explicit adapter.

Preserve existing working code.

Do not replace verified functionality without a measurable reason.

---

## 3. GRAPH ARCHITECTURE

Investigate a unified logical dependency model.

Possible node types:

A. FILE
B. MODULE
C. CLASS
D. FUNCTION
E. METHOD
F. SYMBOL
G. NAME
H. TEST
I. FIXTURE

Every node must have:

- Stable identifier.
- Node type.
- Source or test location.
- Relevant parent identifier.
- Metadata reference.
- Provenance.
- Analysis status.

Avoid storing large redundant objects in every graph node.

Use compact identifiers and separate metadata indexes.

### Edge architecture

Investigate typed directed relationships.

Potential edge types:

- CONTAINS
- DEFINES
- USES
- IMPORTS
- REEXPORTS
- REFERENCES
- INHERITS
- COVERS
- ACCESSES
- USES_FIXTURE
- DEPENDS_ON

Do not generate every relationship indiscriminately.

Every edge must have a defined semantic meaning and a documented source.

For each edge specify:

1. Source node.
2. Destination node.
3. Relationship type.
4. Direction.
5. Provenance.
6. Whether the relationship is direct or inferred.
7. Whether it is exact, approximate or unresolved.

Do not confuse syntactic references with guaranteed semantic dependencies.

---

## 4. GRAPH FAMILY A — FILE AND MODULE GRAPH

Construct a baseline module dependency representation.

Nodes:
- Source files.
- Python modules.

Edges:
- Import.
- Relative import.
- Re-export.
- Package relationships.

Build:

1. Forward dependency index.
2. Reverse dependency index.
3. Module-to-file index.
4. File-to-module index.
5. Cyclic dependency detection.

Investigate direct and transitive imports.

For a changed module, identify modules that may depend on it.

Consider that simple import relationships can over-select tests because importing a module does not imply every function in that module is affected.

Preserve this graph as a useful coarse-grained dependency layer.

Do not discard it merely because finer-grained graphs exist.

---

## 5. GRAPH FAMILY B — SYMBOL AND NAME GRAPH

Use the L03 static-analysis outputs.

Construct relationships between:

- Modules.
- Classes.
- Functions.
- Methods.
- Symbol definitions.
- Name definitions.
- Name references.

Investigate a NameRTS-inspired bipartite representation:

CODE ELEMENTS ↔ NAMES

Example logical relationships:

Function A defines name X.

Function B references name X.

Test C accesses name X.

Module D imports name X.

The graph should support discovering potentially relevant code elements through shared names and dependencies.

Determine:

- How names are normalized.
- How qualified names are represented.
- How aliases are handled.
- How shadowed names are distinguished.
- How scopes are resolved.
- How unresolved references are recorded.
- How false edges are limited.

Do not blindly equate equal textual names in unrelated scopes.

Preserve scope and provenance information.

---

## 6. GRAPH FAMILY C — TEST AND COVERAGE GRAPH

Integrate only baseline coverage data that has been verified as permitted by the official competition rules.

Potential relationships:

TEST → FILE

TEST → FUNCTION

TEST → CLASS

TEST → SYMBOL

Represent test-to-source relationships explicitly.

Investigate:

- Test coverage at file granularity.
- Function-level coverage.
- Line-level coverage where available.
- Multiple tests covering the same function.
- One test covering multiple modules.
- Test setup and teardown.
- Shared fixtures.
- Missing coverage records.

Build efficient reverse indexes:

SOURCE_FILE → TESTS

SYMBOL → TESTS

MODULE → TESTS

These indexes should allow impact analysis to discover tests without scanning the entire test suite repeatedly.

Distinguish actual observed coverage from inferred relationships.

Do not treat absence of observed coverage as proof of absence of dependency.

---

## 7. GRAPH FAMILY D — FIXTURE RELATIONSHIPS

Investigate the fixture metadata available in the official challenge.

Determine which relationships can be extracted reliably.

Potential structures:

- Test-to-fixture.
- Fixture-to-fixture.
- Fixture-to-module.
- Fixture-to-resource.
- Shared fixture dependencies.

Preserve provenance.

Investigate indirect relationships where tests depend on fixtures that initialize or import relevant code.

Do not invent fixture relationships from textual similarity alone.

Any unsupported fixture mapping must be marked unresolved.

---

## 8. GRAPH CONSTRUCTION PIPELINE

Design a deterministic graph-generation process.

Proposed sequence:

1. Read L03 baseline metadata.
2. Read permitted coverage metadata.
3. Read permitted fixture metadata.
4. Normalize identifiers.
5. Create source nodes.
6. Create symbol and name nodes.
7. Create dependency edges.
8. Create test nodes.
9. Create coverage edges.
10. Create fixture edges.
11. Build forward indexes.
12. Build reverse indexes.
13. Validate relationships.
14. Detect malformed records.
15. Serialize the resulting metadata.

Ensure that all generated artifacts are reproducible from the same pinned baseline and configuration.

Do not construct patch-specific failure-to-test lookup tables.

Check the compliance basis for every generated artifact.

---

## 9. CHANGE IMPACT PROPAGATION

Integrate with L03 ChangedSymbolEvidence.

Input:

- Changeset.
- Changed files.
- Changed modules.
- Changed symbols.
- Changed imports.
- Dynamic-feature indicators.
- Unresolved references.

Investigate how to propagate change impact.

Potential approaches:

A. Direct file-level reverse lookup.

B. Direct symbol-level reverse lookup.

C. Import dependency expansion.

D. Name-definition/name-usage propagation.

E. Coverage reverse lookup.

F. Fixture expansion.

G. Combined multi-layer reachability.

For every propagation step:

- Explain the edge being traversed.
- Define traversal direction.
- Define visited-node behaviour.
- Prevent infinite cycles.
- Preserve evidence provenance.
- Avoid unnecessary duplicate exploration.
- Record unresolved relationships.

Do not automatically traverse every edge type.

Design explicit propagation rules.

---

## 10. GRAPH TRAVERSAL AND ALGORITHMS

Compare:

- Breadth-first search.
- Depth-first search.
- Multi-source reachability.
- Reverse dependency traversal.
- Bounded propagation.
- Strongly connected components.
- Incremental reachability.
- Worklist algorithms.
- Bitset-based propagation.

For each algorithm evaluate:

- Time complexity.
- Memory complexity.
- Startup overhead.
- Traversal overhead.
- Worst-case behaviour.
- Determinism.
- Suitability for this repository.

Do not add graph database technology unless a demonstrated requirement justifies it.

Prefer lightweight in-memory structures if they offer better performance.

---

## 11. GRAPH PRUNING AND PRECISION

Investigate how to reduce unnecessary graph expansion.

Potential methods:

- Scope-aware name resolution.
- Module boundaries.
- Symbol ownership.
- Relationship-type filtering.
- Duplicate-edge elimination.
- Context-aware propagation.
- Relevant subgraph extraction.

Every pruning rule must identify what it removes and why removal is justified.

A pruning optimization must not silently remove an essential dependency.

Any uncertain relationship should be represented explicitly and passed to L05.

Do not claim formal safety from an empirical pruning heuristic.

---

## 12. IMPACT EVIDENCE MODEL

Produce a structured output for L05.

Suggested interface:

ImpactEvidence:
- commit_id
- impacted_files
- impacted_modules
- impacted_symbols
- candidate_tests
- evidence_paths
- direct_relationships
- transitive_relationships
- coverage_evidence
- fixture_evidence
- unresolved_relationships
- dynamic_feature_flags
- graph_analysis_status

Each candidate-test record should preserve:

- Test identifier.
- Supporting source nodes.
- Relationship types.
- Evidence provenance.
- Impact depth.
- Uncertainty indicators.

Do not assign arbitrary numerical confidence values without a defensible calibration method.

L05 owns the actual final inclusion and fallback policy.

---

## 13. DATA STRUCTURES AND STORAGE

Compare:

A. Python dictionaries and sets.

B. Adjacency lists.

C. Reverse adjacency indexes.

D. Compact integer identifiers.

E. Sorted edge arrays.

F. Bitsets.

G. Compressed sparse representations.

H. JSON metadata.

I. Binary serialization, if supported and justified.

For every representation document:

- Construction complexity.
- Query complexity.
- Memory cost.
- Artifact size.
- Serialization overhead.
- Ease of debugging.
- Determinism.

Choose the smallest effective representation.

Ensure generated artifacts remain compatible with the official repository size limit.

---

## 14. INCREMENTAL RUNTIME ANALYSIS

The baseline graph should be precomputed where permitted.

At runtime:

1. Receive a new changeset.
2. Map changed files to baseline identifiers.
3. Map changed symbols where available.
4. Resolve known graph nodes.
5. Perform impact propagation.
6. Retrieve relevant test candidates.
7. Record unresolved or unsupported relationships.
8. Return ImpactEvidence.

Do not reconstruct the entire baseline graph for every commit.

Do not depend on runtime network access.

Do not introduce persistent runtime caches unless compatible with the actual filesystem restrictions.

---

## 15. FAILURE AND UNCERTAINTY HANDLING

Investigate:

- Missing graph nodes.
- Missing edges.
- Unknown symbols.
- Invalid identifiers.
- Cyclic imports.
- Unresolved aliases.
- Dynamic imports.
- Dynamic dispatch.
- Incomplete coverage.
- Missing fixtures.
- Stale metadata.
- Corrupt serialized graphs.
- Unsupported patch structures.

For each case:

- Detect the problem.
- Record its source.
- Classify its severity.
- Preserve unresolved evidence.
- Return a predictable result.

Never interpret a failed lookup as proof that no dependency exists.

Do not silently produce an empty impact set following a graph-processing error.

Pass uncertainty information to L05 for conservative selection.

---

## 16. GRAPH PERFORMANCE AND COMPLIANCE

Measure:

- Graph construction CPU time.
- Number of nodes.
- Number of edges.
- Metadata size.
- Serialization time.
- Graph loading time.
- Runtime propagation time.
- Peak memory.
- Number of visited nodes per commit.

Respect actual official constraints:

- Repository size.
- Build CPU and memory.
- Build duration.
- Runtime CPU and memory.
- No runtime network.
- Read-only runtime filesystem.
- Restricted temporary storage.
- Maximum process count.

Do not fabricate performance measurements.

Use the official runtime container when available.

Keep local M4 Pro measurements separate from competition-container measurements.

---

## 17. TEST REQUIREMENTS

Create graph-specific tests.

### Construction

- Every expected node type.
- Every supported edge type.
- Duplicate relationships.
- Missing metadata.
- Invalid references.
- Stable identifiers.

### Traversal

- Direct relationships.
- Multiple dependencies.
- Transitive dependencies.
- Cycles.
- Self-references.
- Reverse lookup.
- Multi-source propagation.

### Python relationships

- Aliased imports.
- Relative imports.
- Re-exports.
- Shadowed names.
- Inherited methods.
- Shared names.
- Dynamic constructs.

### Coverage and fixtures

- Multiple tests covering one source node.
- One test covering multiple source nodes.
- Missing coverage.
- Shared fixtures.
- Indirect dependencies.

### Runtime

- Unknown changed files.
- Unknown symbols.
- Missing baseline nodes.
- Corrupt graph artifacts.
- Large change sets.

Ensure all results are deterministic.

---

## 18. L04 ACCEPTANCE GATE

Complete only when:

1. L03 interfaces are correctly integrated.
2. Graph schema is documented.
3. Node and edge types have defined semantics.
4. Baseline graph construction works.
5. Reverse indexes work.
6. Coverage relationships are incorporated where permitted.
7. Fixture relationships are incorporated where supported.
8. Change-impact propagation operates.
9. Cycles are handled.
10. Unresolved dependencies are preserved.
11. ImpactEvidence is produced.
12. Graph traversal is tested.
13. Memory and CPU are measured.
14. Artifact sizes are checked.
15. Compliance is verified.
16. Existing L02 and L03 functionality remains intact.
17. L05 integration contracts are complete.

---

## 19. REQUIRED DELIVERABLES

Provide:

- Graph architecture.
- Graph schema.
- Node and edge registry.
- Build-time graph generator.
- Serialized dependency indexes.
- Runtime impact propagation engine.
- Test and coverage relationships.
- Fixture relationship support.
- Graph traversal algorithms.
- Uncertainty reporting.
- ImpactEvidence interface.
- Unit and integration tests.
- CPU and memory measurements.
- Compliance assessment.
- Updated PROJECT_STATE.md.
- Updated decision and experiment ledgers.
- L04 completion report.

---

# FINAL DIRECTIVE

Build the dependency intelligence engine.

Use graphs because relationships matter, not because graph technology is fashionable.

Preserve evidence provenance.

Make traversal deterministic.

Prevent cycles and uncontrolled expansion.

Never mistake an absent edge for proof of no dependency.

Never create prohibited patch-specific lookup information.

Produce structured impact evidence that the subsequent selection policy can safely use.

Maintain the working L02 submission and all tested L03 functionality.

L04 begins only after its prerequisites are available and verified.

<!-- END Untitled-4.md -->


<!-- BEGIN Untitled-5.md -->


# BUILDERS BUILDATHON 2026
# L05 — SAFE TEST SELECTION, UNCERTAINTY INTELLIGENCE & CONSERVATIVE FALLBACK ENGINE

PROTOCOL ID: L05
VERSION: 1.0
PHASE: Phase 2 — Local Engineering
TARGET: RWX — BLAST RADIUS
RECIPIENT: MAIN IDE CHIEF ENGINEERING AGENT
AUTHORITY: CENTRAL ARCHITECT
PRIORITY: CRITICAL

---

## 1. MISSION

Implement the final test-selection decision engine.

The engine receives structured impact evidence from L04 and determines which competition test identifiers must be included in the submitted output.

Its objective is to minimize the official aggregate competition score while avoiding missed failing tests.

Official scoring includes a 300-second penalty for a commit that omits at least one failing test.

Therefore, selection aggressiveness must be balanced against safety.

The engine must:

1. Consume L04 ImpactEvidence.
2. Classify dependency evidence.
3. Identify mandatory candidate tests.
4. Resolve overlapping dependencies.
5. Handle unresolved relationships.
6. Detect uncertainty.
7. Decide when to expand the selection.
8. Apply conservative fallback rules.
9. Validate the final selected set.
10. Produce structured output for L06.

Do not allow this engine to make unsupported semantic assumptions.

Do not interpret the absence of a graph relationship as proof that a test cannot be affected.

---

## 2. PRECONDITIONS

Verify:

- L02's working execution pipeline.
- L03's static-analysis interfaces.
- L04's graph-impact interfaces.
- Official test metadata.
- Permitted coverage metadata.
- Exact competition scoring rules.

Inspect the actual implementation and schemas.

Do not assume proposed Phase 1 interfaces exist without verification.

If L04 is incomplete, preserve the working L02 selector and establish the required adapter.

Do not silently replace a functioning implementation.

---

## 3. EVIDENCE CLASSIFICATION ENGINE

Implement a structured evidence model.

Investigate the following categories.

### E1 — Direct change evidence

Examples:
- Test explicitly covers a modified source location.
- A changed file has a verified baseline test relationship.

### E2 — Static dependency evidence

Examples:
- Resolved imports.
- Resolved symbol references.
- Direct source dependencies.
- Class and method relationships.

### E3 — Graph propagation evidence

Examples:
- Transitive dependency paths.
- Reverse reachability.
- Name-definition/name-usage relationships.

### E4 — Coverage evidence

Examples:
- Test-to-file relationship.
- Test-to-function relationship.
- Test-to-symbol relationship.

### E5 — Fixture evidence

Examples:
- Test uses a relevant fixture.
- Fixture imports or initializes related modules.

### E6 — Uncertainty evidence

Examples:
- Dynamic imports.
- Unresolved symbols.
- Incomplete static relationships.
- Unsupported source changes.
- Missing metadata.

For each evidence record preserve:

- Test identifier.
- Evidence source.
- Relationship type.
- Source location where available.
- Dependency path.
- Provenance.
- Resolution status.
- Uncertainty indicators.

Do not invent arbitrary confidence scores.

Use categorical evidence and measurable calibration where numerical confidence is later required.

---

## 4. MANDATORY TEST INCLUSION

Define inclusion rules.

Tests supported by sufficiently strong dependency evidence must enter the candidate selection.

Examples include:

- Direct verified coverage of modified code.
- Verified dependency paths from changed code.
- Relevant baseline test relationships.
- Validated fixture relationships.

Avoid treating different evidence types as interchangeable.

Create an explicit policy table.

For each evidence category specify:

- Inclusion requirement.
- Whether propagation is required.
- Whether additional evidence is needed.
- Whether uncertainty causes expansion.
- Whether exclusion is permitted.
- How the rule is validated.

The policy must be deterministic.

---

## 5. DEPENDENCY EXPANSION

Investigate how evidence should be combined.

Potential expansion rules:

1. Changed file → directly related tests.
2. Changed module → reverse-import dependents.
3. Changed symbol → dependent code elements.
4. Changed name → relevant definition/usage relationships.
5. Impacted source → baseline-covered tests.
6. Impacted fixture → dependent tests.
7. Unresolved dependency → conservative candidate expansion.

Use the verified L04 graph interfaces.

Avoid unnecessary expansion through unrelated modules.

Preserve evidence paths for every candidate test.

Do not expand indefinitely through all edge types.

Use explicit propagation rules and cycle prevention.

---

## 6. UNCERTAINTY INTELLIGENCE ENGINE

Implement a structured uncertainty model.

Investigate:

- Unsupported patch formats.
- Unknown changed file types.
- Missing metadata.
- Dynamic imports.
- Reflection.
- getattr and setattr.
- Monkey patching.
- Inheritance uncertainty.
- Shared state.
- Dynamic dispatch.
- Unresolved names.
- Incomplete coverage.
- Unknown fixture relationships.
- Missing graph nodes.

Classify uncertainty:

U0 — No detected uncertainty.

U1 — Localized uncertainty.

U2 — Significant unresolved dependency.

U3 — Structural analysis failure or unsupported change.

For each category define a corresponding selection response.

These categories must be grounded in actual detected conditions, not arbitrary numerical probabilities.

The system must distinguish an unresolved relationship from a proven unrelated relationship.

---

## 7. CONSERVATIVE FALLBACK ENGINE

This is essential.

Design multiple fallback levels.

### FALLBACK A — Local expansion

Include all tests associated with the uncertain local module or dependency region.

### FALLBACK B — Expanded dependency closure

Include the broader relevant dependency region when direct analysis is incomplete.

### FALLBACK C — Broad test selection

Expand to all defensibly relevant tests when uncertainty crosses several modules or relationships.

### FALLBACK D — Full test suite

Use full-suite selection when the analysis cannot establish a reliable narrower set and runtime feasibility has been evaluated.

For every fallback specify:

- Trigger condition.
- Selection scope.
- Expected test count.
- Estimated simulated cost.
- Runtime implications.
- Compliance status.
- Validation requirement.

Do not assume full-suite execution is always feasible within the deadline.

Do not silently disable fallback because it increases the score.

Evaluate fallback choices using the official scoring function.

A fallback that avoids a missed-test penalty may still cause a runtime violation. Both must be evaluated.

---

## 8. SELECTION OPTIMIZATION

Once safety-relevant candidates are identified, investigate how unnecessary tests can be excluded.

Compare:

A. Conservative file-level selection.

B. Coverage-supported selection.

C. Static dependency selection.

D. Symbol-level selection.

E. Graph-reachability selection.

F. Hybrid evidence selection.

G. Uncertainty-driven expansion.

Do not use machine-learning predictions or arbitrary thresholds as the sole reason for excluding a potentially affected test.

Every exclusion policy must have an explicit justification.

Investigate how to balance:

- Number of selected tests.
- Simulated test duration.
- Missed failure penalty.
- Runtime reliability.
- CPU cost.

Optimize the total official objective, not merely selection precision.

---

## 9. DEDUPLICATION AND SET MANAGEMENT

Implement reliable set operations.

Ensure:

- Each test identifier appears at most once.
- Evidence from multiple paths is merged.
- Selection reasons are preserved.
- Ordering is deterministic.
- Unknown IDs are rejected or handled according to the official contract.
- Empty selection is represented correctly.

Maintain the distinction between:

- Candidate tests.
- Required tests.
- Uncertain tests.
- Selected tests.
- Excluded tests.

Do not lose evidence when merging candidate sets.

---

## 10. SELECTION EXPLANATION AND TRACEABILITY

Create an internal SelectionDecision record.

Suggested fields:

- commit_id
- selected_test_ids
- candidate_test_ids
- mandatory_test_ids
- uncertain_test_ids
- excluded_test_ids
- inclusion_reasons
- exclusion_reasons
- fallback_level
- analysis_status

The final competition JSON must still follow the exact official output contract.

Internal diagnostics must not contaminate stdout.

These records are for engineering validation and debugging.

---

## 11. SCORE-AWARE DECISION MODEL

Integrate the actual scoring formula.

Investigate the economic effect of:

- Adding one more test.
- Adding tests with different durations.
- Expanding an uncertain dependency region.
- Selecting all tests.
- Increasing the worker count later in L06.
- Missing one failing test.

Ensure that selection decisions can be evaluated independently from scheduling but are compatible with L06.

Do not prematurely implement worker allocation here.

Do not use an invented failure probability to justify aggressive exclusion.

Where exact failure risk is unknown, preserve the uncertainty and apply the documented conservative policy.

---

## 12. TESTING REQUIREMENTS

Create tests for:

### Evidence classification
- Direct coverage.
- Import evidence.
- Symbol relationships.
- Graph paths.
- Fixture relationships.
- Conflicting evidence.

### Selection
- Single candidate.
- Multiple candidates.
- Duplicate candidates.
- Overlapping dependency paths.
- Multiple changed files.
- No changed symbols.
- Unknown changed symbols.

### Uncertainty
- Dynamic import.
- Unresolved reference.
- Missing coverage.
- Missing fixture data.
- Incomplete graph.
- Unsupported patch.

### Fallback
- Local expansion.
- Dependency expansion.
- Broad selection.
- Full-suite selection.

### Safety
- Known relevant tests are included in available ground-truth cases.
- No unsupported selection exclusions.
- All fallback conditions work.
- Unknown dependencies are not silently ignored.

Use the official evaluator wherever ground truth is provided.

Do not claim that zero known misses proves zero risk on unseen changes.

---

## 13. PERFORMANCE VALIDATION

Measure:

- Evidence processing CPU.
- Candidate generation time.
- Deduplication cost.
- Dependency expansion cost.
- Fallback computation.
- Selected test count.
- Selection memory.
- Serialization overhead.

Investigate whether maintaining detailed inclusion explanations creates material overhead.

Diagnostics may be retained for development but should not create unnecessary runtime expense.

Preserve the official resource limits.

---

## 14. L05 ACCEPTANCE GATE

Complete only when:

1. L04 ImpactEvidence is consumed correctly.
2. Evidence categories are implemented.
3. Mandatory inclusion policies are explicit.
4. Dependency expansion is deterministic.
5. Uncertainty is represented.
6. All fallback levels are defined.
7. Selection is deterministic.
8. Duplicate IDs are removed.
9. Exclusions have traceable justification.
10. Official output compatibility is preserved.
11. Known ground-truth cases are validated.
12. Runtime and CPU costs are measured.
13. The L06 scheduler interface is complete.
14. The L02 working submission remains recoverable.

---

## 15. REQUIRED DELIVERABLES

Provide:

- Evidence classification module.
- Test inclusion policy.
- Dependency expansion engine.
- Uncertainty model.
- Conservative fallback engine.
- Selection decision engine.
- Candidate and selected-test representations.
- Deduplication logic.
- Traceability and diagnostic records.
- Unit and integration tests.
- Official correctness results, where available.
- CPU and memory measurements.
- Compliance review.
- Updated PROJECT_STATE.md.
- Updated decision and experiment ledgers.
- L05 completion report.

---

# FINAL DIRECTIVE

Your job is to turn uncertain code relationships into safe test-selection decisions.

Do not confuse predictions with guarantees.

Do not assume an unresolved dependency is irrelevant.

Do not optimize selection size while ignoring the 300-second missed-test penalty.

Build explicit, deterministic and auditable inclusion and fallback rules.

Maintain the working L02, L03 and L04 components.

L05 begins only after its required interfaces are operational.

<!-- END Untitled-5.md -->


<!-- BEGIN Untitled-6.md -->


# BUILDERS BUILDATHON 2026
# L06 — INTELLIGENT WORKER SCHEDULING, PARALLEL ALLOCATION & OFFICIAL SCORE OPTIMIZATION

PROTOCOL ID: L06
VERSION: 1.0
PHASE: Phase 2 — Local Engineering
TARGET: RWX — BLAST RADIUS
RECIPIENT: MAIN IDE CHIEF ENGINEERING AGENT
AUTHORITY: CENTRAL ARCHITECT
PRIORITY: HIGH

---

## 1. MISSION

Implement the intelligent worker scheduling engine for our RWX submission.

L05 determines which tests must be selected.

L06 determines how those selected tests should be distributed across the available workers.

The objective is to minimize the official aggregate competition score.

The system must account for:

1. Individual test durations.
2. Worker execution loads.
3. Maximum worker load.
4. Worker initialization overhead.
5. Maximum eight nonempty workers.
6. CPU consumed by the submitted program.
7. Empty-selection behaviour.
8. Deterministic assignment.

Do not assume that using eight workers is always optimal.

Do not assume that the shortest execution time automatically produces the lowest official score.

Use the actual official scoring implementation as the authority.

---

## 2. PRECONDITIONS

Verify:

- L02 working execution pipeline.
- L05 SelectedTests interface.
- Official tests.json.
- Official duration conversion rules.
- Exact worker assignment schema.
- Official SCORING.md.
- Official scorer implementation, if provided.

Verify the following published scoring details against the actual supplied scoring material:

- Two-second overhead per nonempty worker.
- Maximum eight workers.
- Busiest-worker execution load.
- CPU consumption added to the score.
- Empty-selection behaviour.

Do not rely on a previously summarized formula if the actual official files differ.

Preserve the working submission.

---

## 3. SELECTED TEST INPUT CONTRACT

Consume the L05 output.

Proposed interface:

SelectedTests:
- commit_id
- test_ids
- required_test_ids
- selection_status
- selection_reasons
- duration_metadata
- fallback_level

Verify all selected test identifiers against official test metadata.

Every selected test must be assigned exactly once.

Do not:
- Remove tests.
- Duplicate tests.
- Introduce unknown tests.
- Change test identifiers.
- Modify test durations.
- Invent test execution results.

If an input is invalid, report an explicit internal error and follow the official contract's permitted error behaviour.

---

## 4. EXACT SCORING MATHEMATICS

Reconstruct the official score.

Let:

T = selected tests.

K = number of nonempty workers.

d(t) = official duration of test t.

W_j = tests assigned to worker j.

L_j = sum of the official rounded durations of tests assigned to worker j.

M = maximum worker load.

H = worker overhead.

C = actual CPU cost contribution, as defined by the official evaluator.

Under the documented two-second worker-overhead model:

H = 2 × K seconds.

The worker-related cost is:

M + H.

The complete official scoring implementation must also account for missed-test penalties and CPU consumption exactly as specified.

For scheduling, the selected-test set is fixed.

The scheduling optimization objective for a given commit is to minimize the official score contribution affected by the worker assignment and actual CPU cost.

Do not omit any scoring term.

---

## 5. WORKER-COUNT OPTIMIZATION

Investigate every permitted worker count:

K = 1, 2, 3, 4, 5, 6, 7, 8.

For a test set containing n tests:

- Never create more than min(8,n) nonempty workers.
- Do not create empty workers.
- Return an empty worker array when no tests are selected, as specified by the official contract.

For each candidate K, estimate:

1. Maximum worker load.
2. Worker overhead.
3. Expected scheduling computation.
4. Memory use.
5. CPU overhead.
6. Final projected score contribution.

Select the best valid assignment.

Do not always choose the maximum worker count.

---

## 6. SCHEDULING ALGORITHMS

Implement and compare the following.

### A. Single-worker scheduling

All selected tests are placed in one worker.

Use as a simple baseline.

### B. Round-robin assignment

Distribute tests across workers in deterministic order.

Use as a comparison method, not an assumed winner.

### C. Greedy least-loaded scheduling

Assign the next test to the currently least-loaded worker.

### D. Longest Processing Time First — LPT

Procedure:

1. Sort tests by descending official duration.
2. Break equal-duration ties deterministically using test ID.
3. Assign each test to the worker with the lowest current load.
4. Break equal-load ties deterministically using worker index.
5. Update worker load.
6. Continue until every selected test is assigned.

### E. Duration-aware adaptive scheduling

Select a worker count based on the duration distribution and cost economics.

### F. Alternative optimization methods

Investigate:
- Greedy improvements.
- Local search.
- Pairwise swaps.
- Multi-start scheduling.
- Dynamic programming for small test sets.
- Exact partitioning for suitably small instances.

Do not implement expensive algorithms without demonstrating a benefit over LPT.

---

## 7. SCHEDULING ALGORITHM COMPARISON

For identical selected-test inputs, compare:

- Single worker.
- Round robin.
- Greedy least-loaded.
- LPT.
- Adaptive LPT.
- Improved scheduling.
- Exact or near-exact small-instance solutions.

Measure:

- Makespan.
- Worker overhead.
- Total assigned duration.
- Load imbalance.
- Scheduler CPU cost.
- Scheduler wall-clock time.
- Memory.
- Official score contribution.

Use identical test inputs.

Do not compare different selection sets when claiming that a scheduling algorithm is superior.

---

## 8. ADAPTIVE WORKER COUNT

Develop a policy that determines when more workers are beneficial.

Investigate:

- Number of selected tests.
- Total selected duration.
- Longest individual test.
- Duration distribution.
- Current maximum worker load.
- Additional worker overhead.

For each possible K, generate a candidate schedule.

Evaluate the complete worker-related scoring term.

Account separately for the scheduler's actual CPU consumption.

If the scheduler's CPU cost cannot be accurately predicted before execution, measure it through repeatable end-to-end runs.

Do not use unsupported probabilities or arbitrary thresholds as a substitute for score evaluation.

A simpler policy should be preferred when it achieves essentially identical scores with lower computational overhead.

---

## 9. IMPORTANT EXECUTION SEMANTICS

The `workers` array represents the competition's worker assignments.

Do not automatically implement a multiprocessing execution engine.

Determine from the actual starter and official evaluator whether workers are simulated assignments or actual processes that our program must launch.

Do not create subprocesses simply because the competition describes multiple workers.

The submitted program should only perform the actions required by the actual interface.

This distinction is important because unnecessary multiprocessing could increase our CPU consumption and worsen the score.

---

## 10. LOAD BALANCING AND DISTRIBUTION

Implement efficient balancing.

Investigate:

- Highly unequal durations.
- A few extremely long tests.
- Many short tests.
- Repeated equal durations.
- Small test sets.
- Large test sets.
- Skewed duration distributions.

Ensure:

1. Every selected test appears exactly once.
2. No worker is empty.
3. Every worker has a valid test list.
4. Loads are calculated using official duration semantics.
5. Output ordering is deterministic.
6. Worker assignments are reproducible.

Use compact data structures.

Avoid sorting or allocating unnecessary intermediate objects when the selected set is large.

---

## 11. SCORING FEEDBACK LOOP

Integrate the scheduling engine with the benchmark harness.

For every candidate scheduler record:

- Commit identifier.
- Selected test set.
- Algorithm.
- Worker count.
- Worker assignment.
- Load per worker.
- Maximum load.
- Worker overhead.
- CPU seconds.
- Official score.
- Result timestamp.

Use the official scorer wherever available.

If predicted and actual costs differ, determine why.

Never replace measured official scores with theoretical estimates.

---

## 12. EDGE-CASE TESTING

Create tests for:

- Zero selected tests.
- One selected test.
- Fewer than eight tests.
- Exactly eight tests.
- More than eight tests.
- Equal durations.
- Zero duration, if permitted.
- Extremely short durations.
- Long-running tests.
- Repeated duration values.
- Very uneven distributions.
- Large selected test sets.
- Missing duration metadata.
- Unknown test IDs.
- Duplicate input test IDs.

Validate the assignment invariants.

Use the exact official output schema.

---

## 13. PERFORMANCE OPTIMIZATION

Measure:

- Scheduler CPU time.
- Scheduler wall-clock time.
- Peak memory.
- Sorting time.
- Assignment time.
- JSON serialization.
- Aggregate CPU contribution.

Investigate:

- Sorting complexity.
- Heap-based least-loaded worker selection.
- Compact integer representations.
- Deterministic tie-breaking.
- Avoiding repeated scheduling of unchanged data.
- Reusing permissible baseline duration metadata.

Do not introduce complex data structures without measurable advantages.

The scheduler must remain comfortably inside the official runtime constraints.

---

## 14. L06 ACCEPTANCE GATE

Complete only when:

1. L05 SelectedTests is consumed correctly.
2. Exact official scoring semantics are implemented.
3. Every selected test is assigned exactly once.
4. No more than eight nonempty workers are created.
5. Empty workers are eliminated.
6. Zero-selection behaviour is correct.
7. Multiple worker counts can be evaluated.
8. LPT or another selected algorithm is implemented.
9. Adaptive worker-count decisions are deterministic.
10. Scheduler CPU overhead is measured.
11. The official output schema is satisfied.
12. All scheduling tests pass.
13. Official evaluation results are recorded where available.
14. L02–L05 remain operational.

---

## 15. REQUIRED DELIVERABLES

Provide:

- Worker scheduling module.
- Worker-count selection policy.
- LPT implementation or justified alternative.
- Scheduling comparison results.
- Worker-load calculation.
- Official scoring integration.
- Deterministic assignment.
- Edge-case tests.
- CPU and memory measurements.
- Benchmark report.
- L05 integration verification.
- Updated PROJECT_STATE.md.
- Updated decision and experiment ledgers.
- L06 completion report.

---

# FINAL DIRECTIVE

Our goal is not to maximize parallelism.

Our goal is to minimize the actual official score.

A worker is useful only when its reduction in execution load justifies its overhead and resource consequences.

Preserve every selected test.

Measure the scheduling algorithms.

Prefer efficient and deterministic methods.

Do not introduce unnecessary parallel execution.

Maintain the working L02–L05 system throughout implementation.

L06 begins after L05's SelectedTests interface is operational.

<!-- END Untitled-6.md -->


<!-- BEGIN Untitled-7.md -->


# BUILDERS BUILDATHON 2026
# L07 — FULL-SYSTEM INTEGRATION, PERFORMANCE ENGINEERING & COMPETITIVE OPTIMIZATION

PROTOCOL ID: L07
VERSION: 1.0
PHASE: Phase 2 — Local Engineering
TARGET: RWX — BLAST RADIUS
RECIPIENT: MAIN IDE CHIEF ENGINEERING AGENT
AUTHORITY: CENTRAL ARCHITECT
PRIORITY: CRITICAL

---

# 1. MISSION

Integrate the working L02–L06 components into one complete RWX submission.

The system must combine:

- Input and patch processing.
- Python static analysis.
- AST and symbol intelligence.
- Dependency graphs.
- Test-impact analysis.
- Safe test selection.
- Uncertainty handling.
- Conservative fallback.
- Worker scheduling.
- Official output serialization.

The objective is to minimize the actual aggregate competition score.

At the same time, the solution must:
- Detect failing tests reliably.
- Generalize beyond sample commits.
- Respect all official restrictions.
- Fit within the official runtime.
- Remain deterministic.
- Be independently reproducible.

Do not assume that the most sophisticated architecture is the best.

Compare the complete system against its simpler working alternatives.

---

# 2. PRECONDITIONS AND IMPLEMENTATION STATUS

Before integration, inspect:

L02 — Core implementation.
L03 — Python static analysis.
L04 — Dependency and graph engine.
L05 — Safe test selection.
L06 — Worker scheduling.

For each record:

- Implementation status.
- Passing tests.
- Failing tests.
- Current interfaces.
- Known limitations.
- CPU measurements.
- Memory measurements.
- Official scoring results.
- Outstanding blockers.

Use three statuses:

READY:
The module is implemented and its interface tests pass.

PARTIAL:
Some functionality works but acceptance criteria remain incomplete.

BLOCKED:
A required dependency or major correctness condition is missing.

Do not fabricate completion.

If a component is incomplete, retain the best verified earlier implementation or provide a safe adapter.

The existing working submission must remain recoverable.

---

# 3. RELEASE AND VERSION GOVERNANCE

Establish a known-good working release before integration.

Create:

- A stable integration branch.
- A baseline implementation tag.
- A working release identifier.
- An integration decision register.
- A module compatibility record.

Use separate branches or worktrees for concurrent development.

Every integrated component must identify:

- Source revision.
- Interface version.
- Dependencies.
- Test results.
- Integration owner.

Do not permit incompatible interfaces to enter the stable branch.

Maintain a working submission at all times.

---

# 4. MODULE INTERFACE INTEGRATION

Review and finalize the contracts.

Required pipeline:

InputValidator
→ PatchParser
→ ChangeSet
→ StaticAnalyzer
→ ChangeEvidence
→ GraphEngine
→ ImpactEvidence
→ TestSelector
→ SelectedTests
→ WorkerScheduler
→ WorkerAssignments
→ OutputSerializer

For each transition verify:

1. Input schema.
2. Output schema.
3. Identifier consistency.
4. Data type consistency.
5. Error behaviour.
6. Deterministic ordering.
7. Ownership.
8. Version compatibility.

Remove unnecessary data transformations.

Avoid repeated parsing.

Avoid serializing and deserializing large structures without a clear reason.

Use a common normalized internal representation.

---

# 5. COMPLETE END-TO-END INTEGRATION

Implement the actual complete execution flow.

For each commit:

### Stage A — Input

- Read the official input.
- Validate the commit.
- Load relevant test metadata.
- Validate available baseline artifacts.

### Stage B — Change analysis

- Parse the patch.
- Identify changed files.
- Identify added and removed lines.
- Obtain changed-symbol evidence where supported.
- Identify unresolved changes.

### Stage C — Dependency intelligence

- Query the module/import indexes.
- Query symbol and name relationships.
- Query permitted coverage relationships.
- Query supported fixture relationships.
- Perform the appropriate dependency propagation.

### Stage D — Impact analysis

- Aggregate evidence.
- Identify candidate tests.
- Preserve provenance.
- Record unresolved dependencies.
- Detect unsupported structural changes.

### Stage E — Test selection

- Apply mandatory inclusion.
- Apply evidence expansion.
- Evaluate uncertainty.
- Apply the appropriate fallback.
- Validate selected test identifiers.

### Stage F — Worker scheduling

- Evaluate appropriate worker count.
- Assign selected tests.
- Balance loads.
- Account for worker overhead.
- Preserve every selected test.

### Stage G — Output

- Serialize the official output.
- Validate JSON.
- Validate worker constraints.
- Emit one correct line per commit.
- Keep diagnostic logging separate.

The complete pipeline must work independently of development-agent services.

---

# 6. PRIMARY AND BACKUP ARCHITECTURE COMPARISON

Compare two complete systems.

PRIMARY:
The integrated architecture using the strongest validated combination of static analysis, graphs, coverage, selection and scheduling.

BACKUP:
The simplest compliant, conservative architecture that already works.

Evaluate both under identical conditions.

Compare:

- Official aggregate score.
- Missed failing tests.
- Number of selected tests.
- Simulated test execution cost.
- Worker overhead.
- CPU consumption.
- Peak memory.
- Wall-clock time.
- Build duration.
- Artifact size.
- Stability.
- Generalization evidence.

Do not automatically choose the primary architecture.

If the backup has a better verified total score and better reliability, investigate why.

Reject components whose added complexity does not produce measurable value.

---

# 7. PERFORMANCE OPTIMIZATION LAYER A — BUILD TIME

Investigate:

- Source parsing.
- AST extraction.
- Symbol indexing.
- Import resolution.
- Coverage mapping.
- Graph construction.
- Reverse-index generation.
- Metadata serialization.

Optimize:

- Repeated traversals.
- Redundant metadata.
- Duplicate relationships.
- Expensive serialization.
- Artifact size.
- Build CPU.
- Build memory.
- Initialization time.

Keep build-time analysis deterministic and reproducible.

Ensure every artifact is generated only from permitted baseline information.

No patch-to-failure-test lookup tables.

---

# 8. PERFORMANCE OPTIMIZATION LAYER B — RUNTIME

Measure each stage independently:

- Input loading.
- Patch parsing.
- Changed-symbol analysis.
- Dependency lookup.
- Graph propagation.
- Impact aggregation.
- Selection.
- Fallback evaluation.
- Worker scheduling.
- JSON serialization.

Investigate:

- Unnecessary AST parsing.
- Repeated dictionary lookups.
- Excessive set creation.
- Graph traversal duplication.
- Large intermediate objects.
- Inefficient sorting.
- Repeated serialization.
- Unnecessary process creation.

Prefer:
- Compact integer identifiers.
- Efficient adjacency structures.
- Reusable baseline metadata.
- Reverse indexes.
- Single-pass processing where appropriate.
- Deterministic algorithms.

Do not make optimizations that weaken failure detection.

---

# 9. PERFORMANCE OPTIMIZATION LAYER C — GRAPH ENGINE

Optimize:

- Node representation.
- Edge representation.
- Forward and reverse indexes.
- Duplicate elimination.
- Reachability.
- Cycle handling.
- Propagation.
- Graph loading.
- Metadata storage.

Investigate bitsets and compact arrays only when their actual performance advantages justify implementation complexity.

Compare graph traversal alternatives using identical inputs.

Do not retain an expensive graph layer merely because it is a core part of our research.

Its value must be established through selection quality and total score.

---

# 10. PERFORMANCE OPTIMIZATION LAYER D — SAFE SELECTION

Optimize the L05 selection policy.

Measure:

- Candidate test count.
- Mandatory tests.
- Uncertain tests.
- Fallback frequency.
- Final selected tests.
- False positives.
- Known false negatives.
- Official penalty contribution.

Investigate whether different evidence sources can safely reduce unnecessary expansion.

Pay particular attention to:

- Static-analysis uncertainty.
- Dynamic Python features.
- Incomplete coverage.
- Unresolved names.
- Unknown files.
- Missing graph nodes.

Do not reduce selection size simply to improve the apparent precision metric.

A missed failing test can destroy the entire score improvement from other commits.

Maintain conservative behaviour for unsupported cases.

---

# 11. PERFORMANCE OPTIMIZATION LAYER E — WORKER SCHEDULER

Optimize L06 using official measurements.

Compare:

- One worker.
- Multiple fixed worker counts.
- Adaptive worker counts.
- LPT.
- Alternative greedy methods.
- More advanced methods, only where justified.

For each scheduler record:

- Maximum load.
- Worker overhead.
- Assignment computation time.
- CPU consumption.
- Aggregate score.

Use the complete official scoring function.

Ensure worker optimization never changes the selected test set.

---

# 12. RESOURCE AND CONTAINER ENGINEERING

Inspect the final container against the actual official specification.

Verify:

- Repository size.
- Build CPU.
- Build memory.
- Build duration.
- Runtime CPU.
- Runtime memory.
- Runtime duration.
- User permissions.
- Filesystem mode.
- Temporary storage.
- Process limits.
- Network access.
- Dependency availability.
- Architecture compatibility.

Our local MacBook Pro M4 Pro is an Apple Silicon development environment.

Do not treat native ARM benchmark results as definitive x86 competition results.

Use the official execution container or suitable remote validation environment.

Avoid unnecessary dependencies.

Freeze required dependency versions.

---

# 13. DETERMINISM AND RELIABILITY

Verify:

- Stable graph construction.
- Stable node identifiers.
- Stable traversal.
- Stable test ordering.
- Stable worker assignment.
- Stable JSON output.
- Deterministic fallback.
- Reproducible metadata generation.

Run identical inputs multiple times.

Investigate any output or performance variation.

Separate expected timing variability from actual changes in algorithmic behaviour.

---

# 14. FULL BENCHMARK COMPARISON

Run the complete official evaluation on each viable release candidate.

Maintain a benchmark comparison table.

Required fields:

- Release ID.
- Source commit.
- Architecture version.
- Evaluator version.
- Dataset.
- Missed failing commits.
- Selected test count.
- Simulated test seconds.
- Worker count.
- Worker overhead.
- CPU seconds.
- Wall-clock duration.
- Peak RAM.
- Artifact size.
- Official aggregate score.
- Result status.

Use equivalent evaluation conditions.

Compare against:

1. Official reference.
2. Existing working baseline.
3. Conservative selector.
4. Integrated architecture.
5. Optimized release candidate.

Every claimed improvement must have actual experiment records.

---

# 15. AUTOMATED OPTIMIZATION LOOP

Establish a controlled improvement process:

Observe benchmark
→ Identify bottleneck
→ Form hypothesis
→ Change one major component
→ Run correctness tests
→ Run official evaluator
→ Compare metrics
→ Accept or reject
→ Record decision
→ Repeat

Do not make multiple unrelated algorithmic changes without preserving a comparison point.

Do not overwrite the best verified release with an untested optimization.

Maintain a known-good checkpoint after each meaningful improvement.

---

# 16. FINAL INTEGRATED SYSTEM ACCEPTANCE

The complete system must pass:

A. Official environment validation.

B. Input/output contract.

C. Patch processing.

D. Static-analysis integration.

E. Dependency graph construction.

F. Impact propagation.

G. Safe selection.

H. Conservative fallback.

I. Worker scheduling.

J. Official scoring.

K. CPU and memory limits.

L. Determinism.

M. Repository and license compliance.

N. Final packaging.

Do not treat compilation or successful unit tests as sufficient proof of a competitive submission.

---

# 17. L07 ACCEPTANCE GATE

L07 is complete only when:

1. L02–L06 integration is established.
2. All module interfaces are compatible.
3. A complete end-to-end submission runs.
4. The official evaluator accepts it.
5. Primary and backup architectures are compared.
6. All significant optimizations have benchmark evidence.
7. Known-good checkpoints are preserved.
8. No known missed-test problem is concealed.
9. Runtime and memory are within official limits.
10. Build artifacts satisfy repository restrictions.
11. Output remains deterministic and valid.
12. The project state and decision ledger are updated.

---

# 18. REQUIRED DELIVERABLES

Provide:

- Integrated final source tree.
- Module integration report.
- Complete end-to-end execution report.
- Primary and backup architecture comparison.
- Performance profiling.
- Optimization experiment results.
- Correctness and safety report.
- Container compliance report.
- Release candidate identifier.
- Official benchmark evidence.
- Updated PROJECT_STATE.md.
- Updated benchmark and experiment ledgers.
- Remaining risk register.
- L07 completion report.

---

# FINAL DIRECTIVE

Integrate first.

Measure second.

Optimize third.

Preserve safety throughout.

Do not let individual specialists optimize their own components in ways that worsen the total system.

The official aggregate competition score is the deciding metric.

Maintain a known-good release.

Every improvement must earn its place through reproducible testing.

L07 begins once the required L02–L06 modules are operational.

<!-- END Untitled-7.md -->


<!-- BEGIN Untitled-8.md -->


# BUILDERS BUILDATHON 2026
# L08 — FINAL ADVERSARIAL TESTING, SUBMISSION HARDENING & COMPETITION RELEASE

PROTOCOL ID: L08
VERSION: 1.0
PHASE: Phase 2 — Final Release Engineering
TARGET: RWX — BLAST RADIUS
RECIPIENT: MAIN IDE CHIEF ENGINEERING AGENT
AUTHORITY: CENTRAL ARCHITECT
PRIORITY: CRITICAL

---

# 1. MISSION

Prepare the strongest verified RWX submission for final competition evaluation.

L07 integrated the complete system.

L08 must:

1. Perform final adversarial testing.
2. Verify all functional requirements.
3. Test unseen-change generalization using permitted validation methods.
4. Verify exact official scoring compatibility.
5. Verify Docker and resource limits.
6. Audit dependencies and licenses.
7. Compare the best implementation versions.
8. Select the best verified release.
9. Freeze the source commit.
10. Push and verify the public GitHub repository.
11. Submit the selected commit through the official competition interface.
12. Preserve proof of successful submission.

Do not make architectural changes merely because more features appear desirable.

Only accept changes that demonstrate a measurable benefit without introducing unacceptable risk.

---

# 2. PRECONDITIONS

Before beginning, inspect:

- PROJECT_STATE.md.
- Latest L07 release candidate.
- Known-good baseline.
- Official benchmark ledger.
- Decision ledger.
- Risk register.
- Existing Git branches and commits.
- Official Docker configuration.
- Official scoring implementation.

Confirm whether L07 has:

- Integrated L02–L06.
- Passed the official evaluator.
- Produced reproducible benchmark results.
- Identified the current best-scoring commit.

If not, resolve the essential missing requirements before attempting final release.

Never destroy the best verified submission while testing improvements.

---

# 3. ADVERSARIAL TESTING

Conduct a final independent attack against the complete system.

## A. Input attacks

Test:

- Valid patch.
- Empty patch.
- Multiple changed files.
- Added file.
- Deleted file.
- Renamed file.
- Malformed unified diff.
- Unsupported change structure.
- Missing metadata.
- Unexpected input ordering.

## B. Static-analysis attacks

Test:

- Function modification.
- Class modification.
- Import modification.
- Relative imports.
- Re-exports.
- Inheritance.
- Decorators.
- Shared variables.
- Nested functions.
- Dynamic imports.
- Unresolved symbols.
- Multiple module changes.

## C. Graph attacks

Test:

- Dependency cycles.
- Missing nodes.
- Missing edges.
- Duplicate edges.
- Transitive dependencies.
- Unresolved relationships.
- Incomplete coverage.
- Shared fixtures.
- Graph corruption.

## D. Selection attacks

Test:

- No selected tests.
- One selected test.
- Multiple candidate paths.
- Duplicate candidates.
- Uncertain dependencies.
- Unsupported patches.
- Conservative expansion.
- Full-suite fallback.

Verify that selected-test IDs are valid and no known required test is removed.

## E. Scheduling attacks

Test:

- One worker.
- Eight workers.
- Unequal durations.
- Many short tests.
- Very long tests.
- Equal durations.
- Empty selection.
- Highly skewed workloads.

## F. Output attacks

Verify:

- Exact JSON schema.
- One line per commit.
- Correct commit IDs.
- Valid test numbers.
- No duplicate tests.
- No empty workers.
- Maximum eight workers.
- No diagnostic output on stdout.
- Output remains below 2 MB.

Every failed test must be classified and corrected.

---

# 4. OFFICIAL SCORER VALIDATION

Run the supplied official local scoring process.

The official starter includes 30 sample commits and the tests each commit breaks.

Use the official development workflow, including `make sample` where supported by the inspected starter.

Validate:

- Correctness.
- Missed failing tests.
- Selected tests.
- Worker assignments.
- Simulated execution seconds.
- CPU seconds.
- Aggregate score.

Maintain the distinction between:

1. Local sample evaluation.
2. Practice leaderboard submission.
3. Final unseen evaluation.

The local scorer is the primary development tool.

Never assume the actual practice or final evaluation exposes the program's output or exact missed tests. The official system provides aggregate feedback rather than a full diagnostic trace. Debug locally.

---

# 5. FINAL ARCHITECTURE SELECTION

Compare:

A. Best verified conservative implementation.

B. Best verified full architecture.

C. Best verified optimized implementation.

D. Any additional release candidate with a measurable advantage.

Use identical evaluation conditions.

Compare:

- Official score.
- Missed commits.
- CPU seconds.
- Simulated CI seconds.
- Worker overhead.
- Wall-clock time.
- Peak memory.
- Repository size.
- Runtime stability.

Select the release with the strongest verified overall result.

Do not choose the most recently modified branch automatically.

Do not sacrifice correctness for a small speculative score improvement.

Preserve the previous best commit.

---

# 6. FINAL RUNTIME COMPLIANCE AUDIT

Inspect the complete container.

Verify:

- linux/amd64 compatibility.
- Dockerfile at repository root.
- Correct entrypoint.
- Required dependencies.
- Correct user permissions.
- User nobody.
- HOME=/tmp.
- Read-only filesystem.
- 64 MB temporary filesystem.
- Maximum 256 processes.
- No runtime network access.
- Two CPU cores.
- 4 GB runtime memory.
- Three-minute practice execution.
- 4.5-minute final execution.
- Build within ten minutes.
- Four build CPUs.
- 8 GB build memory.
- Repository size no greater than 20 MB.

Use the actual organizer-provided runtime configuration and inspect the complete official specification for any additional details.

Do not assume native Apple Silicon execution proves amd64 compatibility.

Verify using the appropriate container architecture.

---

# 7. DEPENDENCY AND SECURITY AUDIT

Inspect:

- requirements files.
- Python package versions.
- Transitive dependencies.
- Docker base image.
- External downloads.
- Source repositories.
- License notices.
- Embedded files.
- Build scripts.
- Temporary artifacts.
- Credentials and secrets.

Verify the official build-source restrictions:

- Public package registries.
- Public Docker Hub images.
- GitHub releases at fixed tags.
- sqlglot at the pinned commit.

Do not download dependencies from infrastructure controlled by our team.

The final build must remain reproducible after the cutoff.

Remove unnecessary dependencies.

Do not include API keys, credentials, private information or unrelated research archives inside the submission repository.

---

# 8. LICENSING AND OWNERSHIP

Verify:

- Public GitHub repository.
- MIT LICENSE.
- Required third-party notices.
- Correct attribution.
- Independent team ownership.
- Original commit history.
- No copied competing-team implementation.
- No prohibited cross-team code sharing.

Preserve all submitted commits in the public repository until results are published.

The official rules explicitly require the repository to remain accessible for final rebuilding. An unavailable repository or unbuildable submission receives no final score.

---

# 9. RELEASE FREEZE

Establish the release freeze process.

Before freezing:

1. Run the official local evaluator.
2. Run the full correctness suite.
3. Run the final Docker build.
4. Verify the runtime command.
5. Verify repository size.
6. Inspect Git status.
7. Remove accidental experimental files.
8. Commit all required source files.
9. Record the selected Git commit SHA.
10. Push to the public GitHub repository.
11. Verify the remote commit is accessible.

Create:

RELEASE_REPORT.md
FINAL_COMMIT.txt
FINAL_BENCHMARK.csv
FINAL_COMPLIANCE_CHECKLIST.md
RELEASE_SHA256SUMS.txt

No unreviewed changes after the release freeze.

Any necessary correction requires a new tested commit and updated release record.

---

# 10. COMPETITION SUBMISSION

Read the actual current official submission interface.

Verify:

- Correct team account.
- Correct competition.
- Correct RWX track.
- Correct GitHub repository.
- Correct commit SHA.
- Correct submission selection.
- Successful platform response.
- Submission receipt or identifier.
- Final practice score, if available.

The official rules specify that the chosen commit at the cutoff is used for the final.

Only the final result wins the prize.

Practice leaderboard position is not sufficient proof of victory.

Do not assume the latest commit will automatically be selected.

Verify the selected submission explicitly.

---

# 11. SUBMISSION TIMING AND TIE-BREAKS

Follow the current official submission policy.

The official RWX page specifies:

- One submission per hour per team initially.
- The limit may increase when queue conditions permit.
- Earlier submissions rank first in equal-score practice ties.
- The final has its own one-second tie grouping rule.
- The top five entries receive additional final evaluation.
- The final uses five runs rather than the practice three.

Do not leave the first valid submission until the last minute.

Once a valid release exists, submit it.

Later submissions should only replace it when the new candidate has passed the required local verification.

Maintain the best known submitted commit until results are published.

---

# 12. FINAL COMPETITION RELEASE DECISION

Produce a release decision table:

| Candidate | Correctness | Misses | Official score | CPU | Memory | Status |
|---|---|---|---|---|---|---|

Distinguish:

- Local sample score.
- Official practice score.
- Final unseen evaluation.

Do not claim a final competition result before the organizers publish it.

Do not invent first-place probabilities.

The final release recommendation must be backed by actual measurements.

---

# 13. L08 ACCEPTANCE GATE

L08 is complete when:

1. Adversarial tests have been executed.
2. Known correctness issues are resolved.
3. Official local evaluator passes.
4. No prohibited lookup mechanism exists.
5. Docker build succeeds.
6. Runtime limits are respected.
7. Public GitHub repository is accessible.
8. MIT license and notices are correct.
9. Best verified commit is identified.
10. Final commit SHA is recorded.
11. Official platform submission succeeds.
12. Submission confirmation is recorded.
13. Best submitted commit is explicitly selected for the final.
14. Release artifacts and reports are preserved.

If any condition fails, report the exact failure and apply the smallest safe correction.

---

# 14. REQUIRED FINAL DELIVERABLES

Provide:

- Final release candidate.
- Official local evaluation report.
- Adversarial testing report.
- Compliance audit.
- Docker verification.
- Performance comparison.
- Final Git commit SHA.
- Public repository URL.
- Official submission receipt.
- Selected final submission information.
- Updated PROJECT_STATE.md.
- Updated benchmark ledger.
- Release manifest.
- Outstanding risk report.

---

# FINAL DIRECTIVE

The objective is not to submit the most complicated implementation.

The objective is to submit the strongest verified solution that:

- Works.
- Generalizes.
- Detects failures.
- Minimizes the official score.
- Meets every runtime constraint.
- Satisfies all competition rules.
- Can be rebuilt from the public repository.

Protect the best verified release.

Do not make untested last-minute changes.

Do not confuse practice performance with final victory.

Freeze, verify, submit and preserve the exact release.

L08 begins after L07 produces an integrated release candidate.

<!-- END Untitled-8.md -->

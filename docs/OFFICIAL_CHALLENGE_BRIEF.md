# RWX Blast Radius — official challenge brief

Source: supplied `Raw.md`, preserved at `../evaluation/Raw.original.md`.

Official page: https://rwx.com/blast-radius

## Task

Given independent unified patches against sqlglot commit `eb11aec4be8cb2122afe713a4816662c3f0fb2fa`, select the tests that can catch each change and divide them across at most eight workers.

Inputs:

- `/data/commits/<id>.patch`: one standalone unified diff per commit.
- `/data/tests.json`: numbered tests, file paths, recorded durations, and skip metadata.

Emit exactly one JSON object per commit:

```json
{"commit":"k7q2","workers":[[12,845,901],[3,77]]}
```

Use `"workers": []` when no tests are needed. Logs belong on stderr. Invalid output or stdout above 2 MB rejects the run.

## Score

For each commit, cost is the busiest worker's recorded test duration plus two seconds per worker. Leaving out any failing test adds 300 seconds for that commit. Container CPU time is added across the batch. The image runs three times and the middle total counts, rounded to 0.1 seconds.

A failure includes pytest failures, errors, timeouts, test-file import failures, and any failing subtest. A comment-only change is not guaranteed harmless.

## Limits

- Repository: at most 20 MB; no reliance on Git submodules or Git LFS.
- Build: network, four cores, 8 GB RAM, ten minutes.
- Sample runtime: no network, two cores, 4 GB RAM, three minutes.
- Final runtime: 4.5 minutes for roughly 1.5 times as many commits.
- Runtime user: `nobody`; `HOME=/tmp`; read-only disk; empty 64 MB `/tmp`; at most 256 processes.

A committed pinned-source map avoids paying test-generation time on every clean build.

## Compliance

- Submit the team's own public GitHub repository with a top-level Dockerfile and the commit to score.
- Build downloads are restricted to public package registries, fixed-tag GitHub releases, and the pinned sqlglot repository.
- Never use precomputed answers looked up by patch or edit kind. Pinned-source coverage, import, and fixture maps are allowed.
- Keep the repository and submitted commits available until results are published.
- Only final results count; the practice board has no prize.

## Submission repository link

Public GitHub repository: https://github.com/Srujan0798/RWX-Blast-Radius-.git

## Local references

- Exact scorer semantics: `../SCORING.md`.
- Official sample inputs: `../evaluation/sample/` (`answers.json` is evaluation-only).
- Active product: repository root, with `Dockerfile`, `src/`, `maps/`, `tests/`, and `build/`.
- Continuation assignments: `../protocols/00_START_HERE.md`.

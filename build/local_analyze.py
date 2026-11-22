#!/usr/bin/env python3
"""Fast local per-commit analysis: build changesets, run selector+scheduler,
compute base cost + misses using answers.json. No Docker needed."""
from __future__ import annotations

import json
import math
import sys
import zlib
from pathlib import Path

ROOT = Path("/Users/srujansai/Desktop/RWX - Blast Radius")
SAMPLE = ROOT / "evaluation" / "sample"
sys.path.insert(0, str(ROOT))

from src.patch_parser import parse_all_patches
from src.changeset import build_all_changesets
from src.coverage_selector import CoverageSelector
from src.worker_scheduler import WorkerScheduler
from src.input_validator import InputValidator


def duration_ms(seconds: float) -> int:
    return math.floor(seconds * 1000 + 0.5)


def main():
    document = json.loads(zlib.decompress((ROOT / "maps" / "maps.json.z").read_bytes()))
    tests_data = json.loads((SAMPLE / "tests.json").read_text())["tests"]
    answers = json.loads((SAMPLE / "answers.json").read_text())
    failing_by_commit = {c: set(answers["commits"][c]["failing"]) for c in answers["commits"]}
    durations = {t["number"]: duration_ms(t["seconds"]) for t in tests_data}

    # Build validator-like tests list
    from src.input_validator import TestMetadata
    tests = [TestMetadata(number=t["number"], id=t["id"], file=t["file"], seconds=t["seconds"], skipped=t.get("skipped", False)) for t in tests_data]

    selector = CoverageSelector(tests, ROOT / "maps" / "maps.json.z")
    scheduler = WorkerScheduler(tests)

    patches = parse_all_patches(SAMPLE / "commits")
    changesets = build_all_changesets(patches)

    total_base = 0
    total_misses = 0
    total_selected = 0
    total_cpu_est = 0
    rows = []
    for cid in sorted(changesets.keys()):
        cs = changesets[cid]
        failing = failing_by_commit.get(cid, set())
        decision = selector.select_tests(cs)
        selected = set(decision.selected_test_numbers)
        assignment = scheduler.schedule(sorted(selected))
        # base cost
        workers = [w for w in assignment.workers if w]
        if workers:
            largest = max(sum(durations[t] for t in w) for w in workers)
            base_ms = largest + 2000 * len(workers)
        else:
            base_ms = 0
        misses = failing - selected
        miss_penalty = 300000 * len(misses)
        total_base += base_ms
        total_misses += len(misses)
        total_selected += len(selected)
        rows.append((cid, base_ms, len(misses), len(selected), assignment.worker_count, sorted(misses)))

    print(f"Total base_ms: {total_base/1000:.3f}s")
    print(f"Total misses: {total_misses}")
    print(f"Total selected: {total_selected}")
    print(f"Simulated (no CPU): {(total_base + 300000*total_misses)/1000:.3f}s")
    print()
    print(f"{'commit':<8} {'base(s)':>8} {'misses':>7} {'sel':>5} {'workers':>7} {'missed_tests'}")
    for cid, base_ms, nm, sel, wc, misses in rows:
        print(f"{cid:<8} {base_ms/1000:>8.3f} {nm:>7} {sel:>5} {wc:>7} {misses}")


if __name__ == "__main__":
    main()

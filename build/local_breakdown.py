#!/usr/bin/env python3
"""Per-commit breakdown: which files changed, selection method, what contributes."""
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
from src.input_validator import TestMetadata


def duration_ms(seconds: float) -> int:
    return math.floor(seconds * 1000 + 0.5)


def main():
    document = json.loads(zlib.decompress((ROOT / "maps" / "maps.json.z").read_bytes()))
    tests_data = json.loads((SAMPLE / "tests.json").read_text())["tests"]
    from src.input_validator import TestMetadata
    tests = [TestMetadata(number=t["number"], id=t["id"], file=t["file"], seconds=t["seconds"], skipped=t.get("skipped", False)) for t in tests_data]
    durations = {t["number"]: duration_ms(t["seconds"]) for t in tests_data}
    selector = CoverageSelector(tests, ROOT / "maps" / "maps.json.z")
    scheduler = WorkerScheduler(tests)

    patches = parse_all_patches(SAMPLE / "commits")
    changesets = build_all_changesets(patches)

    # Show top 10 expensive commits
    durations = {t["number"]: duration_ms(t["seconds"]) for t in tests_data}
    commit_rows = []
    for cid in sorted(changesets.keys()):
        cs = changesets[cid]
        decision = selector.select_tests(cs)
        selected = set(decision.selected_test_numbers)
        assignment = scheduler.schedule(sorted(selected))
        workers = [w for w in assignment.workers if w]
        base_ms = (max(sum(durations[t] for t in w) for w in workers) + 2000 * len(workers)) if workers else 0
        commit_rows.append((cid, base_ms, len(selected), len(workers), decision.analysis_status, cs))
    commit_rows.sort(key=lambda r: -r[1])
    for cid, base_ms, sel, wc, status, cs in commit_rows[:10]:
        paths = sorted(cs.get_all_changed_paths())
        print(f"{cid}: base={base_ms/1000:.3f}s sel={sel} workers={wc} status={status}")
        print(f"   changed files: {paths}")
        for p in paths:
            fc = cs.file_changes.get(p)
            if fc:
                print(f"     {p}: op={fc.operation.value} hunks={len(fc.hunks)} added_lines={fc.added_lines[:8]} removed_lines={fc.removed_lines[:8]} parse_err={cs.parse_errors}")


if __name__ == "__main__":
    main()

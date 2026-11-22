"""Fast local sample scorer for selector iteration.

Runs the real selector and scheduler over the sample patches without Docker.
Prints per-commit selected counts, worker counts, cost, and the total.
Never reads evaluation/sample/answers.json.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_modules(src_root: Path):
    for name in list(sys.modules):
        if name == "src" or name.startswith("src."):
            del sys.modules[name]
    sys.path.insert(0, str(src_root))
    coverage_selector = importlib.import_module("src.coverage_selector")
    conservative = importlib.import_module("src.test_selector")
    scheduler_mod = importlib.import_module("src.worker_scheduler")
    patch_parser = importlib.import_module("src.patch_parser")
    changeset_mod = importlib.import_module("src.changeset")
    input_validator = importlib.import_module("src.input_validator")
    return {
        "CoverageSelector": coverage_selector.CoverageSelector,
        "ConservativeTestSelector": conservative.ConservativeTestSelector,
        "WorkerScheduler": scheduler_mod.WorkerScheduler,
        "parse_all_patches": patch_parser.parse_all_patches,
        "build_all_changesets": changeset_mod.build_all_changesets,
        "TestMetadata": input_validator.TestMetadata,
    }


def score(sample: Path, root: Path, source_root: Path | None = None, src_root: Path | None = None) -> dict:
    modules = load_modules(src_root or ROOT)

    raw = json.loads((sample / "tests.json").read_text())["tests"]
    tests = [
        modules["TestMetadata"](
            number=t["number"],
            id=t["id"],
            file=t["file"],
            seconds=t["seconds"],
        )
        for t in raw
    ]
    duration_ms = {t["number"]: round(t["seconds"] * 1000) for t in raw}

    patches = modules["parse_all_patches"](sample / "commits")
    changesets = modules["build_all_changesets"](patches)

    map_path = root / "maps" / "maps.json.z"
    if map_path.exists():
        selector = modules["CoverageSelector"](tests, map_path, source_root)
    else:
        selector = modules["ConservativeTestSelector"](tests)
    scheduler = modules["WorkerScheduler"](tests)

    rows = []
    total = 0
    for commit_id in sorted(changesets):
        decision = selector.select_tests(changesets[commit_id])
        assignment = scheduler.schedule(decision.selected_test_numbers)
        workers = [w for w in assignment.workers if w]
        loads = [sum(duration_ms[n] for n in w) for w in workers]
        cost_ms = (max(loads) if loads else 0) + 2000 * len(workers)
        total += cost_ms
        rows.append(
            {
                "commit": commit_id,
                "workers": len(workers),
                "selected": sum(len(w) for w in workers),
                "cost_ms": cost_ms,
                "decision_status": decision.analysis_status,
            }
        )
    return {"total_ms": total, "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", default=str(ROOT / "evaluation" / "sample"))
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--src-root", default=None)
    parser.add_argument("--source-root", default=None)
    parser.add_argument("--detail", action="store_true")
    args = parser.parse_args()

    source_root = Path(args.source_root) if args.source_root else None
    result = score(
        Path(args.sample),
        Path(args.root),
        source_root,
        Path(args.src_root) if args.src_root else None,
    )
    if args.detail:
        for row in sorted(result["rows"], key=lambda r: -r["cost_ms"]):
            print(
                f"{row['cost_ms'] / 1000:8.3f}s {row['commit']:8} "
                f"workers={row['workers']:2d} selected={row['selected']:5d} "
                f"status={row['decision_status']}"
            )
    print(f"TOTAL simulated seconds: {result['total_ms'] / 1000:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

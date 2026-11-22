"""Fast local sample runner: produces output JSONL and scores it locally.

Mirrors src/main.py's selection + scheduling flow without Docker, then scores
the result with score.py. Never reads evaluation/sample/answers.json itself;
the miss check is delegated to the provided scorer.
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
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


def run_sample(sample: Path, root: Path, source_root: Path | None, src_root: Path, output: Path) -> None:
    modules = load_modules(src_root)

    raw = json.loads((sample / "tests.json").read_text())["tests"]
    tests = [
        modules["TestMetadata"](
            number=t["number"], id=t["id"], file=t["file"], seconds=t["seconds"]
        )
        for t in raw
    ]

    patches = modules["parse_all_patches"](sample / "commits")
    changesets = modules["build_all_changesets"](patches)

    map_path = root / "maps" / "maps.json.z"
    if map_path.exists():
        selector = modules["CoverageSelector"](tests, map_path, source_root)
    else:
        selector = modules["ConservativeTestSelector"](tests)
    scheduler = modules["WorkerScheduler"](tests)

    lines = []
    for commit_id in sorted(changesets):
        decision = selector.select_tests(changesets[commit_id])
        assignment = scheduler.schedule(decision.selected_test_numbers)
        workers = [w for w in assignment.workers if w]
        lines.append(json.dumps({"commit": commit_id, "workers": workers}, separators=(",", ":")))
    output.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", default=str(ROOT / "evaluation" / "sample"))
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--src-root", default=None)
    parser.add_argument("--source-root", default=None)
    parser.add_argument("--output", default="/tmp/rwx-local-output.jsonl")
    args = parser.parse_args()

    sample = Path(args.sample)
    output = Path(args.output)
    run_sample(
        sample,
        Path(args.root),
        Path(args.source_root) if args.source_root else None,
        Path(args.src_root) if args.src_root else ROOT,
        output,
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "score.py"), str(sample), str(sample / "answers.json"), str(output)],
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    print(f"output: {output}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

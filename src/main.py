"""RWX Blast Radius - Main Entry Point

Integrates all modules for end-to-end execution.
"""

import sys
import json
from pathlib import Path

from .input_validator import InputValidator
from .patch_parser import parse_all_patches
from .changeset import build_all_changesets
from .test_selector import ConservativeTestSelector
from .coverage_selector import CoverageSelector
from .selection_validator import SelectionValidator
from .worker_scheduler import WorkerScheduler
from .output_serializer import OutputSerializer
from .error_handler import ErrorHandler


def main() -> int:
    validator = InputValidator()
    result = validator.validate_all()

    if not result.success:
        for err in result.errors:
            print(f"VALIDATION ERROR: {err}", file=sys.stderr)
        return 1

    for warn in result.warnings:
        print(f"WARNING: {warn}", file=sys.stderr)

    commits_dir = Path("/data/commits")
    patches = parse_all_patches(commits_dir)
    changesets = build_all_changesets(patches)

    map_path = Path(__file__).resolve().parent.parent / "maps" / "maps.json.z"
    if map_path.exists():
        selector = CoverageSelector(validator.tests, map_path)
    else:
        print("WARNING: coverage map unavailable; using conservative selector", file=sys.stderr)
        selector = ConservativeTestSelector(validator.tests)
    sel_validator = SelectionValidator(validator.tests)
    scheduler = WorkerScheduler(validator.tests)
    error_handler = ErrorHandler(validator.tests)

    assignments = {}

    for commit_id in sorted(changesets.keys()):
        cs = changesets[commit_id]

        try:
            decision = selector.select_tests(cs)

            val_result = sel_validator.validate(decision)
            if not val_result.valid:
                for err in val_result.errors:
                    print(f"SELECTION VALIDATION ERROR ({commit_id}): {err}", file=sys.stderr)
                decision = error_handler.handle_invalid_test_numbers(commit_id, [])

            assignment = scheduler.schedule(decision.selected_test_numbers)

            worker_val = sel_validator.validate_workers(assignment.workers)
            if not worker_val.valid:
                for err in worker_val.errors:
                    print(f"WORKER VALIDATION ERROR ({commit_id}): {err}", file=sys.stderr)

            assignments[commit_id] = assignment

        except Exception as e:
            decision = error_handler.handle_unexpected_error(commit_id, e, "main_loop")
            assignment = scheduler.schedule(decision.selected_test_numbers)
            assignments[commit_id] = assignment

    lines = OutputSerializer.serialize_all(assignments)
    OutputSerializer.write_output(lines)

    error_handler.report_errors()

    return 0


if __name__ == "__main__":
    sys.exit(main())
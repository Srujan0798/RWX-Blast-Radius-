"""MODULE G — Output Serializer

Implements exact output contract for official evaluator.
"""

import json
import sys
from typing import Any
from .worker_scheduler import WorkerAssignment


class OutputSerializer:
    @staticmethod
    def serialize(commit_id: str, assignment: WorkerAssignment) -> str:
        output = {
            "commit": commit_id,
            "workers": assignment.workers
        }
        return json.dumps(output, separators=(',', ':'))

    @staticmethod
    def serialize_all(assignments: dict[str, WorkerAssignment]) -> list[str]:
        lines = []
        for commit_id in sorted(assignments.keys()):
            lines.append(OutputSerializer.serialize(commit_id, assignments[commit_id]))
        return lines

    @staticmethod
    def write_output(lines: list[str], output_path: str | None = None) -> None:
        out = sys.stdout if output_path is None else open(output_path, 'w')
        try:
            for line in lines:
                out.write(line + "\n")
        finally:
            if output_path is not None:
                out.close()


def main() -> int:
    from .input_validator import InputValidator
    from .test_selector import ConservativeTestSelector
    from .worker_scheduler import WorkerScheduler
    from .patch_parser import parse_all_patches
    from .changeset import build_all_changesets
    from pathlib import Path

    validator = InputValidator()
    result = validator.validate_all()
    if not result.success:
        return 1

    commits_dir = Path("/data/commits")
    patches = parse_all_patches(commits_dir)
    changesets = build_all_changesets(patches)

    selector = ConservativeTestSelector(validator.tests)
    scheduler = WorkerScheduler(validator.tests)

    assignments = {}
    for commit_id, cs in changesets.items():
        decision = selector.select_tests(cs)
        assignments[commit_id] = scheduler.schedule(decision.selected_test_numbers)

    lines = OutputSerializer.serialize_all(assignments)
    OutputSerializer.write_output(lines)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
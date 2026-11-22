"""MODULE E — Selection Validator

Verifies selection output meets all official requirements.
"""

from dataclasses import dataclass
from typing import Any
from .test_selector import SelectionDecision
from .input_validator import TestMetadata


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class SelectionValidator:
    MAX_WORKERS = 8

    def __init__(self, tests: list[TestMetadata]):
        self.test_by_number = {t.number: t for t in tests}
        self.valid_test_numbers = set(self.test_by_number.keys())

    def validate(self, decision: SelectionDecision) -> ValidationResult:
        result = ValidationResult(valid=True)

        self._validate_test_numbers(decision, result)
        self._validate_duplicates(decision, result)
        self._validate_deterministic(decision, result)

        if not result.valid:
            return result

        return result

    def _validate_test_numbers(self, decision: SelectionDecision, result: ValidationResult) -> None:
        for num in decision.selected_test_numbers:
            if num not in self.valid_test_numbers:
                result.valid = False
                result.errors.append(f"Invalid test number in selection: {num}")

        for num in decision.candidate_test_numbers:
            if num not in self.valid_test_numbers:
                result.warnings.append(f"Invalid test number in candidates: {num}")

    def _validate_duplicates(self, decision: SelectionDecision, result: ValidationResult) -> None:
        seen = set()
        for num in decision.selected_test_numbers:
            if num in seen:
                result.valid = False
                result.errors.append(f"Duplicate test number in selection: {num}")
            seen.add(num)

    def _validate_deterministic(self, decision: SelectionDecision, result: ValidationResult) -> None:
        if decision.selected_test_numbers != sorted(decision.selected_test_numbers):
            result.warnings.append("Selected tests not in sorted order (may affect determinism)")

    def validate_workers(self, workers: list[list[int]]) -> ValidationResult:
        result = ValidationResult(valid=True)

        occupied = [w for w in workers if w]
        if len(occupied) > self.MAX_WORKERS:
            result.valid = False
            result.errors.append(f"Too many workers: {len(occupied)} > {self.MAX_WORKERS}")

        seen = set()
        for worker in workers:
            for test_num in worker:
                if test_num in seen:
                    result.valid = False
                    result.errors.append(f"Test {test_num} appears in multiple workers")
                if test_num not in self.valid_test_numbers:
                    result.valid = False
                    result.errors.append(f"Worker contains invalid test number: {test_num}")
                seen.add(test_num)

        return result


def main() -> int:
    from .input_validator import InputValidator
    from .test_selector import ConservativeTestSelector
    from .patch_parser import parse_all_patches
    from .changeset import build_all_changesets
    from pathlib import Path
    import sys

    validator = InputValidator()
    result = validator.validate_all()
    if not result.success:
        return 1

    commits_dir = Path("/data/commits")
    patches = parse_all_patches(commits_dir)
    changesets = build_all_changesets(patches)

    selector = ConservativeTestSelector(validator.tests)
    sel_validator = SelectionValidator(validator.tests)

    for commit_id, cs in changesets.items():
        decision = selector.select_tests(cs)
        val_result = sel_validator.validate(decision)

        if not val_result.valid:
            print(f"Commit {commit_id}: VALIDATION FAILED", file=sys.stderr)
            for err in val_result.errors:
                print(f"  ERROR: {err}", file=sys.stderr)
        else:
            print(f"Commit {commit_id}: VALID")

        for warn in val_result.warnings:
            print(f"  WARNING: {warn}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
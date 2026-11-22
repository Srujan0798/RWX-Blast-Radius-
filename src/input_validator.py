"""MODULE A — Input Validation

Validates all expected input files and establishes consistent internal representations.
"""

import json
import sys
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


@dataclass
class TestMetadata:
    number: int
    id: str
    file: str
    seconds: float
    skipped: bool = False

    @property
    def duration_ms(self) -> int:
        return int(self.seconds * 1000 + 0.5)


@dataclass
class ValidationResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class InputValidator:
    DATA_DIR = Path("/data")
    TESTS_FILE = DATA_DIR / "tests.json"
    COMMITS_DIR = DATA_DIR / "commits"

    def __init__(self):
        self.tests: list[TestMetadata] = []
        self.test_by_number: dict[int, TestMetadata] = {}
        self.test_by_id: dict[str, TestMetadata] = {}
        self.commit_ids: list[str] = []
        self._validation_result = ValidationResult(success=True)

    def validate_all(self) -> ValidationResult:
        self._validate_tests_file()
        self._validate_commits_dir()
        self._validate_cross_references()
        return self._validation_result

    def _validate_tests_file(self) -> None:
        if not self.TESTS_FILE.exists():
            self._validation_result.success = False
            self._validation_result.errors.append(f"Missing tests.json at {self.TESTS_FILE}")
            return

        try:
            data = json.loads(self.TESTS_FILE.read_text())
        except json.JSONDecodeError as e:
            self._validation_result.success = False
            self._validation_result.errors.append(f"Invalid JSON in tests.json: {e}")
            return

        if "tests" not in data:
            self._validation_result.success = False
            self._validation_result.errors.append("tests.json missing 'tests' key")
            return

        seen_numbers = set()
        seen_ids = set()

        for idx, test_data in enumerate(data["tests"]):
            try:
                test = TestMetadata(
                    number=test_data["number"],
                    id=test_data["id"],
                    file=test_data["file"],
                    seconds=test_data["seconds"],
                    skipped=test_data.get("skipped", False),
                )
            except KeyError as e:
                self._validation_result.success = False
                self._validation_result.errors.append(f"Test {idx} missing required field: {e}")
                continue

            if test.number in seen_numbers:
                self._validation_result.success = False
                self._validation_result.errors.append(f"Duplicate test number: {test.number}")
            seen_numbers.add(test.number)

            if test.id in seen_ids:
                self._validation_result.warnings.append(f"Duplicate test id: {test.id}")
            seen_ids.add(test.id)

            if test.seconds < 0:
                self._validation_result.warnings.append(f"Test {test.number} has negative duration: {test.seconds}")

            self.tests.append(test)
            self.test_by_number[test.number] = test
            self.test_by_id[test.id] = test

        if not self.tests:
            self._validation_result.success = False
            self._validation_result.errors.append("No valid tests found")

        expected_numbers = set(range(len(self.tests)))
        actual_numbers = set(self.test_by_number.keys())
        if expected_numbers != actual_numbers:
            missing = expected_numbers - actual_numbers
            extra = actual_numbers - expected_numbers
            if missing:
                self._validation_result.warnings.append(f"Missing test numbers: {sorted(missing)}")
            if extra:
                self._validation_result.warnings.append(f"Extra test numbers: {sorted(extra)}")

    def _validate_commits_dir(self) -> None:
        if not self.COMMITS_DIR.exists():
            self._validation_result.success = False
            self._validation_result.errors.append(f"Missing commits directory at {self.COMMITS_DIR}")
            return

        patches = list(self.COMMITS_DIR.glob("*.patch"))
        if not patches:
            self._validation_result.success = False
            self._validation_result.errors.append("No .patch files found in commits directory")
            return

        self.commit_ids = sorted(p.stem for p in patches)

    def _validate_cross_references(self) -> None:
        pass

    def get_test(self, number: int) -> TestMetadata | None:
        return self.test_by_number.get(number)

    def get_test_by_id(self, test_id: str) -> TestMetadata | None:
        return self.test_by_id.get(test_id)

    def all_test_numbers(self) -> list[int]:
        return sorted(self.test_by_number.keys())


def main() -> int:
    validator = InputValidator()
    result = validator.validate_all()

    if not result.success:
        for err in result.errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    for warn in result.warnings:
        print(f"WARNING: {warn}", file=sys.stderr)

    print(f"Validated {len(validator.tests)} tests and {len(validator.commit_ids)} commits", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
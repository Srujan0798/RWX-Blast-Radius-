"""MODULE H — Error and Fallback Management

Predictable handling for all error conditions.
"""

import sys
import traceback
from typing import Any
from dataclasses import dataclass
from enum import Enum
from .test_selector import FallbackLevel, UncertaintyLevel, SelectionDecision
from .input_validator import TestMetadata


class ErrorSeverity(Enum):
    RECOVERABLE = "recoverable"
    FALLBACK = "fallback"
    FATAL = "fatal"


@dataclass
class ErrorRecord:
    severity: ErrorSeverity
    component: str
    message: str
    details: dict = None
    fallback_applied: FallbackLevel | None = None


class ErrorHandler:
    def __init__(self, tests: list[TestMetadata]):
        self.tests = tests
        self.all_test_numbers = [t.number for t in tests]
        self.errors: list[ErrorRecord] = []

    def handle_patch_parse_error(self, commit_id: str, error: Exception) -> SelectionDecision:
        self.errors.append(ErrorRecord(
            severity=ErrorSeverity.FALLBACK,
            component="patch_parser",
            message=f"Failed to parse patch for {commit_id}: {error}",
            details={"commit_id": commit_id, "error": str(error)},
            fallback_applied=FallbackLevel.FULL
        ))
        return self._full_fallback_decision(commit_id, "patch_parse_error")

    def handle_invalid_test_numbers(self, commit_id: str, invalid_numbers: list[int]) -> SelectionDecision:
        self.errors.append(ErrorRecord(
            severity=ErrorSeverity.FALLBACK,
            component="selection_validator",
            message=f"Invalid test numbers selected for {commit_id}: {invalid_numbers}",
            details={"commit_id": commit_id, "invalid_numbers": invalid_numbers},
            fallback_applied=FallbackLevel.FULL
        ))
        return self._full_fallback_decision(commit_id, "invalid_test_numbers")

    def handle_serialization_error(self, commit_id: str, error: Exception) -> None:
        self.errors.append(ErrorRecord(
            severity=ErrorSeverity.FATAL,
            component="output_serializer",
            message=f"Failed to serialize output for {commit_id}: {error}",
            details={"commit_id": commit_id, "error": str(error)}
        ))
        print(json.dumps({"commit": commit_id, "workers": []}), file=sys.stdout)

    def handle_unexpected_error(self, commit_id: str, error: Exception, component: str) -> SelectionDecision:
        self.errors.append(ErrorRecord(
            severity=ErrorSeverity.FATAL,
            component=component,
            message=f"Unexpected error in {component} for {commit_id}: {error}",
            details={"commit_id": commit_id, "error": str(error), "traceback": traceback.format_exc()},
            fallback_applied=FallbackLevel.FULL
        ))
        return self._full_fallback_decision(commit_id, f"unexpected_{component}_error")

    def _full_fallback_decision(self, commit_id: str, reason: str) -> SelectionDecision:
        return SelectionDecision(
            commit_id=commit_id,
            selected_test_numbers=self.all_test_numbers.copy(),
            candidate_test_numbers=self.all_test_numbers.copy(),
            mandatory_test_numbers=[],
            uncertain_test_numbers=self.all_test_numbers.copy(),
            fallback_level=FallbackLevel.FULL,
            uncertainty_level=UncertaintyLevel.U3_STRUCTURAL,
            analysis_status=f"fallback_full_suite_{reason}"
        )

    def report_errors(self) -> None:
        for err in self.errors:
            print(f"[{err.severity.value.upper()}] {err.component}: {err.message}", file=sys.stderr)
            if err.details:
                print(f"  Details: {err.details}", file=sys.stderr)


import json
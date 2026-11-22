"""L05 — Safe Test Selection Engine

Sophisticated test selection consuming L04 ImpactEvidence with:
- Evidence classification (E1-E6 categories)
- Mandatory inclusion policies
- 4-tier uncertainty model (U0-U3)
- 4-tier conservative fallback (Local -> Expanded -> Broad -> Full)
- SelectionDecision output with full traceability
"""

import json
from dataclasses import dataclass, field
from typing import Any
from enum import Enum
from pathlib import Path
from collections import defaultdict
from .input_validator import TestMetadata
from .graph_engine import ImpactEvidence, GraphEngine


class EvidenceCategory(Enum):
    E1_DIRECT_COVERAGE = "E1_direct_coverage"
    E2_IMPORT_DEPENDENCY = "E2_import_dependency"
    E3_SYMBOL_REFERENCE = "E3_symbol_reference"
    E4_GRAPH_PROPAGATION = "E4_graph_propagation"
    E5_COVERAGE_EVIDENCE = "E5_coverage_evidence"
    E6_FIXTURE_EVIDENCE = "E6_fixture_evidence"


class UncertaintyLevel(Enum):
    U0_NONE = "U0_none"
    U1_LOCALIZED = "U1_localized"
    U2_SIGNIFICANT = "U2_significant"
    U3_STRUCTURAL = "U3_structural"


class FallbackLevel(Enum):
    NONE = "none"
    LOCAL = "local"
    EXPANDED = "expanded"
    BROAD = "broad"
    FULL = "full"


class MandatoryPolicy(Enum):
    CORE_MODULE = "core_module"
    SECURITY_CRITICAL = "security_critical"
    HIGH_CHURN = "high_churn"
    ALWAYS_RUN = "always_run"


@dataclass
class EvidenceRecord:
    test_number: int
    category: EvidenceCategory
    source: str
    details: str
    commit_id: str
    confidence: float = 1.0
    path: list[str] = field(default_factory=list)


@dataclass
class TestClassification:
    test_number: int
    primary_category: EvidenceCategory
    all_categories: list[EvidenceCategory]
    confidence: float
    evidence_records: list[EvidenceRecord]
    is_mandatory: bool = False
    mandatory_reasons: list[MandatoryPolicy] = field(default_factory=list)


@dataclass
class SelectionDecision:
    commit_id: str
    selected_test_numbers: list[int] = field(default_factory=list)
    candidate_test_numbers: list[int] = field(default_factory=list)
    mandatory_test_numbers: list[int] = field(default_factory=list)
    uncertain_test_numbers: list[int] = field(default_factory=list)
    excluded_test_numbers: list[int] = field(default_factory=list)
    evidence_records: list[EvidenceRecord] = field(default_factory=list)
    fallback_level: FallbackLevel = FallbackLevel.NONE
    uncertainty_level: UncertaintyLevel = UncertaintyLevel.U0_NONE
    analysis_status: str = "ok"
    test_classifications: dict[int, TestClassification] = field(default_factory=dict)
    traceability: dict = field(default_factory=dict)


CORE_MODULES = {
    "sqlglot.parser",
    "sqlglot.generator",
    "sqlglot.optimizer",
    "sqlglot.expressions",
    "sqlglot.dialects",
    "sqlglot.executor",
    "sqlglot.serde",
}

SECURITY_CRITICAL_PATTERNS = [
    "sqlglot.parser",
    "sqlglot.generator",
    "sqlglot.tokens",
    "sqlglot.errors",
]

HIGH_CHURN_THRESHOLD = 3

ALWAYS_RUN_TESTS = {
    "tests.test_parser",
    "tests.test_generator",
    "tests.test_optimizer",
    "tests.test_expressions",
}


def load_coverage_history(path: str = "/app/graph_artifacts/coverage_history.json") -> dict[int, float]:
    if not Path(path).exists():
        return {}
    with open(path) as f:
        data = json.load(f)
    return {int(k): float(v) for k, v in data.get("test_coverage", {}).items()}


def load_churn_data(path: str = "/app/graph_artifacts/churn_data.json") -> dict[str, int]:
    if not Path(path).exists():
        return {}
    with open(path) as f:
        return json.load(f)


class SafeTestSelector:
    def __init__(
        self,
        tests: list[TestMetadata],
        graph_engine: GraphEngine | None = None,
        coverage_history_path: str | None = None,
        churn_data_path: str | None = None,
    ):
        self.tests = tests
        self.test_by_number = {t.number: t for t in tests}
        self.test_by_file: dict[str, list[int]] = defaultdict(list)
        self._build_file_index()

        self.graph_engine = graph_engine
        self.coverage_history = load_coverage_history(coverage_history_path) if coverage_history_path else {}
        self.churn_data = load_churn_data(churn_data_path) if churn_data_path else {}

        self.module_to_tests: dict[str, list[int]] = defaultdict(list)
        self._build_module_index()

    def _build_file_index(self) -> None:
        for test in self.tests:
            self.test_by_file[test.file].append(test.number)

    def _build_module_index(self) -> None:
        for test in self.tests:
            test_module = test.file.replace("/", ".").replace(".py", "")
            self.module_to_tests[test_module].append(test.number)

    def select_tests(self, evidence: ImpactEvidence) -> SelectionDecision:
        decision = SelectionDecision(commit_id=evidence.commit_id)

        if evidence.graph_analysis_status != "ok":
            decision.uncertainty_level = UncertaintyLevel.U3_STRUCTURAL
            decision.fallback_level = FallbackLevel.FULL
            decision.selected_test_numbers = self._full_suite_fallback()
            decision.analysis_status = f"fallback_full_suite_{evidence.graph_analysis_status}"
            self._finalize_decision(decision)
            return decision

        decision.candidate_test_numbers = sorted(set(evidence.candidate_tests))
        decision.test_classifications = self._classify_candidates(evidence, decision)
        decision.mandatory_test_numbers = sorted(
            t for t, cls in decision.test_classifications.items() if cls.is_mandatory
        )

        uncertainty = self._assess_uncertainty(evidence, decision)
        decision.uncertainty_level = uncertainty

        if uncertainty == UncertaintyLevel.U3_STRUCTURAL:
            decision.fallback_level = FallbackLevel.FULL
            decision.selected_test_numbers = self._full_suite_fallback()
        elif uncertainty == UncertaintyLevel.U2_SIGNIFICANT:
            decision.fallback_level = FallbackLevel.BROAD
            decision.selected_test_numbers = self._broad_fallback(evidence, decision)
        elif uncertainty == UncertaintyLevel.U1_LOCALIZED:
            decision.fallback_level = FallbackLevel.EXPANDED
            decision.selected_test_numbers = self._expanded_fallback(evidence, decision)
        else:
            decision.fallback_level = FallbackLevel.LOCAL
            decision.selected_test_numbers = self._local_selection(evidence, decision)

        if len(decision.candidate_test_numbers) < 20 and decision.fallback_level == FallbackLevel.LOCAL:
            decision.fallback_level = FallbackLevel.EXPANDED
            decision.selected_test_numbers = self._expanded_fallback(evidence, decision)

        decision.selected_test_numbers = sorted(set(decision.selected_test_numbers) | set(decision.mandatory_test_numbers))
        self._finalize_decision(decision)
        return decision

    def _classify_candidates(self, evidence: ImpactEvidence, decision: SelectionDecision) -> dict[int, TestClassification]:
        classifications: dict[int, TestClassification] = {}
        all_evidence: dict[int, list[EvidenceRecord]] = defaultdict(list)

        for test_num in evidence.candidate_tests:
            test = self.test_by_number.get(test_num)
            if not test:
                continue

            categories: list[EvidenceCategory] = []
            confidence = 0.0

            for covered_file in evidence.impacted_files:
                if test.file == covered_file or test.file.replace(".py", "") == covered_file.replace(".py", ""):
                    cat = EvidenceCategory.E1_DIRECT_COVERAGE
                    categories.append(cat)
                    confidence = max(confidence, 1.0)
                    all_evidence[test_num].append(EvidenceRecord(
                        test_number=test_num,
                        category=cat,
                        source="direct_file_coverage",
                        details=f"Test directly covers changed file {covered_file}",
                        commit_id=evidence.commit_id,
                        confidence=1.0,
                        path=[covered_file],
                    ))

            for module in evidence.impacted_modules:
                test_module = test.file.replace("/", ".").replace(".py", "")
                if test_module == module or test_module.startswith(module + "."):
                    cat = EvidenceCategory.E2_IMPORT_DEPENDENCY
                    categories.append(cat)
                    confidence = max(confidence, 0.9)
                    all_evidence[test_num].append(EvidenceRecord(
                        test_number=test_num,
                        category=cat,
                        source="module_import_dependency",
                        details=f"Test module {test_module} imports or depends on {module}",
                        commit_id=evidence.commit_id,
                        confidence=0.9,
                        path=[module, test_module],
                    ))

            for symbol in evidence.impacted_symbols:
                test_module = test.file.replace("/", ".").replace(".py", "")
                if symbol.startswith(test_module + ".") or symbol == test_module:
                    cat = EvidenceCategory.E3_SYMBOL_REFERENCE
                    categories.append(cat)
                    confidence = max(confidence, 0.85)
                    all_evidence[test_num].append(EvidenceRecord(
                        test_number=test_num,
                        category=cat,
                        source="symbol_reference",
                        details=f"Test references impacted symbol {symbol}",
                        commit_id=evidence.commit_id,
                        confidence=0.85,
                        path=[symbol, test_module],
                    ))

            if test_num in evidence.candidate_tests:
                cat = EvidenceCategory.E4_GRAPH_PROPAGATION
                categories.append(cat)
                confidence = max(confidence, 0.7)
                all_evidence[test_num].append(EvidenceRecord(
                    test_number=test_num,
                    category=cat,
                    source="graph_propagation",
                    details="Test reached via graph propagation from changed files",
                    commit_id=evidence.commit_id,
                    confidence=0.7,
                    path=[],
                ))

            for test_evidence, details in evidence.coverage_evidence:
                if test_evidence == test_num:
                    cat = EvidenceCategory.E5_COVERAGE_EVIDENCE
                    categories.append(cat)
                    confidence = max(confidence, 0.75)
                    all_evidence[test_num].append(EvidenceRecord(
                        test_number=test_num,
                        category=cat,
                        source="historical_coverage",
                        details=f"Historical coverage: {details}",
                        commit_id=evidence.commit_id,
                        confidence=0.75,
                        path=[],
                    ))

            for test_evidence, details in evidence.fixture_evidence:
                if test_evidence == test_num:
                    cat = EvidenceCategory.E6_FIXTURE_EVIDENCE
                    categories.append(cat)
                    confidence = max(confidence, 0.8)
                    all_evidence[test_num].append(EvidenceRecord(
                        test_number=test_num,
                        category=cat,
                        source="fixture_dependency",
                        details=f"Test depends on fixture: {details}",
                        commit_id=evidence.commit_id,
                        confidence=0.8,
                        path=[],
                    ))

            if not categories:
                cat = EvidenceCategory.E4_GRAPH_PROPAGATION
                categories.append(cat)
                confidence = 0.5

            primary = max(categories, key=lambda c: {
                EvidenceCategory.E1_DIRECT_COVERAGE: 1.0,
                EvidenceCategory.E2_IMPORT_DEPENDENCY: 0.9,
                EvidenceCategory.E3_SYMBOL_REFERENCE: 0.85,
                EvidenceCategory.E5_COVERAGE_EVIDENCE: 0.75,
                EvidenceCategory.E6_FIXTURE_EVIDENCE: 0.8,
                EvidenceCategory.E4_GRAPH_PROPAGATION: 0.7,
            }[c])

            is_mandatory, reasons = self._check_mandatory(test, test_module := test.file.replace("/", ".").replace(".py", ""), evidence)

            cls = TestClassification(
                test_number=test_num,
                primary_category=primary,
                all_categories=list(set(categories)),
                confidence=confidence,
                evidence_records=all_evidence[test_num],
                is_mandatory=is_mandatory,
                mandatory_reasons=reasons,
            )
            classifications[test_num] = cls

        decision.evidence_records = [rec for records in all_evidence.values() for rec in records]
        return classifications

    def _check_mandatory(self, test: TestMetadata, test_module: str, evidence: ImpactEvidence) -> tuple[bool, list[MandatoryPolicy]]:
        reasons = []

        if any(test_module.startswith(core) for core in CORE_MODULES):
            reasons.append(MandatoryPolicy.CORE_MODULE)

        if any(test_module.startswith(sec) for sec in SECURITY_CRITICAL_PATTERNS):
            reasons.append(MandatoryPolicy.SECURITY_CRITICAL)

        churn = self.churn_data.get(test_module, 0)
        if churn >= HIGH_CHURN_THRESHOLD:
            reasons.append(MandatoryPolicy.HIGH_CHURN)

        if test_module in ALWAYS_RUN_TESTS:
            reasons.append(MandatoryPolicy.ALWAYS_RUN)

        return len(reasons) > 0, reasons

    def _assess_uncertainty(self, evidence: ImpactEvidence, decision: SelectionDecision) -> UncertaintyLevel:
        if evidence.dynamic_feature_flags:
            return UncertaintyLevel.U3_STRUCTURAL

        if evidence.unresolved_relationships:
            return UncertaintyLevel.U2_SIGNIFICANT

        if len(evidence.impacted_files) > 15:
            return UncertaintyLevel.U2_SIGNIFICANT

        if len(evidence.impacted_modules) > 10:
            return UncertaintyLevel.U1_LOCALIZED

        if len(evidence.candidate_tests) == 0:
            return UncertaintyLevel.U2_SIGNIFICANT

        if len(evidence.candidate_tests) > 50:
            return UncertaintyLevel.U1_LOCALIZED

        low_confidence = sum(1 for cls in decision.test_classifications.values() if cls.confidence < 0.7)
        if low_confidence > len(decision.test_classifications) * 0.3:
            return UncertaintyLevel.U1_LOCALIZED

        return UncertaintyLevel.U0_NONE

    def _local_selection(self, evidence: ImpactEvidence, decision: SelectionDecision) -> list[int]:
        selected = set(decision.mandatory_test_numbers)

        for test_num, cls in decision.test_classifications.items():
            if cls.primary_category in (EvidenceCategory.E1_DIRECT_COVERAGE, EvidenceCategory.E2_IMPORT_DEPENDENCY):
                selected.add(test_num)

        return sorted(selected)

    def _expanded_fallback(self, evidence: ImpactEvidence, decision: SelectionDecision) -> list[int]:
        selected = set(self._local_selection(evidence, decision))

        for test_num, cls in decision.test_classifications.items():
            if cls.primary_category in (EvidenceCategory.E3_SYMBOL_REFERENCE, EvidenceCategory.E6_FIXTURE_EVIDENCE):
                selected.add(test_num)

        for module in evidence.impacted_modules:
            for test_num in self.module_to_tests.get(module, []):
                selected.add(test_num)
            for test_num in self.module_to_tests.get(module + ".*", []):
                selected.add(test_num)

        return sorted(selected)

    def _broad_fallback(self, evidence: ImpactEvidence, decision: SelectionDecision) -> list[int]:
        selected = set(self._expanded_fallback(evidence, decision))

        for test_num, cls in decision.test_classifications.items():
            if cls.primary_category == EvidenceCategory.E4_GRAPH_PROPAGATION:
                selected.add(test_num)

        for module in evidence.impacted_modules:
            top_level = module.split(".")[0]
            for mod, tests in self.module_to_tests.items():
                if mod.startswith(top_level + "."):
                    selected.update(tests)

        return sorted(selected)

    def _full_suite_fallback(self) -> list[int]:
        return sorted(self.test_by_number.keys())

    def _finalize_decision(self, decision: SelectionDecision) -> None:
        decision.uncertain_test_numbers = sorted(
            t for t in decision.selected_test_numbers
            if t not in decision.mandatory_test_numbers
        )
        all_tests = set(self.test_by_number.keys())
        decision.excluded_test_numbers = sorted(all_tests - set(decision.selected_test_numbers))

        decision.traceability = {
            "commit_id": decision.commit_id,
            "total_tests": len(all_tests),
            "selected_count": len(decision.selected_test_numbers),
            "mandatory_count": len(decision.mandatory_test_numbers),
            "uncertain_count": len(decision.uncertain_test_numbers),
            "excluded_count": len(decision.excluded_test_numbers),
            "candidate_count": len(decision.candidate_test_numbers),
            "fallback_level": decision.fallback_level.value,
            "uncertainty_level": decision.uncertainty_level.value,
            "analysis_status": decision.analysis_status,
            "evidence_breakdown": self._evidence_breakdown(decision),
            "mandatory_breakdown": self._mandatory_breakdown(decision),
        }

    def _evidence_breakdown(self, decision: SelectionDecision) -> dict[str, int]:
        breakdown = defaultdict(int)
        for rec in decision.evidence_records:
            breakdown[rec.category.value] += 1
        return dict(breakdown)

    def _mandatory_breakdown(self, decision: SelectionDecision) -> dict[str, int]:
        breakdown = defaultdict(int)
        for test_num in decision.mandatory_test_numbers:
            cls = decision.test_classifications.get(test_num)
            if cls:
                for reason in cls.mandatory_reasons:
                    breakdown[reason.value] += 1
        return dict(breakdown)


def main() -> int:
    from .input_validator import InputValidator
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

    ast_metadata_path = "/app/graph_artifacts/ast_metadata.json"
    tests_path = "/data/tests.json"

    graph_engine = GraphEngine(ast_metadata_path, tests_path)
    selector = SafeTestSelector(
        validator.tests,
        graph_engine,
        coverage_history_path="/app/graph_artifacts/coverage_history.json",
        churn_data_path="/app/graph_artifacts/churn_data.json",
    )

    for commit_id, cs in changesets.items():
        evidence = graph_engine.propagate_impact(cs)
        decision = selector.select_tests(evidence)

        print(f"Commit: {commit_id}")
        print(f"  Selected: {len(decision.selected_test_numbers)} tests")
        print(f"  Candidates: {len(decision.candidate_test_numbers)}")
        print(f"  Mandatory: {len(decision.mandatory_test_numbers)}")
        print(f"  Fallback: {decision.fallback_level.value}")
        print(f"  Uncertainty: {decision.uncertainty_level.value}")
        print(f"  Status: {decision.analysis_status}")
        print(f"  Evidence breakdown: {decision.traceability.get('evidence_breakdown', {})}")
        print(f"  Mandatory breakdown: {decision.traceability.get('mandatory_breakdown', {})}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
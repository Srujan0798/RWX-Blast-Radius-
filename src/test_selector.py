"""MODULE D — Initial Test-Selection Engine

Conservative first selection policy using officially permitted information.
Implements 4-tier fallback: Local -> Expanded -> Broad -> Full suite.
L03 enhancement: AST-based symbol-level dependency analysis.
L04 enhancement: Graph-based impact propagation via GraphEngine.
"""

import json
from dataclasses import dataclass, field
from typing import Any
from enum import Enum
from pathlib import Path
from .changeset import ChangeSet
from .input_validator import TestMetadata
from .graph_engine import GraphEngine, ImpactEvidence


class EvidenceCategory(Enum):
    DIRECT_COVERAGE = "direct_coverage"
    IMPORT_DEPENDENCY = "import_dependency"
    SYMBOL_REFERENCE = "symbol_reference"
    GRAPH_PROPAGATION = "graph_propagation"
    COVERAGE_EVIDENCE = "coverage_evidence"
    FIXTURE_EVIDENCE = "fixture_evidence"
    UNCERTAINTY = "uncertainty"


class UncertaintyLevel(Enum):
    U0_NONE = "U0_none"
    U1_LOCALIZED = "U1_localized"
    U2_SIGNIFICANT = "U2_significant"
    U3_STRUCTURAL = "U3_structural"


class FallbackLevel(Enum):
    NONE = "none"
    LOCAL = "local_expansion"
    EXPANDED = "expanded_dependency"
    BROAD = "broad_selection"
    FULL = "full_suite"


@dataclass
class EvidenceRecord:
    test_number: int
    category: EvidenceCategory
    source: str
    details: str
    commit_id: str


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


SOURCE_TO_TEST_MODULE = {
    "sqlglot.dialects": "tests.dialects",
    "sqlglot.optimizer": "tests.test_optimizer",
    "sqlglot.parsers": "tests.test_parser",
    "sqlglot.generators": "tests.test_generator",
    "sqlglot.executor": "tests.test_executor",
    "sqlglot.expressions": "tests.test_expressions",
    "sqlglot.serde": "tests.test_serde",
    "sqlglot.transforms": "tests.test_transforms",
    "sqlglot.typing": "tests.test_typing",
    "sqlglot.dialect": "tests.dialects",
    "sqlglot.parser": "tests.test_parser",
    "sqlglot.generator": "tests.test_generator",
    "sqlglot.tokens": "tests.test_tokens",
    "sqlglot.schema": "tests.test_schema",
    "sqlglot.lineage": "tests.test_lineage",
    "sqlglot.helper": "tests.test_helper",
    "sqlglot.errors": "tests.test_errors",
    "sqlglot.diff": "tests.test_diff",
    "sqlglot.build": "tests.test_build",
    "sqlglot.anonymize": "tests.test_anonymize",
    "sqlglot.jsonpath": "tests.test_jsonpath",
    "sqlglot.time": "tests.test_time",
    "sqlglot.transpile": "tests.test_transpile",
    "sqlglot.simplify": "tests.test_simplify_between",
}

FIXTURE_TO_TEST_MODULE = {
    "tests.fixtures.optimizer": "tests.test_optimizer",
}

CORE_MODULE_CROSS_DEPS = {
    "sqlglot.optimizer": ["tests.test_executor", "tests.test_expressions", "tests.test_parser"],
    "sqlglot.serde": ["tests.test_executor", "tests.test_expressions"],
    "sqlglot.transforms": ["tests.test_optimizer", "tests.test_parser", "tests.test_expressions"],
    "sqlglot.parsers": ["tests.test_optimizer", "tests.test_expressions"],
    "sqlglot.generators": ["tests.test_optimizer", "tests.test_expressions"],
    "sqlglot.expressions": ["tests.test_optimizer", "tests.test_parser", "tests.test_generator"],
    "sqlglot.executor": ["tests.test_optimizer", "tests.test_expressions"],
}


DIALECT_PARSER_MAP = {
    "dremio": "tests.dialects.test_dremio",
    "bigquery": "tests.dialects.test_bigquery",
    "clickhouse": "tests.dialects.test_clickhouse",
    "snowflake": "tests.dialects.test_snowflake",
    "databricks": "tests.dialects.test_databricks",
    "postgres": "tests.dialects.test_postgres",
    "mysql": "tests.dialects.test_mysql",
    "sqlite": "tests.dialects.test_sqlite",
    "tsql": "tests.dialects.test_tsql",
    "presto": "tests.dialects.test_presto",
    "spark": "tests.dialects.test_spark",
    "redshift": "tests.dialects.test_redshift",
    "athena": "tests.dialects.test_athena",
    "drill": "tests.dialects.test_drill",
    "duckdb": "tests.dialects.test_duckdb",
    "teradata": "tests.dialects.test_teradata",
    "oracle": "tests.dialects.test_oracle",
}

DIALECT_GENERATOR_MAP = DIALECT_PARSER_MAP.copy()

ALL_DIALECT_TESTS = list(DIALECT_PARSER_MAP.values())


class ConservativeTestSelector:
    def __init__(self, tests: list[TestMetadata], ast_metadata_path: str | None = None, tests_path: str | None = None):
        self.tests = tests
        self.test_by_number = {t.number: t for t in tests}
        self.test_by_file: dict[str, list[int]] = {}
        self._build_file_index()

        self.ast_metadata = None
        self.symbol_index: dict[str, Any] = {}
        self.name_definition_index: dict[str, list[str]] = {}
        self.name_usage_index: dict[str, list[str]] = {}
        self.module_index: dict[str, Any] = {}

        self.graph_engine: GraphEngine | None = None
        if ast_metadata_path and Path(ast_metadata_path).exists():
            self._load_ast_metadata(ast_metadata_path)
            if tests_path and Path(tests_path).exists():
                self.graph_engine = GraphEngine(ast_metadata_path, tests_path)

    def _load_ast_metadata(self, path: str) -> None:
        with open(path) as f:
            self.ast_metadata = json.load(f)
        self.symbol_index = self.ast_metadata.get("symbol_index", {})
        self.name_definition_index = self.ast_metadata.get("name_definition_index", {})
        self.name_usage_index = self.ast_metadata.get("name_usage_index", {})
        self.module_index = self.ast_metadata.get("module_index", {})

    def _build_file_index(self) -> None:
        for test in self.tests:
            if test.file not in self.test_by_file:
                self.test_by_file[test.file] = []
            self.test_by_file[test.file].append(test.number)

    def select_tests(self, changeset: ChangeSet) -> SelectionDecision:
        decision = SelectionDecision(commit_id=changeset.commit_id)

        if changeset.parse_status == "error" or changeset.parse_errors:
            decision.uncertainty_level = UncertaintyLevel.U3_STRUCTURAL
            decision.fallback_level = FallbackLevel.FULL
            decision.selected_test_numbers = self._full_suite_fallback()
            decision.analysis_status = "fallback_full_suite_parse_error"
            return decision

        python_files = changeset.get_python_files()
        all_changed_files = changeset.get_all_changed_paths()

        if not all_changed_files:
            decision.selected_test_numbers = []
            decision.analysis_status = "no_changes"
            return decision

        candidate_tests = self._collect_candidates(changeset, decision)
        decision.candidate_test_numbers = sorted(set(candidate_tests))

        uncertainty = self._assess_uncertainty(changeset, len(candidate_tests))
        decision.uncertainty_level = uncertainty

        if uncertainty == UncertaintyLevel.U3_STRUCTURAL:
            decision.fallback_level = FallbackLevel.FULL
            decision.selected_test_numbers = self._full_suite_fallback()
        elif uncertainty == UncertaintyLevel.U2_SIGNIFICANT:
            decision.fallback_level = FallbackLevel.BROAD
            decision.selected_test_numbers = self._broad_fallback(python_files, decision)
        elif uncertainty == UncertaintyLevel.U1_LOCALIZED:
            decision.fallback_level = FallbackLevel.LOCAL
            decision.selected_test_numbers = self._local_expansion(python_files, decision)
        else:
            decision.fallback_level = FallbackLevel.NONE
            if len(candidate_tests) < 20:
                decision.fallback_level = FallbackLevel.LOCAL
                decision.selected_test_numbers = self._local_expansion(python_files, decision)
            else:
                decision.selected_test_numbers = sorted(set(decision.candidate_test_numbers))

        decision.mandatory_test_numbers = sorted(
            t for t in decision.selected_test_numbers
            if any(e.test_number == t and e.category == EvidenceCategory.DIRECT_COVERAGE
                   for e in decision.evidence_records)
        )

        decision.selected_test_numbers = sorted(set(decision.selected_test_numbers))
        return decision

    def _collect_candidates(self, changeset: ChangeSet, decision: SelectionDecision) -> list[int]:
        candidates = set()

        if self.graph_engine:
            changeset_dict = {
                "commit_id": changeset.commit_id,
                "python_files": changeset.get_python_files(),
                "all_changed_files": changeset.get_all_changed_paths(),
            }
            evidence: ImpactEvidence = self.graph_engine.propagate_impact(changeset_dict)

            for test_num in evidence.candidate_tests:
                candidates.add(test_num)
                decision.evidence_records.append(EvidenceRecord(
                    test_number=test_num,
                    category=EvidenceCategory.GRAPH_PROPAGATION,
                    source="graph_propagation",
                    details=f"Graph-engine propagated impact to test {test_num}",
                    commit_id=changeset.commit_id
                ))

            for mod in evidence.impacted_modules:
                decision.evidence_records.append(EvidenceRecord(
                    test_number=0,
                    category=EvidenceCategory.GRAPH_PROPAGATION,
                    source="graph_impacted_module",
                    details=f"Impacted module: {mod}",
                    commit_id=changeset.commit_id
                ))

            for sym in evidence.impacted_symbols:
                decision.evidence_records.append(EvidenceRecord(
                    test_number=0,
                    category=EvidenceCategory.GRAPH_PROPAGATION,
                    source="graph_impacted_symbol",
                    details=f"Impacted symbol: {sym}",
                    commit_id=changeset.commit_id
                ))

            for test_num, cov_type in evidence.coverage_evidence:
                if test_num not in candidates:
                    candidates.add(test_num)
                    decision.evidence_records.append(EvidenceRecord(
                        test_number=test_num,
                        category=EvidenceCategory.COVERAGE_EVIDENCE,
                        source="graph_coverage",
                        details=f"Coverage evidence: {cov_type}",
                        commit_id=changeset.commit_id
                    ))

            for test_num, fixture in evidence.fixture_evidence:
                if test_num not in candidates:
                    candidates.add(test_num)
                    decision.evidence_records.append(EvidenceRecord(
                        test_number=test_num,
                        category=EvidenceCategory.FIXTURE_EVIDENCE,
                        source="graph_fixture",
                        details=f"Fixture dependency: {fixture}",
                        commit_id=changeset.commit_id
                    ))

            if evidence.dynamic_feature_flags:
                decision.evidence_records.append(EvidenceRecord(
                    test_number=0,
                    category=EvidenceCategory.UNCERTAINTY,
                    source="graph_dynamic_features",
                    details=f"Dynamic features detected: {evidence.dynamic_feature_flags}",
                    commit_id=changeset.commit_id
                ))

        for py_file in changeset.get_python_files():
            if py_file in self.test_by_file:
                for test_num in self.test_by_file[py_file]:
                    if test_num not in candidates:
                        candidates.add(test_num)
                        decision.evidence_records.append(EvidenceRecord(
                            test_number=test_num,
                            category=EvidenceCategory.DIRECT_COVERAGE,
                            source="file_coverage",
                            details=f"Test covers changed file {py_file}",
                            commit_id=changeset.commit_id
                        ))

        for fixture_file in changeset.get_all_changed_paths():
            if fixture_file.startswith("tests/fixtures/"):
                fixture_tests = self._find_fixture_dependents(fixture_file)
                for test_num in fixture_tests:
                    if test_num not in candidates:
                        candidates.add(test_num)
                        decision.evidence_records.append(EvidenceRecord(
                            test_number=test_num,
                            category=EvidenceCategory.FIXTURE_EVIDENCE,
                            source="fixture_dependency",
                            details=f"Test may depend on fixture {fixture_file}",
                            commit_id=changeset.commit_id
                        ))

        return list(candidates)

    def _find_symbol_dependents(self, py_file: str, changeset: ChangeSet) -> list[int]:
        if not self.ast_metadata:
            return []

        src_module = py_file.replace("/", ".").replace(".py", "")
        dependents = []

        changed_symbols = self._get_changed_symbols(py_file, changeset)
        for sym_name in changed_symbols:
            test_modules = self.name_usage_index.get(sym_name, [])
            for test_module in test_modules:
                if test_module.startswith("tests."):
                    for test in self.tests:
                        if test.file.startswith(test_module.replace(".", "/")):
                            dependents.append(test.number)

        return list(set(dependents))

    def _get_changed_symbols(self, py_file: str, changeset: ChangeSet) -> set[str]:
        changed = set()
        src_module = py_file.replace("/", ".").replace(".py", "")
        if py_file in changeset.added_lines:
            for line_num in changeset.added_lines[py_file]:
                for sym_id, symbol in self.symbol_index.items():
                    if symbol.get("module_path") == src_module and symbol.get("start_line", 0) <= line_num <= symbol.get("end_line", 0):
                        changed.add(symbol.get("qualified_name", ""))
        return changed

    def _find_fixture_dependents(self, fixture_file: str) -> list[int]:
        dependents = []

        for prefix, test_module in FIXTURE_TO_TEST_MODULE.items():
            if fixture_file.startswith(prefix.replace(".", "/")):
                for test in self.tests:
                    if test.file.startswith(test_module.replace(".", "/")):
                        dependents.append(test.number)
                break

        if not dependents:
            for test in self.tests:
                if "optimizer" in test.file and "optimizer" in fixture_file:
                    dependents.append(test.number)

        return dependents

    def _find_import_dependents(self, py_file: str) -> list[int]:
        dependents = []

        src_module = py_file.replace("/", ".").replace(".py", "")
        test_module = SOURCE_TO_TEST_MODULE.get(src_module)

        if not test_module:
            parts = src_module.split(".")
            for i in range(len(parts), 0, -1):
                prefix = ".".join(parts[:i])
                if prefix in SOURCE_TO_TEST_MODULE:
                    test_module = SOURCE_TO_TEST_MODULE[prefix]
                    break

        if test_module:
            for test in self.tests:
                if test.file.startswith(test_module.replace(".", "/")):
                    dependents.append(test.number)

        if not dependents:
            for test in self.tests:
                test_file = test.file
                if self._path_structurally_related(py_file, test_file):
                    dependents.append(test.number)

        return dependents

    def _path_structurally_related(self, src_file: str, test_file: str) -> bool:
        src_parts = src_file.replace(".py", "").split("/")
        test_parts = test_file.replace(".py", "").split("/")

        if len(src_parts) < 2 or len(test_parts) < 2:
            return False

        src_components = set(src_parts)
        test_components = set(test_parts)

        common = src_components & test_components
        if common:
            return True

        return False

    def _assess_uncertainty(self, changeset: ChangeSet, candidate_count: int) -> UncertaintyLevel:
        if changeset.parse_errors:
            return UncertaintyLevel.U3_STRUCTURAL

        if changeset.dynamic_flags:
            return UncertaintyLevel.U2_SIGNIFICANT

        if changeset.unresolved_ranges:
            return UncertaintyLevel.U1_LOCALIZED

        python_files = changeset.get_python_files()
        if len(python_files) > 10:
            return UncertaintyLevel.U1_LOCALIZED

        if candidate_count == 0:
            return UncertaintyLevel.U2_SIGNIFICANT

        if candidate_count < 20:
            return UncertaintyLevel.U1_LOCALIZED

        return UncertaintyLevel.U0_NONE

    DIALECT_PARSER_MAP = {
        "dremio": "tests.dialects.test_dremio",
        "bigquery": "tests.dialects.test_bigquery",
        "clickhouse": "tests.dialects.test_clickhouse",
        "snowflake": "tests.dialects.test_snowflake",
        "databricks": "tests.dialects.test_databricks",
        "postgres": "tests.dialects.test_postgres",
        "mysql": "tests.dialects.test_mysql",
        "sqlite": "tests.dialects.test_sqlite",
        "tsql": "tests.dialects.test_tsql",
        "presto": "tests.dialects.test_presto",
        "spark": "tests.dialects.test_spark",
        "redshift": "tests.dialects.test_redshift",
        "athena": "tests.dialects.test_athena",
        "drill": "tests.dialects.test_drill",
        "duckdb": "tests.dialects.test_duckdb",
        "teradata": "tests.dialects.test_teradata",
        "oracle": "tests.dialects.test_oracle",
    }

    DIALECT_GENERATOR_MAP = DIALECT_PARSER_MAP.copy()

    ALL_DIALECT_TESTS = list(DIALECT_PARSER_MAP.values())

    def _local_expansion(self, python_files: set[str], decision: SelectionDecision) -> list[int]:
        expanded = set(decision.candidate_test_numbers)

        for py_file in python_files:
            related = self._find_related_modules(py_file)
            for mod in related:
                mod_file = mod.replace(".", "/") + ".py"
                if mod_file in self.test_by_file:
                    expanded.update(self.test_by_file[mod_file])

            src_module = py_file.replace("/", ".").replace(".py", "")
            
            # Handle core module cross-deps (reduced set)
            if src_module in CORE_MODULE_CROSS_DEPS:
                for cross_test_module in CORE_MODULE_CROSS_DEPS[src_module]:
                    for test in self.tests:
                        if test.file.startswith(cross_test_module.replace(".", "/")):
                            expanded.add(test.number)

            # Handle dialect-specific parser changes
            if src_module.startswith("sqlglot.parsers."):
                dialect = src_module.split(".")[-1]
                if dialect in DIALECT_PARSER_MAP:
                    cross_module = DIALECT_PARSER_MAP[dialect]
                    for test in self.tests:
                        if test.file.startswith(cross_module.replace(".", "/")):
                            expanded.add(test.number)
                else:
                    # Unknown parser dialect - only add test_optimizer
                    for test in self.tests:
                        if test.file.startswith("tests/test_optimizer/"):
                            expanded.add(test.number)

            # Handle dialect-specific generator changes
            if src_module.startswith("sqlglot.generators."):
                dialect = src_module.split(".")[-1]
                if dialect in DIALECT_GENERATOR_MAP:
                    cross_module = DIALECT_GENERATOR_MAP[dialect]
                    for test in self.tests:
                        if test.file.startswith(cross_module.replace(".", "/")):
                            expanded.add(test.number)
                else:
                    for test in self.tests:
                        if test.file.startswith("tests/test_optimizer/"):
                            expanded.add(test.number)

            # Core parser/generator changes affect all dialects
            # Core parser/generator changes - rely on symbol analysis and specific dialect mapping
            # Don't add ALL_DIALECT_TESTS - rely on graph engine's symbol analysis

            # Handle dialect module changes (e.g., sqlglot.dialects.tsql)
            if src_module.startswith("sqlglot.dialects."):
                dialect = src_module.split(".")[-1]
                if dialect in DIALECT_PARSER_MAP:
                    cross_module = DIALECT_PARSER_MAP[dialect]
                    for test in self.tests:
                        if test.file.startswith(cross_module.replace(".", "/")):
                            expanded.add(test.number)
                else:
                    # Unknown dialect - only add test_optimizer
                    for test in self.tests:
                        if test.file.startswith("tests/test_optimizer/"):
                            expanded.add(test.number)

        return sorted(expanded)

    def _find_related_modules(self, py_file: str) -> set[str]:
        module = py_file.replace("/", ".").replace(".py", "")
        parts = module.split(".")
        related = {module}

        for i in range(1, len(parts)):
            related.add(".".join(parts[:i]))

        return related

    def _broad_fallback(self, python_files: set[str], decision: SelectionDecision) -> list[int]:
        expanded = set(decision.candidate_test_numbers)

        for py_file in python_files:
            top_level = py_file.split("/")[0]
            for test in self.tests:
                if test.file.startswith(top_level + "/"):
                    expanded.add(test.number)

        return sorted(expanded)

    def _full_suite_fallback(self) -> list[int]:
        return [t.number for t in self.tests]


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
    selector = ConservativeTestSelector(validator.tests, ast_metadata_path, tests_path)

    for commit_id, cs in changesets.items():
        decision = selector.select_tests(cs)
        print(f"Commit: {commit_id}")
        print(f"  Selected: {len(decision.selected_test_numbers)} tests")
        print(f"  Candidates: {len(decision.candidate_test_numbers)}")
        print(f"  Fallback: {decision.fallback_level.value}")
        print(f"  Uncertainty: {decision.uncertainty_level.value}")
        print(f"  Status: {decision.analysis_status}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
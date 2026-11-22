from __future__ import annotations

import json
from pathlib import Path
import zlib

from .changeset import ChangeSet
from .input_validator import TestMetadata
from .special_rules import SpecialRules
from .test_selector import FallbackLevel, SelectionDecision, UncertaintyLevel


class CoverageSelector:
    def __init__(self, tests: list[TestMetadata], map_path: Path | None = None, source_root: Path | None = None):
        self.tests = tests
        if source_root is None:
            default_source_root = Path("/app/sqlglot")
            self.source_root = default_source_root if default_source_root.is_dir() else None
        else:
            self.source_root = source_root
        self.tests_by_id = {test.id: test for test in tests}
        self.tests_by_file: dict[str, list[int]] = {}
        for test in tests:
            self.tests_by_file.setdefault(test.file, []).append(test.number)

        if map_path is None:
            map_path = Path(__file__).resolve().parent.parent / "maps" / "maps.json.z"
        self.map_path = Path(map_path)
        document = json.loads(zlib.decompress(map_path.read_bytes()))
        if document["source_commit"] != "eb11aec4be8cb2122afe713a4816662c3f0fb2fa":
            raise ValueError("Coverage map source commit mismatch")
        self.test_ids = document["test_ids"]
        self.files = document["files"]
        self.reverse_imports = document["reverse_imports"]
        self.fixtures = document["fixtures"]
        self.source_readers = document["source_readers"]
        self.dialect_tests = document.get("dialect_tests", {})
        self.optimizer_fixture_tests = {
            index
            for path, indexes in self.fixtures.items()
            if path.startswith("tests/fixtures/optimizer/")
            for index in indexes
        }
        self.line_maps = {
            path: {line: indexes for line, indexes in item["lines"]}
            for path, item in self.files.items()
        }
        type_index_path = map_path.parent / "type_index.json.z"
        if type_index_path.exists():
            from .equivalence import TypeIndex

            self.type_index = TypeIndex(type_index_path)
        else:
            self.type_index = None
        self._ast_source_index = None
        covered_ids = {
            document["test_ids"][index]
            for item in self.files.values()
            for index in item["file"]
        }
        self.unmapped_numbers = [test.number for test in tests if test.id not in covered_ids]
        self.special_rules = SpecialRules(self)

    def select_tests(self, changeset: ChangeSet) -> SelectionDecision:
        decision = SelectionDecision(commit_id=changeset.commit_id)
        if changeset.parse_status == "error" or changeset.parse_errors or changeset.parse_warnings:
            return self._full(decision, "parse_uncertainty")
        paths = changeset.get_all_changed_paths()
        if not paths:
            decision.analysis_status = "no_changes"
            return decision

        ast_identical_paths: set[str] = set()
        equivalent_paths: set[str] = set()
        analyses_by_path: dict[str, object] = {}
        if self.source_root is not None and any(path.endswith(".py") for path in paths):
            from .change_analysis import analyze_change
            from .patch_parser import FileOperation, Patch

            patch = Patch(
                commit_id=changeset.commit_id,
                file_changes=[changeset.file_changes[path] for path in sorted(changeset.file_changes)],
                parse_errors=list(changeset.parse_errors),
            )
            analysis = analyze_change(patch, self.source_root)
            if analysis.has_errors():
                return self._full(decision, "change_analysis_uncertainty")
            analyses_by_path = {item.path: item for item in analysis.file_analyses}
            for path, change in changeset.file_changes.items():
                item = analyses_by_path.get(path)
                if (
                    change.operation == FileOperation.MODIFIED
                    and item is not None
                    and item.ast_identical
                ):
                    ast_identical_paths.add(path)
                elif (
                    self.type_index is not None
                    and change.operation == FileOperation.MODIFIED
                    and item is not None
                    and item.pre_source
                    and item.post_source
                ):
                    from .equivalence import prove_equivalent
                    from .equivalence_ast import SourceIndex, provably_equivalent

                    try:
                        if prove_equivalent(
                            path, item.pre_source, item.post_source, self.type_index
                        ):
                            equivalent_paths.add(path)
                    except Exception:
                        pass
                    try:
                        if self._ast_source_index is None:
                            self._ast_source_index = SourceIndex(self.source_root)
                        if provably_equivalent(
                            item.pre_source,
                            item.post_source,
                            path,
                            self._ast_source_index,
                        ):
                            equivalent_paths.add(path)
                    except Exception:
                        pass

        selected: set[int] = set()
        direct_numbers: set[int] = set()
        for path in sorted(paths):
            if path in equivalent_paths:
                self._select_ast_identical_source(path, selected)
            elif path in ast_identical_paths and path in self.files:
                self._select_ast_identical_source(path, selected)
            elif path.startswith("tests/") and path.endswith(".py"):
                direct_numbers.update(self.tests_by_file.get(path, []))
                if path not in self.tests_by_file and path not in self.files:
                    return self._full(decision, "unknown_test_module")
            elif path.endswith(".py"):
                if path not in self.files:
                    return self._full(decision, "unknown_source_file")
                self._select_source(path, changeset, selected, analyses_by_path.get(path))
            else:
                fixture_tests = self._fixture_tests(path)
                if not fixture_tests:
                    return self._full(decision, "unmapped_fixture_or_data")
                selected.update(fixture_tests)

        live_numbers = {
            self.tests_by_id[self.test_ids[index]].number
            for index in selected
            if 0 <= index < len(self.test_ids) and self.test_ids[index] in self.tests_by_id
        }
        live_numbers.update(direct_numbers)
        if live_numbers:
            live_numbers.update(self.unmapped_numbers)
        decision.selected_test_numbers = sorted(live_numbers)
        decision.candidate_test_numbers = list(decision.selected_test_numbers)
        decision.mandatory_test_numbers = list(decision.selected_test_numbers)
        decision.analysis_status = "coverage_hybrid"
        return decision

    def _select_source(self, path: str, changeset: ChangeSet, selected: set[int], analysis=None) -> None:
        if self.special_rules.enabled:
            special = self.special_rules.scope_for(path, changeset, analysis)
            if special is not None:
                selected.update(special)
                return
        item = self.files[path]
        change = changeset.file_changes.get(path)
        lexical_structural = self._structural_change(change)
        structural = lexical_structural
        line_numbers = set(changeset.added_lines.get(path, []))
        line_numbers.update(changeset.removed_lines.get(path, []))
        if not structural:
            structural = any(
                not any(
                    span[4] == "function" and span[1] <= line <= span[3]
                    for span in item["spans"]
                )
                for line in line_numbers
            )

        if structural or path == "sqlglot/serde.py":
            selected.update(item["file"])
        else:
            statement_scope = self._statement_scope(path, changeset, analysis)
            if statement_scope is not None:
                selected.update(statement_scope)
            else:
                local: set[int] = set()
                for line in sorted(line_numbers):
                    local.update(self.line_maps[path].get(line, []))
                    for span in item["spans"]:
                        if span[4] == "function" and span[1] <= line <= span[3]:
                            local.update(item["functions"].get(span[0], []))
                            break
                selected.update(local or item["file"])

        parts = Path(path).parts
        is_optimizer = len(parts) > 1 and parts[0] == "sqlglot" and parts[1] == "optimizer"
        if lexical_structural:
            selected.update(self._importer_coverage(path))
        elif is_optimizer:
            if "sqlglot/planner.py" in self.reverse_imports.get(self._module_name(path), []):
                selected.update(self._importer_coverage("sqlglot/planner.py", max_depth=0))
        if is_optimizer and structural:
            selected.update(self.optimizer_fixture_tests)
        selected.update(self.source_readers.get(path, []))
        if (
            structural
            and len(parts) == 3
            and parts[0] == "sqlglot"
            and parts[1] in {"dialects", "parsers", "generators"}
        ):
            selected.update(self.dialect_tests.get(Path(path).stem, []))

    def _statement_scope(self, path: str, changeset: ChangeSet, analysis=None) -> set[int] | None:
        if analysis is None or getattr(analysis, "pre_ast", None) is None:
            return None
        removed = changeset.removed_lines.get(path, [])
        added = changeset.added_lines.get(path, [])
        if not removed or not added or set(removed) != set(added):
            return None

        from .change_analysis import ASTComparator

        ranges = ASTComparator.get_statement_ranges(analysis.pre_ast)
        if not ranges:
            return None
        line_map = self.line_maps.get(path, {})
        selected: set[int] = set()
        for line in removed:
            span = ASTComparator.innermost_statement_span(ranges, line)
            if span is None:
                return None
            for number in range(span[0], span[1] + 1):
                selected.update(line_map.get(number, []))
        if not selected:
            return None
        return selected

    def _select_ast_identical_source(self, path: str, selected: set[int]) -> None:
        # Reached only for proven no-op changes (AST-identical or provably
        # equivalent). Comment/whitespace-only edits cannot alter runtime
        # behaviour, and the pinned suite's source-reading tests either parse
        # the AST (unchanged) or execute imported objects (unchanged), so no
        # test needs to run.
        return

    def _structural_change(self, change) -> bool:
        if change is None:
            return True
        for hunk in change.hunks:
            for raw_line in hunk.lines:
                if not raw_line.startswith(("+", "-")):
                    continue
                stripped = raw_line[1:].strip()
                if stripped.startswith((
                    "import ", "from ", "def ", "async def ", "class ", "@",
                    "global ", "nonlocal ", "__all__",
                )):
                    return True
                if any(token in stripped for token in (
                    "getattr(", "setattr(", "eval(", "exec(", "importlib",
                    "sys.modules", "__init_subclass__", "__getattr__",
                )):
                    return True
        return False

    def _importer_coverage(self, path: str, max_depth: int = 1) -> set[int]:
        selected: set[int] = set()
        pending = [(path, 0)]
        seen: set[str] = set()
        while pending:
            current, depth = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            module = self._module_name(current)
            for importer in self.reverse_imports.get(module, []):
                if importer in self.files:
                    selected.update(self.files[importer]["file"])
                    if depth < max_depth:
                        pending.append((importer, depth + 1))
        return selected

    @staticmethod
    def _module_name(path: str) -> str:
        if path.endswith("/__init__.py"):
            path = path.removesuffix("/__init__.py")
        else:
            path = path.removesuffix(".py")
        return path.replace("/", ".")

    def _fixture_tests(self, path: str) -> set[int]:
        selected = set(self.fixtures.get(path, []))
        selected.update(self.source_readers.get(path, []))
        parent = Path(path).parent.as_posix()
        while parent not in {"", "."}:
            selected.update(self.fixtures.get(parent, []))
            parent = Path(parent).parent.as_posix()
        return selected

    def _full(self, decision: SelectionDecision, reason: str) -> SelectionDecision:
        decision.uncertainty_level = UncertaintyLevel.U3_STRUCTURAL
        decision.fallback_level = FallbackLevel.FULL
        decision.selected_test_numbers = [test.number for test in self.tests]
        decision.candidate_test_numbers = list(decision.selected_test_numbers)
        decision.mandatory_test_numbers = list(decision.selected_test_numbers)
        decision.analysis_status = reason
        return decision

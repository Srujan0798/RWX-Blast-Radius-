import json
from pathlib import Path
import tempfile
import unittest
import zlib

from src.changeset import ChangeSet
from src.coverage_selector import CoverageSelector
from src.input_validator import TestMetadata
from src.patch_parser import FileChange, FileOperation, Hunk


class CoverageSelectorTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.map_path = Path(self.tempdir.name) / "maps.json.z"
        self.tests = [
            TestMetadata(number=10, id="tests/test_a.py::test_a", file="tests/test_a.py", seconds=1),
            TestMetadata(number=20, id="tests/test_b.py::test_b", file="tests/test_b.py", seconds=1),
            TestMetadata(number=30, id="tests/test_c.py::test_c", file="tests/test_c.py", seconds=1),
        ]
        self.document = {
            "source_commit": "eb11aec4be8cb2122afe713a4816662c3f0fb2fa",
            "test_ids": sorted(test.id for test in self.tests),
            "files": {
                "sqlglot/a.py": {
                    "lines": [[2, [0]]],
                    "spans": [["foo", 1, 2, 3, "function"]],
                    "functions": {"foo": [0]},
                    "file": [0, 1],
                },
                "sqlglot/b.py": {"lines": [], "spans": [], "functions": {}, "file": [1, 2]},
                "sqlglot/parsers/a.py": {"lines": [], "spans": [], "functions": {}, "file": []},
            },
            "reverse_imports": {"sqlglot.a": ["sqlglot/b.py"]},
            "fixtures": {"fixtures/data.sql": [2]},
            "source_readers": {},
            "dialect_tests": {"a": [2]},
        }

    def tearDown(self):
        self.tempdir.cleanup()

    def selector(self, source_root=None):
        self.map_path.write_bytes(zlib.compress(json.dumps(self.document).encode()))
        if source_root is None:
            return CoverageSelector(self.tests, self.map_path)
        return CoverageSelector(self.tests, self.map_path, source_root)

    def comment_only_change(self):
        change = FileChange(
            path="sqlglot/a.py",
            operation=FileOperation.MODIFIED,
            hunks=[Hunk(
                old_start=1,
                old_count=2,
                new_start=1,
                new_count=3,
                lines=[" def foo():", "-    return 1", "+    # explanation", "+    return 1"],
            )],
            added_lines=[2, 3],
            removed_lines=[2],
        )
        return ChangeSet(
            commit_id="comment",
            changed_files=["sqlglot/a.py"],
            file_changes={"sqlglot/a.py": change},
            added_lines={"sqlglot/a.py": [2, 3]},
            removed_lines={"sqlglot/a.py": [2]},
        )

    def source_change(self, lines, hunk_lines):
        change = FileChange(
            path="sqlglot/a.py",
            operation=FileOperation.MODIFIED,
            hunks=[Hunk(old_start=1, old_count=1, new_start=1, new_count=1, lines=hunk_lines)],
        )
        return ChangeSet(
            commit_id="c1",
            changed_files=["sqlglot/a.py"],
            file_changes={"sqlglot/a.py": change},
            added_lines={"sqlglot/a.py": lines},
        )

    def test_function_body_maps_index_to_live_test_number(self):
        decision = self.selector().select_tests(self.source_change([2], ["+    return 2"]))
        self.assertEqual(decision.selected_test_numbers, [10])

    def test_structural_change_includes_importer_coverage(self):
        decision = self.selector().select_tests(self.source_change([1], ["+import os"]))
        self.assertEqual(decision.selected_test_numbers, [10, 20, 30])

    def test_two_hop_importer_coverage(self):
        self.document["files"]["sqlglot/b.py"]["file"] = [1]
        self.document["files"]["sqlglot/c.py"] = {"lines": [], "spans": [], "functions": {}, "file": [2]}
        self.document["reverse_imports"]["sqlglot.b"] = ["sqlglot/c.py"]
        decision = self.selector().select_tests(self.source_change([1], ["+import os"]))
        self.assertEqual(decision.selected_test_numbers, [10, 20, 30])

    def test_optimizer_source_uses_coverage_driven_tests(self):
        optimizer_path = "sqlglot/optimizer/a.py"
        self.document["files"][optimizer_path] = self.document["files"]["sqlglot/a.py"]
        self.document["fixtures"]["tests/fixtures/optimizer/a.sql"] = [2]
        change = FileChange(path=optimizer_path, operation=FileOperation.MODIFIED)
        changeset = ChangeSet(
            commit_id="c1",
            changed_files=[optimizer_path],
            file_changes={optimizer_path: change},
            added_lines={optimizer_path: [2]},
        )
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [10])

    def test_optimizer_body_uses_coverage_not_fixture_consumers(self):
        self.tests.extend([
            TestMetadata(number=40, id="tests/test_d.py::test_d", file="tests/test_d.py", seconds=1),
            TestMetadata(number=50, id="tests/test_e.py::test_e", file="tests/test_e.py", seconds=1),
        ])
        self.document["test_ids"] = sorted(test.id for test in self.tests)
        optimizer_path = "sqlglot/optimizer/a.py"
        self.document["files"][optimizer_path] = {
            "lines": [],
            "spans": [["foo", 1, 2, 3, "function"]],
            "functions": {"foo": [0]},
            "file": [4],
        }
        self.document["fixtures"]["tests/fixtures/optimizer/a.sql"] = [2]
        self.document["fixtures"]["tests/fixtures/optimizer/a_extra.sql"] = [1]
        self.document["fixtures"]["tests/fixtures/optimizer/optimizer.sql"] = [0]
        self.document["fixtures"]["tests/fixtures/optimizer/tpc-ds/tpc-ds.sql"] = [3]
        self.document["fixtures"]["tests/fixtures/optimizer/other.sql"] = [4]
        self.document["files"]["sqlglot/d.py"] = {"lines": [], "spans": [], "functions": {}, "file": [3]}
        change = FileChange(path=optimizer_path, operation=FileOperation.MODIFIED)
        changeset = ChangeSet(
            commit_id="c1",
            changed_files=[optimizer_path],
            file_changes={optimizer_path: change},
            added_lines={optimizer_path: [2]},
        )
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [10])

    def test_optimizer_body_without_coverage_selects_nothing(self):
        optimizer_path = "sqlglot/optimizer/helpers.py"
        self.document["files"][optimizer_path] = {
            "lines": [],
            "spans": [["foo", 1, 2, 3, "function"]],
            "functions": {"foo": []},
            "file": [],
        }
        self.document["fixtures"] = {
            "tests/fixtures/optimizer/optimizer.sql": [0],
            "tests/fixtures/optimizer/b.sql": [1],
            "tests/fixtures/optimizer/tpc-ds/tpc-ds.sql": [2],
        }
        change = FileChange(path=optimizer_path, operation=FileOperation.MODIFIED)
        changeset = ChangeSet(
            commit_id="c1",
            changed_files=[optimizer_path],
            file_changes={optimizer_path: change},
            added_lines={optimizer_path: [2]},
        )
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [])

    def test_optimizer_structural_change_uses_all_optimizer_fixtures(self):
        optimizer_path = "sqlglot/optimizer/a.py"
        self.document["files"][optimizer_path] = {
            "lines": [],
            "spans": [["foo", 1, 2, 3, "function"]],
            "functions": {"foo": []},
            "file": [0],
        }
        self.document["fixtures"]["tests/fixtures/optimizer/a.sql"] = [2]
        self.document["fixtures"]["tests/fixtures/optimizer/b.sql"] = [1]
        self.document["fixtures"]["tests/fixtures/optimizer/optimizer.sql"] = [0]
        change = FileChange(
            path=optimizer_path,
            operation=FileOperation.MODIFIED,
            hunks=[Hunk(
                old_start=1,
                old_count=0,
                new_start=1,
                new_count=1,
                lines=["+import os"],
            )],
        )
        changeset = ChangeSet(
            commit_id="c1",
            changed_files=[optimizer_path],
            file_changes={optimizer_path: change},
            added_lines={optimizer_path: [1]},
        )
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [10, 20, 30])

    def test_optimizer_body_uses_planner_edge_but_not_other_second_hops(self):
        optimizer_path = "sqlglot/optimizer/a.py"
        self.document["files"][optimizer_path] = self.document["files"]["sqlglot/a.py"]
        for path in ["sqlglot/planner.py", "sqlglot/optimizer/optimizer.py", "sqlglot/c.py"]:
            self.document["files"][path] = {"lines": [], "spans": [], "functions": {}, "file": []}
        self.document["files"]["sqlglot/b.py"]["file"] = [1]
        self.document["files"]["sqlglot/c.py"]["file"] = [2]
        self.document["reverse_imports"] = {
            "sqlglot.optimizer.a": ["sqlglot/planner.py", "sqlglot/optimizer/optimizer.py"],
            "sqlglot.planner": ["sqlglot/b.py"],
            "sqlglot.optimizer.optimizer": ["sqlglot/c.py"],
        }
        change = FileChange(path=optimizer_path, operation=FileOperation.MODIFIED)
        changeset = ChangeSet(
            commit_id="c1",
            changed_files=[optimizer_path],
            file_changes={optimizer_path: change},
            added_lines={optimizer_path: [2]},
        )
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [10, 20])

    def test_typing_source_is_coverage_driven(self):
        typing_path = "sqlglot/typing/a.py"
        self.document["files"][typing_path] = self.document["files"]["sqlglot/a.py"]
        self.document["fixtures"]["tests/fixtures/optimizer/a.sql"] = [2]
        change = FileChange(path=typing_path, operation=FileOperation.MODIFIED)
        changeset = ChangeSet(
            commit_id="c1",
            changed_files=[typing_path],
            file_changes={typing_path: change},
            added_lines={typing_path: [2]},
        )
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [10])

    def test_module_assignment_includes_importer_coverage(self):
        decision = self.selector().select_tests(self.source_change([5], ["+VALUE = 2"]))
        self.assertEqual(decision.selected_test_numbers, [10, 20])

    def test_fixture_uses_live_test_number(self):
        changeset = ChangeSet(commit_id="c1", changed_files=["fixtures/data.sql"])
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [30])

    def test_unknown_file_falls_back_to_full_suite(self):
        changeset = ChangeSet(commit_id="c1", changed_files=["sqlglot/unknown.py"])
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [10, 20, 30])

    def test_empty_change_selects_nothing(self):
        decision = self.selector().select_tests(ChangeSet(commit_id="c1"))
        self.assertEqual(decision.selected_test_numbers, [])

    def test_parse_error_falls_back_to_full_suite(self):
        changeset = ChangeSet(
            commit_id="bad",
            parse_status="error",
            parse_errors=["nonempty patch contains no file changes"],
        )
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [10, 20, 30])
        self.assertEqual(decision.analysis_status, "parse_uncertainty")

    def test_ast_identical_source_change_selects_nothing(self):
        source_root = Path(self.tempdir.name) / "source"
        source_file = source_root / "sqlglot/a.py"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("def foo():\n    return 1\n")
        decision = self.selector(source_root).select_tests(self.comment_only_change())
        self.assertEqual(decision.selected_test_numbers, [])

    def test_ast_identical_source_change_drops_source_readers(self):
        self.document["source_readers"] = {"sqlglot/a.py": [1]}
        source_root = Path(self.tempdir.name) / "source"
        source_file = source_root / "sqlglot/a.py"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("def foo():\n    return 1\n")
        decision = self.selector(source_root).select_tests(self.comment_only_change())
        self.assertEqual(decision.selected_test_numbers, [])

    def test_ast_identical_optimizer_change_skips_path_based_tests(self):
        optimizer_path = "sqlglot/optimizer/a.py"
        self.document["files"][optimizer_path] = self.document["files"]["sqlglot/a.py"]
        self.document["reverse_imports"]["sqlglot.optimizer.a"] = ["sqlglot/b.py"]
        self.document["fixtures"]["tests/fixtures/optimizer/a.sql"] = [2]
        source_root = Path(self.tempdir.name) / "source"
        source_file = source_root / optimizer_path
        source_file.parent.mkdir(parents=True)
        source_file.write_text("def foo():\n    return 1\n")
        changeset = self.comment_only_change()
        change = changeset.file_changes.pop("sqlglot/a.py")
        change.path = optimizer_path
        changeset.file_changes[optimizer_path] = change
        changeset.changed_files = [optimizer_path]
        decision = self.selector(source_root).select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [])

    def test_ast_identical_dialect_change_skips_path_based_tests(self):
        generator_path = "sqlglot/generators/a.py"
        self.document["files"][generator_path] = self.document["files"]["sqlglot/a.py"]
        source_root = Path(self.tempdir.name) / "source"
        source_file = source_root / generator_path
        source_file.parent.mkdir(parents=True)
        source_file.write_text("def foo():\n    return 1\n")
        changeset = self.comment_only_change()
        change = changeset.file_changes.pop("sqlglot/a.py")
        change.path = generator_path
        changeset.file_changes[generator_path] = change
        changeset.changed_files = [generator_path]
        decision = self.selector(source_root).select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [])

    def test_change_analysis_error_falls_back_to_full_suite(self):
        source_root = Path(self.tempdir.name) / "source"
        source_root.mkdir()
        decision = self.selector(source_root).select_tests(self.comment_only_change())
        self.assertEqual(decision.selected_test_numbers, [10, 20, 30])
        self.assertEqual(decision.analysis_status, "change_analysis_uncertainty")

    def test_structural_dialect_change_includes_dialect_literal_tests(self):
        change = FileChange(
            path="sqlglot/parsers/a.py",
            operation=FileOperation.MODIFIED,
            hunks=[Hunk(
                old_start=1,
                old_count=1,
                new_start=1,
                new_count=2,
                lines=["+import os", "+VALUE = 2"],
            )],
        )
        changeset = ChangeSet(
            commit_id="c1",
            changed_files=["sqlglot/parsers/a.py"],
            file_changes={"sqlglot/parsers/a.py": change},
            added_lines={"sqlglot/parsers/a.py": [1, 2]},
        )
        decision = self.selector().select_tests(changeset)
        self.assertIn(30, decision.selected_test_numbers)

    def test_changed_test_file_uses_live_catalog(self):
        changeset = ChangeSet(commit_id="c1", changed_files=["tests/test_b.py"])
        decision = self.selector().select_tests(changeset)
        self.assertEqual(decision.selected_test_numbers, [20])


if __name__ == "__main__":
    unittest.main()

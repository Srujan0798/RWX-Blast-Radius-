"""Tests for change_analysis module."""

import ast
import tempfile
import unittest
from pathlib import Path

from src.patch_parser import PatchParser, FileChange, FileOperation, Hunk, Patch
from src.change_analysis import (
    SourceApplicator,
    ASTComparator,
    FileAnalysis,
    ChangeAnalysis,
    analyze_change,
    ApplyStatus,
    FunctionChange,
)


class TestSourceApplicator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.source_root = Path(self.temp_dir.name)
        self.applicator = SourceApplicator(self.source_root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_file(self, path: str, content: str) -> Path:
        file_path = self.source_root / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_read_file_exists(self):
        self.write_file("foo.py", "def bar():\n    return 1\n")
        content = self.applicator.read_file("foo.py")
        self.assertEqual(content, "def bar():\n    return 1\n")

    def test_read_file_not_exists(self):
        content = self.applicator.read_file("nonexistent.py")
        self.assertIsNone(content)

    def test_validate_hunk_success(self):
        source = "def foo():\n    return 1\n"
        source_lines = source.splitlines(keepends=True)
        hunk = Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" def foo():", "     return 1"])
        errors = self.applicator.validate_hunk(hunk, source_lines)
        self.assertEqual(errors, [])

    def test_validate_hunk_context_mismatch(self):
        source = "def foo():\n    return 1\n"
        source_lines = source.splitlines(keepends=True)
        hunk = Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" def foo():", "     return 2"])
        errors = self.applicator.validate_hunk(hunk, source_lines)
        self.assertTrue(any("mismatch" in e for e in errors))

    def test_validate_hunk_out_of_bounds(self):
        source = "def foo():\n    return 1\n"
        source_lines = source.splitlines(keepends=True)
        hunk = Hunk(old_start=5, old_count=2, new_start=5, new_count=2, lines=[" def bar():", "     return 3"])
        errors = self.applicator.validate_hunk(hunk, source_lines)
        self.assertTrue(any("out of bounds" in e for e in errors))

    def test_apply_hunks_modification(self):
        source = "def foo():\n    return 1\n"
        hunk = Hunk(old_start=2, old_count=1, new_start=2, new_count=1, lines=["-    return 1", "+    return 2"])
        result, errors = self.applicator.apply_hunks(source, [hunk])
        self.assertEqual(errors, [])
        self.assertEqual(result, "def foo():\n    return 2\n")

    def test_apply_hunks_addition(self):
        source = "def foo():\n    return 1\n"
        hunk = Hunk(old_start=1, old_count=0, new_start=2, new_count=1, lines=["+    x = 5"])
        result, errors = self.applicator.apply_hunks(source, [hunk])
        self.assertEqual(errors, [])
        self.assertEqual(result, "def foo():\n    x = 5\n    return 1\n")

    def test_apply_hunks_deletion(self):
        source = "def foo():\n    x = 5\n    return 1\n"
        hunk = Hunk(old_start=2, old_count=1, new_start=2, new_count=0, lines=["-    x = 5"])
        result, errors = self.applicator.apply_hunks(source, [hunk])
        self.assertEqual(errors, [])
        self.assertEqual(result, "def foo():\n    return 1\n")

    def test_apply_hunks_multiple(self):
        source = "def foo():\n    a = 1\n    b = 2\n    return a + b\n"
        hunks = [
            Hunk(old_start=2, old_count=1, new_start=2, new_count=1, lines=["-    a = 1", "+    a = 10"]),
            Hunk(old_start=3, old_count=1, new_start=3, new_count=1, lines=["-    b = 2", "+    b = 20"]),
        ]
        result, errors = self.applicator.apply_hunks(source, hunks)
        self.assertEqual(errors, [])
        self.assertEqual(result, "def foo():\n    a = 10\n    b = 20\n    return a + b\n")

    def test_apply_hunks_multiple_with_shifted_coordinates(self):
        source = "def foo():\n    a = 1\n    b = 2\n    c = 3\n    return a + b + c\n"
        hunks = [
            Hunk(old_start=1, old_count=1, new_start=1, new_count=2, lines=[" def foo():", "+    inserted = 0"]),
            Hunk(old_start=4, old_count=1, new_start=5, new_count=1, lines=["-    c = 3", "+    c = 30"]),
        ]
        result, errors = self.applicator.apply_hunks(source, hunks)
        self.assertEqual(errors, [])
        self.assertEqual(result, "def foo():\n    inserted = 0\n    a = 1\n    b = 2\n    c = 30\n    return a + b + c\n")

    def test_apply_hunks_rejects_count_mismatch(self):
        source = "def foo():\n    return 1\n"
        hunk = Hunk(old_start=1, old_count=2, new_start=1, new_count=3, lines=[" def foo():", "-    return 1", "+    return 2"])
        result, errors = self.applicator.apply_hunks(source, [hunk])
        self.assertEqual(result, source)
        self.assertTrue(any("new_count mismatch" in error for error in errors))

    def test_apply_hunks_rejects_overlapping_hunks(self):
        source = "a = 1\nb = 2\nc = 3\n"
        hunks = [
            Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" a = 1", "-b = 2", "+b = 20"]),
            Hunk(old_start=2, old_count=1, new_start=2, new_count=1, lines=["-b = 2", "+b = 200"]),
        ]
        result, errors = self.applicator.apply_hunks(source, hunks)
        self.assertEqual(result, source)
        self.assertTrue(any("nonoverlapping" in error for error in errors))

    def test_apply_hunks_preserves_no_newline_marker(self):
        source = "def foo():\n    return 1"
        hunk = Hunk(
            old_start=2,
            old_count=1,
            new_start=2,
            new_count=1,
            lines=["-    return 1", "\\ No newline at end of file", "+    return 2", "\\ No newline at end of file"],
        )
        result, errors = self.applicator.apply_hunks(source, [hunk])
        self.assertEqual(errors, [])
        self.assertEqual(result, "def foo():\n    return 2")

    def test_apply_hunks_error_recovery(self):
        source = "def foo():\n    return 1\n"
        hunk = Hunk(old_start=5, old_count=1, new_start=5, new_count=1, lines=["     return 2"])
        result, errors = self.applicator.apply_hunks(source, [hunk])
        self.assertTrue(any("out of bounds" in e for e in errors))
        self.assertEqual(result, source)


class TestASTComparator(unittest.TestCase):
    def test_get_function_qualnames_simple(self):
        source = "def foo():\n    return 1\n"
        tree = ast.parse(source)
        qualnames = ASTComparator.get_function_qualnames(tree, "test")
        self.assertEqual(qualnames, {"test.foo": (1, 2)})

    def test_get_function_qualnames_class(self):
        source = "class Bar:\n    def baz(self):\n        return 2\n"
        tree = ast.parse(source)
        qualnames = ASTComparator.get_function_qualnames(tree, "test")
        self.assertEqual(qualnames, {"test.Bar.baz": (2, 3)})

    def test_get_function_qualnames_async(self):
        source = "async def foo():\n    return 1\n"
        tree = ast.parse(source)
        qualnames = ASTComparator.get_function_qualnames(tree, "test")
        self.assertEqual(qualnames, {"test.foo": (1, 2)})

    def test_get_module_level_nodes(self):
        source = "import os\n\ndef foo():\n    return 1\n"
        tree = ast.parse(source)
        nodes = ASTComparator.get_module_level_nodes(tree)
        self.assertTrue(any(n[0] == "Import" for n in nodes))
        self.assertTrue(any(n[0] == "FunctionDef" for n in nodes))

    def test_compare_functions_added(self):
        pre = {}
        post = {"test.foo": (1, 2)}
        changes = ASTComparator.compare_functions(pre, post, "", "def foo():\n    return 1\n", [1, 2], [])
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].qualname, "test.foo")
        self.assertEqual(changes[0].change_type, "added")

    def test_compare_functions_removed(self):
        pre = {"test.foo": (1, 2)}
        post = {}
        changes = ASTComparator.compare_functions(pre, post, "def foo():\n    return 1\n", "", [], [1, 2])
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].qualname, "test.foo")
        self.assertEqual(changes[0].change_type, "removed")

    def test_compare_functions_modified(self):
        pre = {"test.foo": (1, 2)}
        post = {"test.foo": (1, 3)}
        changes = ASTComparator.compare_functions(pre, post, "def foo():\n    return 1\n", "def foo():\n    x = 1\n    return 1\n", [2], [])
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].qualname, "test.foo")
        self.assertEqual(changes[0].change_type, "modified")

    def test_compare_functions_unchanged_after_line_shift(self):
        pre = {"test.foo": (2, 3)}
        post = {"test.foo": (4, 5)}
        changes = ASTComparator.compare_functions(
            pre,
            post,
            "import os\ndef foo():\n    return 1\n",
            "import os\nimport sys\n\ndef foo():\n    return 1\n",
            [2],
            [],
        )
        self.assertEqual(changes, [])

    def test_compare_functions_added_lines_use_post_ranges(self):
        pre = {"test.foo": (1, 2), "test.bar": (4, 5)}
        post = {"test.foo": (1, 4), "test.bar": (6, 7)}
        changes = ASTComparator.compare_functions(pre, post, "", "", [2, 3], [])
        self.assertEqual([change.qualname for change in changes], ["test.foo"])
        self.assertEqual(changes[0].added_lines, [2, 3])

    def test_compare_module_level_true(self):
        pre = [("FunctionDef", 1, 2)]
        post = [("FunctionDef", 1, 3)]
        self.assertTrue(ASTComparator.compare_module_level(pre, post))

    def test_compare_module_level_false(self):
        pre = [("FunctionDef", 1, 2)]
        post = [("FunctionDef", 1, 2)]
        self.assertFalse(ASTComparator.compare_module_level(pre, post))

    def test_asts_identical_true(self):
        tree1 = ast.parse("def foo():\n    return 1\n")
        tree2 = ast.parse("def foo():\n    return 1\n")
        self.assertTrue(ASTComparator.asts_identical(tree1, tree2))

    def test_asts_identical_false(self):
        tree1 = ast.parse("def foo():\n    return 1\n")
        tree2 = ast.parse("def foo():\n    return 2\n")
        self.assertFalse(ASTComparator.asts_identical(tree1, tree2))


class TestAnalyzeChange(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.source_root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_file(self, path: str, content: str) -> Path:
        file_path = self.source_root / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def make_patch(self, commit_id: str, file_changes: list[FileChange]) -> Patch:
        return Patch(commit_id=commit_id, file_changes=file_changes)

    def test_analyze_modified_file(self):
        self.write_file("foo.py", "def bar():\n    return 1\n")
        fc = FileChange(
            path="foo.py",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" def bar():", "-    return 1", "+    return 2"])
            ],
            added_lines=[2],
            removed_lines=[2],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        self.assertEqual(len(analysis.file_analyses), 1)
        fa = analysis.file_analyses[0]
        self.assertEqual(fa.path, "foo.py")
        self.assertEqual(fa.operation, FileOperation.MODIFIED)
        self.assertEqual(fa.apply_status, ApplyStatus.OK)
        self.assertIn("return 2", fa.post_source or "")
        self.assertEqual(len(fa.changed_functions), 1)
        self.assertEqual(fa.changed_functions[0].qualname, "foo.bar")
        self.assertEqual(fa.changed_functions[0].change_type, "modified")

    def test_analyze_added_file(self):
        fc = FileChange(
            path="new.py",
            operation=FileOperation.ADDED,
            hunks=[
                Hunk(old_start=0, old_count=0, new_start=1, new_count=2, lines=["+def foo():", "+    return 1"])
            ],
            added_lines=[1, 2],
            removed_lines=[],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        self.assertEqual(len(analysis.file_analyses), 1)
        fa = analysis.file_analyses[0]
        self.assertEqual(fa.path, "new.py")
        self.assertEqual(fa.operation, FileOperation.ADDED)
        self.assertEqual(fa.apply_status, ApplyStatus.OK)
        self.assertIn("def foo():", fa.post_source or "")
        self.assertEqual(len(fa.changed_functions), 1)
        self.assertEqual(fa.changed_functions[0].qualname, "new.foo")
        self.assertEqual(fa.changed_functions[0].change_type, "added")

    def test_analyze_deleted_file(self):
        self.write_file("old.py", "def foo():\n    return 1\n")
        fc = FileChange(
            path="old.py",
            operation=FileOperation.DELETED,
            hunks=[
                Hunk(old_start=1, old_count=2, new_start=1, new_count=0, lines=["-def foo():", "-    return 1"])
            ],
            added_lines=[],
            removed_lines=[1, 2],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        self.assertEqual(len(analysis.file_analyses), 1)
        fa = analysis.file_analyses[0]
        self.assertEqual(fa.path, "old.py")
        self.assertEqual(fa.operation, FileOperation.DELETED)
        self.assertEqual(fa.apply_status, ApplyStatus.OK)
        self.assertEqual(fa.post_source, "")
        self.assertEqual(len(fa.changed_functions), 1)
        self.assertEqual(fa.changed_functions[0].qualname, "old.foo")
        self.assertEqual(fa.changed_functions[0].change_type, "removed")

    def test_analyze_renamed_file(self):
        self.write_file("old.py", "def foo():\n    return 1\n")
        fc = FileChange(
            path="new.py",
            operation=FileOperation.RENAMED,
            old_path="old.py",
            hunks=[
                Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" def foo():", "-    return 1", "+    return 2"])
            ],
            added_lines=[2],
            removed_lines=[2],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        self.assertEqual(len(analysis.file_analyses), 1)
        fa = analysis.file_analyses[0]
        self.assertEqual(fa.path, "new.py")
        self.assertEqual(fa.operation, FileOperation.RENAMED)
        self.assertEqual(fa.old_path, "old.py")
        self.assertEqual(fa.apply_status, ApplyStatus.OK)
        self.assertIn("return 2", fa.post_source or "")
        self.assertEqual(fa.changed_functions[0].qualname, "new.foo")

    def test_analyze_missing_source_file(self):
        fc = FileChange(
            path="missing.py",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=1, new_start=1, new_count=1, lines=[" def foo():"])
            ],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        self.assertEqual(len(analysis.file_analyses), 1)
        fa = analysis.file_analyses[0]
        self.assertEqual(fa.apply_status, ApplyStatus.ERROR)
        self.assertTrue(any("not found" in e for e in fa.apply_errors))

    def test_analyze_hunk_context_mismatch(self):
        self.write_file("foo.py", "def bar():\n    return 1\n")
        fc = FileChange(
            path="foo.py",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" def bar():", "-    return 1", "+    return 999"])
            ],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        fa = analysis.file_analyses[0]
        self.assertEqual(fa.apply_status, ApplyStatus.OK)
        self.assertIn("return 999", fa.post_source or "")

    def test_analyze_syntax_error_in_post(self):
        self.write_file("foo.py", "def bar():\n    return 1\n")
        fc = FileChange(
            path="foo.py",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" def bar():", "-    return 1", "+    return ("])
            ],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        fa = analysis.file_analyses[0]
        self.assertTrue(any("parse error" in e for e in fa.parse_errors))

    def test_analyze_hunk_context_mismatch_explicit(self):
        self.write_file("foo.py", "def bar():\n    return 1\n")
        fc = FileChange(
            path="foo.py",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" def bar():", "     return 999"])
            ],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        fa = analysis.file_analyses[0]
        self.assertEqual(fa.apply_status, ApplyStatus.ERROR)
        self.assertTrue(any("mismatch" in e for e in fa.apply_errors))

    def test_analyze_ast_identical_noop(self):
        self.write_file("foo.py", "def bar():\n    return 1\n")
        fc = FileChange(
            path="foo.py",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=2, new_start=1, new_count=2, lines=[" def bar():", "     return 1"])
            ],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        fa = analysis.file_analyses[0]
        self.assertTrue(fa.ast_identical)
        self.assertFalse(fa.structural_changes)

    def test_analyze_structural_changes(self):
        self.write_file("foo.py", "def bar():\n    return 1\n")
        fc = FileChange(
            path="foo.py",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=2, new_start=1, new_count=3, lines=[" def bar():", "     x = 1", "+    x = 1", "     return 1"])
            ],
            added_lines=[2],
            removed_lines=[],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        fa = analysis.file_analyses[0]
        self.assertFalse(fa.ast_identical)
        self.assertTrue(fa.structural_changes)

    def test_analyze_module_level_changes(self):
        self.write_file("foo.py", "import os\n\ndef bar():\n    return 1\n")
        fc = FileChange(
            path="foo.py",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=1, new_start=1, new_count=2, lines=[" import os", "+import sys"])
            ],
            added_lines=[2],
            removed_lines=[],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        fa = analysis.file_analyses[0]
        self.assertTrue(fa.module_level_changes)

    def test_analyze_non_python_file_skipped(self):
        fc = FileChange(
            path="foo.txt",
            operation=FileOperation.MODIFIED,
            hunks=[
                Hunk(old_start=1, old_count=1, new_start=1, new_count=1, lines=[" hello"])
            ],
        )
        patch = self.make_patch("c1", [fc])
        analysis = analyze_change(patch, self.source_root)

        self.assertEqual(len(analysis.file_analyses), 0)

    def test_analyze_multiple_files(self):
        self.write_file("a.py", "def a():\n    return 1\n")
        self.write_file("b.py", "def b():\n    return 2\n")
        fcs = [
            FileChange(path="a.py", operation=FileOperation.MODIFIED, hunks=[Hunk(old_start=2, old_count=1, new_start=2, new_count=1, lines=["-    return 1", "+    return 10"])]),
            FileChange(path="b.py", operation=FileOperation.MODIFIED, hunks=[Hunk(old_start=2, old_count=1, new_start=2, new_count=1, lines=["-    return 2", "+    return 20"])]),
        ]
        patch = self.make_patch("c1", fcs)
        analysis = analyze_change(patch, self.source_root)

        self.assertEqual(len(analysis.file_analyses), 2)
        self.assertEqual(analysis.file_analyses[0].path, "a.py")
        self.assertEqual(analysis.file_analyses[1].path, "b.py")

    def test_analyze_parse_errors_from_patch(self):
        fc = FileChange(
            path="foo.py",
            operation=FileOperation.MODIFIED,
            hunks=[],
            parse_warnings=["malformed hunk at line 5"],
        )
        patch = Patch(commit_id="c1", file_changes=[fc], parse_errors=["missing header"])
        analysis = analyze_change(patch, self.source_root)

        self.assertTrue(any("missing header" in e for e in analysis.parse_errors))


class TestFileAnalysisDataclass(unittest.TestCase):
    def test_defaults(self):
        fa = FileAnalysis(path="test.py", operation=FileOperation.MODIFIED)
        self.assertEqual(fa.path, "test.py")
        self.assertEqual(fa.operation, FileOperation.MODIFIED)
        self.assertIsNone(fa.old_path)
        self.assertIsNone(fa.pre_source)
        self.assertIsNone(fa.post_source)
        self.assertIsNone(fa.pre_ast)
        self.assertIsNone(fa.post_ast)
        self.assertEqual(fa.parse_errors, [])
        self.assertEqual(fa.apply_errors, [])
        self.assertEqual(fa.apply_status, ApplyStatus.OK)
        self.assertEqual(fa.changed_functions, [])
        self.assertFalse(fa.module_level_changes)
        self.assertFalse(fa.structural_changes)
        self.assertFalse(fa.ast_identical)


class TestChangeAnalysisDataclass(unittest.TestCase):
    def test_defaults(self):
        ca = ChangeAnalysis(commit_id="c1")
        self.assertEqual(ca.commit_id, "c1")
        self.assertEqual(ca.file_analyses, [])
        self.assertEqual(ca.parse_errors, [])
        self.assertEqual(ca.apply_errors, [])

    def test_get_python_analyses(self):
        fa1 = FileAnalysis(path="a.py", operation=FileOperation.MODIFIED)
        fa2 = FileAnalysis(path="b.txt", operation=FileOperation.MODIFIED)
        ca = ChangeAnalysis(commit_id="c1", file_analyses=[fa1, fa2])
        python_analyses = ca.get_python_analyses()
        self.assertEqual(len(python_analyses), 1)
        self.assertEqual(python_analyses[0].path, "a.py")

    def test_has_errors(self):
        ca = ChangeAnalysis(commit_id="c1")
        self.assertFalse(ca.has_errors())

        ca.parse_errors.append("error")
        self.assertTrue(ca.has_errors())

        ca2 = ChangeAnalysis(commit_id="c2", file_analyses=[FileAnalysis(path="a.py", operation=FileOperation.MODIFIED, apply_status=ApplyStatus.ERROR)])
        self.assertTrue(ca2.has_errors())


if __name__ == "__main__":
    unittest.main()
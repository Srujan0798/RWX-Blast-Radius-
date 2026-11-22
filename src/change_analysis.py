"""MODULE D — Source Change Analysis

Strict unified-diff post-image applicator. Reconstructs modified Python files
from FileChange hunks, validates hunk line counts and old context, parses
pre/post AST, and reports structural changes.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from enum import Enum

from .patch_parser import Patch, FileChange, FileOperation, Hunk
from .changeset import ChangeSet


class ApplyStatus(Enum):
    OK = "ok"
    ERROR = "error"


@dataclass
class FunctionChange:
    qualname: str
    change_type: str
    added_lines: list[int] = field(default_factory=list)
    removed_lines: list[int] = field(default_factory=list)


@dataclass
class FileAnalysis:
    path: str
    operation: FileOperation
    old_path: str | None = None
    pre_source: str | None = None
    post_source: str | None = None
    pre_ast: ast.AST | None = None
    post_ast: ast.AST | None = None
    parse_errors: list[str] = field(default_factory=list)
    apply_errors: list[str] = field(default_factory=list)
    apply_status: ApplyStatus = ApplyStatus.OK
    changed_functions: list[FunctionChange] = field(default_factory=list)
    module_level_changes: bool = False
    structural_changes: bool = False
    ast_identical: bool = False


@dataclass
class ChangeAnalysis:
    commit_id: str
    file_analyses: list[FileAnalysis] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)
    apply_errors: list[str] = field(default_factory=list)

    def get_python_analyses(self) -> list[FileAnalysis]:
        return [fa for fa in self.file_analyses if fa.path.endswith(".py")]

    def has_errors(self) -> bool:
        return bool(
            self.parse_errors
            or self.apply_errors
            or any(
                fa.apply_status == ApplyStatus.ERROR or fa.parse_errors or fa.apply_errors
                for fa in self.file_analyses
            )
        )


class SourceApplicator:
    def __init__(self, source_root: Path):
        self.source_root = source_root

    def read_file(self, path: str) -> str | None:
        file_path = self.source_root / path
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return None

    @staticmethod
    def _old_index(hunk: Hunk) -> int:
        return hunk.old_start if hunk.old_count == 0 else hunk.old_start - 1

    @staticmethod
    def _new_index(hunk: Hunk) -> int:
        return hunk.new_start if hunk.new_count == 0 else hunk.new_start - 1

    @staticmethod
    def _content(line: str) -> str:
        return line.rstrip("\r\n")

    def validate_hunk(self, hunk: Hunk, source_lines: list[str]) -> list[str]:
        errors = []
        old_start = self._old_index(hunk)
        old_end = old_start + hunk.old_count
        if hunk.old_start < 0 or hunk.new_start < 0 or hunk.old_count < 0 or hunk.new_count < 0:
            return ["Hunk coordinates and counts must be nonnegative"]
        if old_start < 0 or old_start > len(source_lines):
            return [f"Hunk old_start {hunk.old_start} out of bounds (file has {len(source_lines)} lines)"]
        if old_end > len(source_lines):
            return [f"Hunk old_count {hunk.old_count} exceeds file length (start={hunk.old_start}, file has {len(source_lines)} lines)"]

        actual_context = []
        old_count = 0
        new_count = 0
        previous = None
        old_no_newline = []
        new_no_newline = []
        for raw_line in hunk.lines:
            if raw_line.startswith("\\ No newline at end of file"):
                if previous is None:
                    errors.append("No-newline marker without a preceding diff line")
                    continue
                prefix, _, _ = previous
                if prefix in {"-", " "}:
                    old_no_newline.append(len(actual_context) - 1)
                if prefix in {"+", " "}:
                    new_no_newline.append(new_count - 1)
                continue
            if not raw_line.startswith((" ", "-", "+")):
                errors.append(f"Invalid hunk line: {raw_line[:50]!r}")
                continue
            prefix = raw_line[0]
            content = self._content(raw_line[1:])
            previous = (prefix, content, raw_line)
            if prefix in {" ", "-"}:
                actual_context.append(content)
                old_count += 1
            if prefix in {" ", "+"}:
                new_count += 1

        if old_count != hunk.old_count:
            errors.append(f"Hunk old_count mismatch: header={hunk.old_count}, actual={old_count}")
        if new_count != hunk.new_count:
            errors.append(f"Hunk new_count mismatch: header={hunk.new_count}, actual={new_count}")

        expected_context = [self._content(line) for line in source_lines[old_start:old_end]]
        if expected_context != actual_context:
            for i, (exp, act) in enumerate(zip(expected_context, actual_context)):
                if exp != act:
                    errors.append(f"Hunk context mismatch at line {old_start + i + 1}: expected {exp!r}, got {act!r}")
                    break
            if len(expected_context) != len(actual_context) and not any("context mismatch" in error for error in errors):
                errors.append(f"Hunk context length mismatch: expected {len(expected_context)} lines, got {len(actual_context)}")
        elif old_count == hunk.old_count:
            for index, source_line in enumerate(source_lines[old_start:old_end]):
                has_newline = source_line.endswith(("\n", "\r"))
                if has_newline == (index in old_no_newline):
                    errors.append(f"Hunk newline mismatch at source line {old_start + index + 1}")
                    break
        if set(old_no_newline) - set(range(old_count)) or set(new_no_newline) - set(range(new_count)):
            errors.append("No-newline marker refers to an unavailable line")
        return errors

    def apply_hunks(self, source: str, hunks: list[Hunk]) -> tuple[str, list[str]]:
        source_lines = source.splitlines(keepends=True)
        errors = []
        previous_old_end = 0
        previous_new_end = 0
        for hunk in hunks:
            errors.extend(self.validate_hunk(hunk, source_lines))
            old_start = self._old_index(hunk)
            new_start = self._new_index(hunk)
            if old_start < previous_old_end or new_start < previous_new_end:
                errors.append("Hunks must be ordered and nonoverlapping")
            previous_old_end = old_start + hunk.old_count
            previous_new_end = new_start + hunk.new_count
        if errors:
            return source, errors

        result = []
        cursor = 0
        for hunk in hunks:
            old_start = self._old_index(hunk)
            old_end = old_start + hunk.old_count
            result.extend(source_lines[cursor:old_start])
            old_offset = 0
            new_lines = []
            previous = None
            for raw_line in hunk.lines:
                if raw_line.startswith("\\ No newline at end of file"):
                    if previous is not None and previous[0] in {"+", " "}:
                        new_lines[-1] = self._content(new_lines[-1])
                    continue
                prefix = raw_line[0]
                content = self._content(raw_line[1:])
                previous = (prefix, content)
                if prefix == " ":
                    new_lines.append(source_lines[old_start + old_offset])
                    old_offset += 1
                elif prefix == "-":
                    old_offset += 1
                else:
                    new_lines.append(content + "\n")
            result.extend(new_lines)
            cursor = old_end
        result.extend(source_lines[cursor:])
        return "".join(result), []


class ASTComparator:
    @staticmethod
    def get_function_qualnames(tree: ast.AST, module_name: str) -> dict[str, tuple[int, int]]:
        qualnames = {}

        class FunctionVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_class: str | None = None

            def visit_ClassDef(self, node: ast.ClassDef):
                old_class = self.current_class
                self.current_class = node.name
                self.generic_visit(node)
                self.current_class = old_class

            def visit_FunctionDef(self, node: ast.FunctionDef):
                if self.current_class:
                    qualname = f"{module_name}.{self.current_class}.{node.name}"
                else:
                    qualname = f"{module_name}.{node.name}"
                qualnames[qualname] = (node.lineno, node.end_lineno or node.lineno)
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                if self.current_class:
                    qualname = f"{module_name}.{self.current_class}.{node.name}"
                else:
                    qualname = f"{module_name}.{node.name}"
                qualnames[qualname] = (node.lineno, node.end_lineno or node.lineno)
                self.generic_visit(node)

        visitor = FunctionVisitor()
        visitor.visit(tree)
        return qualnames

    @staticmethod
    def get_module_level_nodes(tree: ast.AST) -> list[tuple[str, int, int]]:
        nodes = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign, ast.AnnAssign)):
                nodes.append((type(node).__name__, node.lineno, node.end_lineno or node.lineno))
        return nodes

    @staticmethod
    def get_statement_ranges(tree: ast.AST) -> list[tuple[int, int]]:
        ranges = []
        for node in ast.walk(tree):
            if isinstance(node, ast.stmt):
                ranges.append((node.lineno, node.end_lineno or node.lineno))
        return ranges

    @staticmethod
    def innermost_statement_span(ranges: list[tuple[int, int]], line: int) -> tuple[int, int] | None:
        candidates = [span for span in ranges if span[0] <= line <= span[1]]
        if not candidates:
            return None
        return min(candidates, key=lambda span: (span[1] - span[0], span[0]))

    @staticmethod
    def compare_functions(pre_qualnames: dict[str, tuple[int, int]], post_qualnames: dict[str, tuple[int, int]], pre_source: str, post_source: str, added_lines: list[int], removed_lines: list[int]) -> list[FunctionChange]:
        changes = []
        all_qualnames = set(pre_qualnames.keys()) | set(post_qualnames.keys())

        for qualname in sorted(all_qualnames):
            pre_range = pre_qualnames.get(qualname)
            post_range = post_qualnames.get(qualname)

            if pre_range is None and post_range is not None:
                changes.append(FunctionChange(qualname=qualname, change_type="added"))
            elif pre_range is not None and post_range is None:
                changes.append(FunctionChange(qualname=qualname, change_type="removed"))
            elif pre_range is not None and post_range is not None:
                pre_start, pre_end = pre_range
                post_start, post_end = post_range
                local_added = [line for line in added_lines if post_start <= line <= post_end]
                local_removed = [line for line in removed_lines if pre_start <= line <= pre_end]
                if local_added or local_removed:
                    changes.append(FunctionChange(
                        qualname=qualname,
                        change_type="modified",
                        added_lines=local_added,
                        removed_lines=local_removed,
                    ))

        return changes

    @staticmethod
    def compare_module_level(pre_nodes: list[tuple[str, int, int]], post_nodes: list[tuple[str, int, int]]) -> bool:
        pre_sigs = {(n[0], n[1], n[2]) for n in pre_nodes}
        post_sigs = {(n[0], n[1], n[2]) for n in post_nodes}
        return pre_sigs != post_sigs

    @staticmethod
    def asts_identical(pre_tree: ast.AST, post_tree: ast.AST) -> bool:
        return ast.dump(pre_tree) == ast.dump(post_tree)


def analyze_change(patch: Patch, source_root: Path) -> ChangeAnalysis:
    applicator = SourceApplicator(source_root)
    comparator = ASTComparator()
    analysis = ChangeAnalysis(commit_id=patch.commit_id)

    for fc in patch.file_changes:
        if not fc.path.endswith(".py"):
            continue

        fa = FileAnalysis(
            path=fc.path,
            operation=fc.operation,
            old_path=fc.old_path,
        )

        try:
            if fc.operation == FileOperation.ADDED:
                fa.pre_source = ""
                fa.pre_ast = ast.parse("")
                fa.post_source, apply_errors = applicator.apply_hunks("", fc.hunks)
                fa.apply_errors.extend(apply_errors)
                if apply_errors:
                    fa.apply_status = ApplyStatus.ERROR
                else:
                    try:
                        fa.post_ast = ast.parse(fa.post_source, filename=fc.path)
                    except SyntaxError as e:
                        fa.parse_errors.append(f"Post-source parse error: {e}")

            elif fc.operation == FileOperation.DELETED:
                fa.pre_source = applicator.read_file(fc.path)
                fa.post_source = ""

                if fa.pre_source is None:
                    fa.apply_errors.append(f"Source file not found: {fc.path}")
                    fa.apply_status = ApplyStatus.ERROR
                else:
                    try:
                        fa.pre_ast = ast.parse(fa.pre_source, filename=fc.path)
                    except SyntaxError as e:
                        fa.parse_errors.append(f"Pre-source parse error: {e}")

            elif fc.operation in (FileOperation.MODIFIED, FileOperation.RENAMED):
                old_path = fc.old_path if fc.operation == FileOperation.RENAMED else fc.path
                fa.pre_source = applicator.read_file(old_path)

                if fa.pre_source is None:
                    fa.apply_errors.append(f"Source file not found: {old_path}")
                    fa.apply_status = ApplyStatus.ERROR
                else:
                    try:
                        fa.pre_ast = ast.parse(fa.pre_source, filename=old_path)
                    except SyntaxError as e:
                        fa.parse_errors.append(f"Pre-source parse error: {e}")

                    fa.post_source, apply_errors = applicator.apply_hunks(fa.pre_source, fc.hunks)
                    fa.apply_errors.extend(apply_errors)
                    if apply_errors:
                        fa.apply_status = ApplyStatus.ERROR
                    else:
                        try:
                            fa.post_ast = ast.parse(fa.post_source, filename=fc.path)
                        except SyntaxError as e:
                            fa.parse_errors.append(f"Post-source parse error: {e}")

            else:
                fa.apply_errors.append(f"Unknown file operation: {fc.operation}")
                fa.apply_status = ApplyStatus.ERROR

            module_name = fc.path.replace("/", ".").replace(".py", "")

            if fa.pre_ast and fa.post_ast:
                pre_qualnames = comparator.get_function_qualnames(fa.pre_ast, module_name)
                post_qualnames = comparator.get_function_qualnames(fa.post_ast, module_name)

                fa.changed_functions = comparator.compare_functions(
                    pre_qualnames, post_qualnames, fa.pre_source, fa.post_source,
                    fc.added_lines, fc.removed_lines
                )

                pre_module = comparator.get_module_level_nodes(fa.pre_ast)
                post_module = comparator.get_module_level_nodes(fa.post_ast)
                fa.module_level_changes = comparator.compare_module_level(pre_module, post_module)

                fa.structural_changes = bool(fa.changed_functions) or fa.module_level_changes
                fa.ast_identical = (
                    fa.apply_status == ApplyStatus.OK
                    and not fa.parse_errors
                    and not fa.apply_errors
                    and comparator.asts_identical(fa.pre_ast, fa.post_ast)
                )

            elif fa.pre_ast and not fa.post_ast:
                pre_qualnames = comparator.get_function_qualnames(fa.pre_ast, module_name)
                fa.changed_functions = [
                    FunctionChange(qualname=qn, change_type="removed") for qn in pre_qualnames
                ]
                fa.structural_changes = True

            elif not fa.pre_ast and fa.post_ast:
                post_qualnames = comparator.get_function_qualnames(fa.post_ast, module_name)
                fa.changed_functions = [
                    FunctionChange(qualname=qn, change_type="added") for qn in post_qualnames
                ]
                fa.structural_changes = True

        except Exception as e:
            fa.apply_errors.append(f"Unexpected error during analysis: {e}")
            fa.apply_status = ApplyStatus.ERROR

        analysis.parse_errors.extend(fa.parse_errors)
        analysis.apply_errors.extend(fa.apply_errors)
        analysis.apply_errors.extend(fc.parse_warnings)
        analysis.file_analyses.append(fa)

    if patch.parse_errors:
        analysis.parse_errors.extend(patch.parse_errors)

    return analysis


def analyze_changeset(changeset: ChangeSet, source_root: Path) -> dict[str, ChangeAnalysis]:
    from .patch_parser import Patch
    analyses = {}
    for commit_id, fc_map in changeset.file_changes.items():
        patch = Patch(commit_id=commit_id, file_changes=list(fc_map.values()))
        analyses[commit_id] = analyze_change(patch, source_root)
    return analyses


def main() -> int:
    import sys
    import json

    source_root = Path("/app/sqlglot") if Path("/app/sqlglot").exists() else Path(".")
    commits_dir = Path("/data/commits")

    from .patch_parser import parse_all_patches
    patches = parse_all_patches(commits_dir)

    for commit_id, patch in patches.items():
        analysis = analyze_change(patch, source_root)
        output = {
            "commit": commit_id,
            "files": []
        }
        for fa in analysis.file_analyses:
            file_data = {
                "path": fa.path,
                "operation": fa.operation.value,
                "apply_status": fa.apply_status.value,
                "parse_errors": fa.parse_errors,
                "apply_errors": fa.apply_errors,
                "changed_functions": [
                    {"qualname": fc.qualname, "change_type": fc.change_type, "added_lines": fc.added_lines, "removed_lines": fc.removed_lines}
                    for fc in fa.changed_functions
                ],
                "module_level_changes": fa.module_level_changes,
                "structural_changes": fa.structural_changes,
                "ast_identical": fa.ast_identical,
            }
            if fa.post_source is not None:
                file_data["post_source"] = fa.post_source
            output["files"].append(file_data)
        print(json.dumps(output))

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
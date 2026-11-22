from __future__ import annotations

import argparse
import ast
import collections
import json
import os
from pathlib import Path
import sys

PINNED_COMMIT = "eb11aec4be8cb2122afe713a4816662c3f0fb2fa"


class SpanVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.spans: list[list[object]] = []
        self.imports: list[list[object]] = []
        self.stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.spans.append([".".join([*self.stack, node.name]), node.lineno, node.lineno, node.end_lineno, "class"])
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function(node, "function")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function(node, "function")

    def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, kind: str) -> None:
        qualname = ".".join([*self.stack, node.name])
        body_start = min(child.lineno for child in node.body)
        self.spans.append([qualname, node.lineno, body_start, node.end_lineno, kind])
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append([alias.name, None, 0, node.lineno])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            self.imports.append([node.module, alias.name, node.level, node.lineno])


class CallGraphVisitor(ast.NodeVisitor):
    """Extract function calls to build caller->callee edges."""

    def __init__(self, module_path: str) -> None:
        self.module_path = module_path
        self.stack: list[str] = []
        self.calls: dict[str, set[str]] = collections.defaultdict(set)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        qualname = ".".join([self.module_path, *self.stack, node.name]) if self.stack else f"{self.module_path}.{node.name}"
        self.stack.append(node.name)
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                callee = self._get_call_name(child)
                if callee:
                    self.calls[qualname].add(callee)
        self.generic_visit(node)
        self.stack.pop()

    def _get_call_name(self, call: ast.Call) -> str | None:
        if isinstance(call.func, ast.Name):
            return call.func.id
        if isinstance(call.func, ast.Attribute):
            parts = []
            node = call.func
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
                return ".".join(reversed(parts))
        return None


def module_name(relative_path: str) -> str:
    if relative_path.endswith("/__init__.py"):
        relative_path = relative_path.removesuffix("/__init__.py")
    else:
        relative_path = relative_path.removesuffix(".py")
    return relative_path.replace("/", ".")


def static_metadata(source_root: Path) -> tuple[dict, dict]:
    spans_by_file: dict[str, list] = {}
    reverse_imports: dict[str, set[str]] = collections.defaultdict(set)
    for path in sorted(source_root.rglob("*.py")):
        relative = path.relative_to(source_root).as_posix()
        try:
            tree = ast.parse(path.read_bytes(), filename=relative)
        except (SyntaxError, UnicodeDecodeError):
            continue
        visitor = SpanVisitor()
        visitor.visit(tree)
        spans_by_file[relative] = {
            "spans": sorted(visitor.spans, key=lambda row: (row[1], -(row[3] - row[1]), row[0])),
        }
        importer = module_name(relative)
        is_package = relative.endswith("/__init__.py")
        package_parts = importer.split(".") if is_package else importer.split(".")[:-1]
        for imported, imported_name, level, _line in visitor.imports:
            candidates: list[str] = []
            if level:
                base = package_parts[: max(0, len(package_parts) - level + 1)]
                target = ".".join([*base, imported] if imported else base)
            else:
                target = imported or ""
            if target:
                candidates.append(target)
                if imported_name and imported_name != "*":
                    candidates.append(f"{target}.{imported_name}")
            for candidate in candidates:
                reverse_imports[candidate].add(relative)
    return spans_by_file, {key: sorted(value) for key, value in sorted(reverse_imports.items())}


def build_call_graph(source_root: Path, spans_by_file: dict) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Build caller->callee and callee->callers indexes from pinned source."""
    call_graph: dict[str, set[str]] = collections.defaultdict(set)
    for relative in sorted(spans_by_file):
        path = source_root / relative
        try:
            tree = ast.parse(path.read_bytes(), filename=relative)
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        module = module_name(relative)
        visitor = CallGraphVisitor(module)
        visitor.visit(tree)
        for caller, callees in visitor.calls.items():
            call_graph[caller].update(callees)

    function_callers: dict[str, set[str]] = collections.defaultdict(set)
    for caller, callees in call_graph.items():
        for callee in callees:
            function_callers[callee].add(caller)

    return (
        {k: sorted(v) for k, v in sorted(call_graph.items())},
        {k: sorted(v) for k, v in sorted(function_callers.items())},
    )


def dialect_usage(source_root: Path, test_ids: list[str], accessed_document: dict[str, list[str]]) -> dict[str, list[int]]:
    dialects = {
        path.stem
        for directory in ("dialects", "parsers", "generators")
        for path in (source_root / "sqlglot" / directory).glob("*.py")
        if path.stem != "__init__"
    }
    test_index = {test_id: index for index, test_id in enumerate(test_ids)}
    tests_by_file: dict[str, list[str]] = collections.defaultdict(list)
    for test_id in test_ids:
        relative = test_id.split("::", 1)[0]
        tests_by_file[relative].append(test_id)

    usage: dict[str, set[int]] = collections.defaultdict(set)
    for relative, file_test_ids in sorted(tests_by_file.items()):
        path = source_root / relative
        try:
            tree = ast.parse(path.read_bytes(), filename=relative)
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue

        class TestVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.stack: list[str] = []

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                self._function(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self._function(node)

            def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
                qualname = "::".join([*self.stack, node.name])
                test_id = f"{relative}::{qualname}"
                index = test_index.get(test_id)
                if index is not None:
                    for child in ast.walk(node):
                        if isinstance(child, ast.Constant) and isinstance(child.value, str):
                            dialect = child.value.lower()
                            if dialect in dialects:
                                usage[dialect].add(index)
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

        TestVisitor().visit(tree)

    import re

    dialect_marker = re.compile(r"(?im)^\s*#\s*dialect\s*:\s*([a-z0-9_]+)")
    test_index = {test_id: index for index, test_id in enumerate(test_ids)}
    for test_id, paths in accessed_document.items():
        index = test_index.get(test_id)
        if index is None:
            continue
        for relative in paths:
            if relative.endswith(".py") or "__pycache__" in relative:
                continue
            try:
                content = (source_root / relative).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for dialect in dialect_marker.findall(content):
                dialect = dialect.lower()
                if dialect in dialects:
                    usage[dialect].add(index)
    return {key: sorted(value) for key, value in sorted(usage.items())}


def _replace_process_pools() -> None:
    import concurrent.futures

    def thread_pool(*args, mp_context=None, **kwargs):
        kwargs.pop("max_workers", None)
        return concurrent.futures.ThreadPoolExecutor(max_workers=4, **kwargs)

    for name in ("tests.test_optimizer", "tests.test_executor"):
        try:
            module = __import__(name, fromlist=["ProcessPoolExecutor"])
        except ImportError:
            continue
        if hasattr(module, "ProcessPoolExecutor"):
            module.ProcessPoolExecutor = thread_pool


def run_coverage(source_root: Path, database: Path, in_process: bool = True) -> int:
    import coverage
    import pytest

    current_context = ""
    accessed: dict[str, set[str]] = collections.defaultdict(set)

    def audit(event: str, args: tuple) -> None:
        if not current_context:
            return
        if event not in {"open", "os.listdir", "os.scandir"}:
            return
        raw_path = args[0]
        if not isinstance(raw_path, (str, bytes, os.PathLike)):
            return
        try:
            path = Path(raw_path)
            if not path.is_absolute():
                path = source_root / path
            relative = path.resolve().relative_to(source_root.resolve()).as_posix()
        except (OSError, ValueError, TypeError):
            return
        accessed[current_context].add(relative)

    class ContextPlugin:
        def pytest_collection_modifyitems(self, items):
            if in_process:
                _replace_process_pools()

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtest_protocol(self, item: pytest.Item, nextitem: pytest.Item | None):
            nonlocal current_context
            current_context = item.nodeid
            cov.switch_context(item.nodeid)
            try:
                yield
            finally:
                current_context = ""
                cov.switch_context("")

    sys.addaudithook(audit)
    cov = coverage.Coverage(
        data_file=str(database),
        config_file=False,
        source=[str(source_root)],
        check_preimported=True,
        concurrency=["thread"],
    )
    cov.start()
    try:
        result = pytest.main(["-q", "--disable-warnings", str(source_root / "tests")], plugins=[ContextPlugin()])
    finally:
        cov.stop()
        cov.save()
    (database.parent / "accessed.json").write_text(
        json.dumps({key: sorted(value) for key, value in sorted(accessed.items())}, separators=(",", ":"))
    )
    return int(result)


def build_map_document(source_root: Path, tests_path: Path, database: Path) -> dict:
    import coverage

    tests_document = json.loads(tests_path.read_text())
    test_ids = sorted(test["id"] for test in tests_document["tests"])
    test_index = {test_id: index for index, test_id in enumerate(test_ids)}

    data = coverage.CoverageData(str(database))
    data.read()
    lines_by_file: dict[str, dict[int, set[int]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    unmatched_contexts: set[str] = set()
    for filename in sorted(data.measured_files()):
        path = Path(filename)
        try:
            relative = path.resolve().relative_to(source_root.resolve()).as_posix()
        except ValueError:
            continue
        contexts_by_line = data.contexts_by_lineno(filename)
        for line, contexts in contexts_by_line.items():
            for context in contexts:
                index = test_index.get(context)
                if index is None:
                    if context:
                        unmatched_contexts.add(context)
                else:
                    lines_by_file[relative][line].add(index)

    spans_by_file, reverse_imports = static_metadata(source_root)
    call_graph, function_callers = build_call_graph(source_root, spans_by_file)

    files: dict[str, dict] = {}
    all_source_files = set(lines_by_file) | set(spans_by_file)
    for relative in sorted(all_source_files):
        line_map = lines_by_file.get(relative, {})
        rows = [[line, sorted(lines_by_file[relative][line])] for line in sorted(line_map)]
        spans = spans_by_file.get(relative, {}).get("spans", [])
        function_coverage: dict[str, set[int]] = collections.defaultdict(set)
        file_coverage: set[int] = set()
        for line, indexes in line_map.items():
            file_coverage.update(indexes)
            containing = [
                span for span in spans
                if span[4] == "function" and span[2] <= line <= span[3]
            ]
            if containing:
                span = min(containing, key=lambda row: (row[3] - row[2], row[0]))
                function_coverage[span[0]].update(indexes)
        files[relative] = {
            "lines": rows,
            "spans": spans,
            "functions": {key: sorted(value) for key, value in sorted(function_coverage.items())},
            "file": sorted(file_coverage),
        }

    accessed_document = json.loads((database.parent / "accessed.json").read_text())
    fixture_map: dict[str, set[int]] = collections.defaultdict(set)
    source_readers: dict[str, set[int]] = collections.defaultdict(set)
    for test_id, paths in accessed_document.items():
        index = test_index.get(test_id)
        if index is None:
            continue
        for relative in paths:
            if relative.endswith(".py"):
                source_readers[relative].add(index)
            else:
                fixture_map[relative].add(index)

    document = {
        "version": 2,
        "source_commit": PINNED_COMMIT,
        "test_ids": test_ids,
        "files": files,
        "reverse_imports": reverse_imports,
        "fixtures": {key: sorted(value) for key, value in sorted(fixture_map.items())},
        "source_readers": {key: sorted(value) for key, value in sorted(source_readers.items())},
        "dialect_tests": dialect_usage(source_root, test_ids, accessed_document),
        "call_graph": call_graph,
        "function_callers": function_callers,
    }
    return document


def load_map(path: Path) -> dict:
    import zlib

    return json.loads(zlib.decompress(path.read_bytes()))


def merge_map_documents(base: dict, overlay: dict) -> dict:
    if base["source_commit"] != overlay["source_commit"]:
        raise ValueError("map source commit mismatch")
    if base["test_ids"] != overlay["test_ids"]:
        raise ValueError("map test catalog mismatch")

    files: dict[str, dict] = {}
    for relative in sorted(set(base["files"]) | set(overlay["files"])):
        left = base["files"].get(relative)
        right = overlay["files"].get(relative)
        spans = (left or right or {}).get("spans", [])
        lines: dict[int, set[int]] = collections.defaultdict(set)
        for source in (left, right):
            if not source:
                continue
            for line, indexes in source["lines"]:
                lines[line].update(indexes)
        function_coverage: dict[str, set[int]] = collections.defaultdict(set)
        file_coverage: set[int] = set()
        for line, indexes in lines.items():
            file_coverage.update(indexes)
            containing = [
                span
                for span in spans
                if span[4] == "function" and span[2] <= line <= span[3]
            ]
            if containing:
                span = min(containing, key=lambda row: (row[3] - row[2], row[0]))
                function_coverage[span[0]].update(indexes)
        files[relative] = {
            "lines": [[line, sorted(lines[line])] for line in sorted(lines)],
            "spans": spans,
            "functions": {key: sorted(value) for key, value in sorted(function_coverage.items())},
            "file": sorted(file_coverage),
        }
    return {
        "version": base.get("version", 1),
        "source_commit": base["source_commit"],
        "test_ids": base["test_ids"],
        "files": files,
        "reverse_imports": base["reverse_imports"],
        "fixtures": base["fixtures"],
        "source_readers": base["source_readers"],
        "dialect_tests": base.get("dialect_tests", {}),
        "call_graph": base.get("call_graph", {}),
        "function_callers": base.get("function_callers", {}),
    }


def write_map(document: dict, output: Path, report: dict) -> None:
    import zlib

    encoded = zlib.compress(json.dumps(document, separators=(",", ":"), sort_keys=True).encode(), 9)
    output.write_bytes(encoded)
    report["source_files"] = len(document["files"])
    report["covered_lines"] = sum(len(item["lines"]) for item in document["files"].values())
    report["artifact_bytes"] = len(encoded)
    report["uncompressed_bytes"] = len(json.dumps(document, separators=(",", ":"), sort_keys=True).encode())
    (output.parent / "map_build_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def map_report(document: dict, database: Path, source_root: Path) -> dict:
    test_ids = document["test_ids"]
    mapped = {
        test_ids[index]
        for item in document["files"].values()
        for index in item["file"]
    }
    accessed_document = json.loads((database.parent / "accessed.json").read_text())
    actual_contexts = set(accessed_document)
    return {
        "source_commit": document["source_commit"],
        "tests_in_catalog": len(test_ids),
        "coverage_contexts_matched": len(mapped),
        "tests_without_coverage": sorted(set(test_ids) - mapped),
        "access_trace_contexts": len(actual_contexts & set(test_ids)),
        "tests_without_access_trace": sorted(set(test_ids) - actual_contexts),
        "unmatched_coverage_contexts": [],
        "source_files": len(document["files"]),
        "covered_lines": sum(len(item["lines"]) for item in document["files"].values()),
        "artifact_bytes": 0,
        "uncompressed_bytes": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument("tests", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--in-process", dest="in_process", action="store_true", default=True)
    parser.add_argument("--process-pool", dest="in_process", action="store_false")
    parser.add_argument("--merge", type=Path, default=None)
    options = parser.parse_args()
    options.output.parent.mkdir(parents=True, exist_ok=True)
    database = options.output.parent / "coverage.db"
    result = run_coverage(options.source_root, database, in_process=options.in_process)
    document = build_map_document(options.source_root, options.tests, database)
    report = map_report(document, database, options.source_root)
    report["coverage_view"] = "in-process" if options.in_process else "process-pool"
    if options.merge is not None:
        document = merge_map_documents(document, load_map(options.merge))
        report["coverage_view"] = "in-process + process-pool"
        report["merged_with"] = str(options.merge)
    write_map(document, options.output, report)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
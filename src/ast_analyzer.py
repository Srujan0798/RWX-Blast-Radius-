"""L03 — Python Static Analysis & AST Intelligence

Lightweight source-analysis engine using stdlib AST.
Extracts modules, classes, functions, imports, symbols, references.
"""

import ast
import sys
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


def build_test_name_usage(source_root: Path, tests_json_path: Path) -> dict[str, list[int]]:
    """Map each identifier used inside a test to the catalog numbers of the
    tests that reference it. Generic and derived only from pinned source plus
    the test catalog; never from commit outcomes."""
    import json

    document = json.loads(Path(tests_json_path).read_text())
    ids_by_file: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for test in document.get("tests", []):
        ids_by_file[test["file"]].append((test["id"], test["number"]))

    usage: dict[str, set[int]] = defaultdict(set)

    for relative, entries in ids_by_file.items():
        path = Path(source_root) / relative
        try:
            tree = ast.parse(path.read_bytes(), filename=relative)
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue

        numbers_by_func: dict[str, set[int]] = defaultdict(set)
        for test_id, number in entries:
            _, _, suffix = test_id.partition("::")
            if not suffix:
                continue
            numbers_by_func[suffix.split("::")[-1]].add(number)
            if "::" in suffix:
                numbers_by_func[suffix.replace("::", ".")].add(number)

        class _TestVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.stack: list[str] = []

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                self._handle(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self._handle(node)

            def _handle(self, node) -> None:
                key = f"{self.stack[-1]}.{node.name}" if self.stack else node.name
                numbers = numbers_by_func.get(node.name) or numbers_by_func.get(key)
                if numbers:
                    names: set[str] = set()
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                            names.add(child.id)
                        elif isinstance(child, ast.Attribute):
                            names.add(child.attr)
                    for name in names:
                        usage[name].update(numbers)
                self.generic_visit(node)

        _TestVisitor().visit(tree)

    return {name: sorted(nums) for name, nums in sorted(usage.items())}


class SymbolType(Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMPORT = "import"
    ATTRIBUTE = "attribute"
    VARIABLE = "variable"


class DefinitionType(Enum):
    DEF = "def"
    CLASS = "class"
    IMPORT = "import"
    IMPORT_FROM = "import_from"
    ASSIGN = "assign"
    ANNOTATED_ASSIGN = "annotated_assign"
    GLOBAL = "global"
    NONLOCAL = "nonlocal"


class ReferenceType(Enum):
    CALL = "call"
    ATTRIBUTE = "attribute"
    NAME = "name"
    SUBSCRIPT = "subscript"


@dataclass
class Symbol:
    symbol_id: str
    qualified_name: str
    symbol_type: SymbolType
    module_path: str
    parent_symbol: str | None
    start_line: int
    end_line: int
    decorators: list[str] = field(default_factory=list)
    confidence: float = 1.0
    analysis_status: str = "resolved"


@dataclass
class Definition:
    defining_symbol: str
    defined_name: str
    scope: str
    source_location: tuple[str, int]


@dataclass
class Reference:
    referencing_symbol: str | None
    referenced_name: str
    source_location: tuple[str, int]
    reference_type: ReferenceType
    resolution_status: str = "unresolved"


@dataclass
class ImportRecord:
    importing_module: str
    imported_module: str | None
    imported_name: str | None
    alias: str | None
    import_type: str
    source_location: tuple[str, int]


@dataclass
class ModuleIndex:
    module_name: str
    file_path: str
    package: str | None
    symbols: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)


class ASTAnalyzer:
    def __init__(self, source_root: Path):
        self.source_root = source_root
        self.symbols: dict[str, Symbol] = {}
        self.definitions: list[Definition] = []
        self.references: list[Reference] = []
        self.imports: list[ImportRecord] = []
        self.module_index: dict[str, ModuleIndex] = {}
        self.symbol_by_qname: dict[str, str] = {}
        self.name_definitions: dict[str, list[str]] = defaultdict(list)
        self.name_references: dict[str, list[str]] = defaultdict(list)
        self._symbol_counter = 0

    def _gen_symbol_id(self) -> str:
        self._symbol_counter += 1
        return f"sym_{self._symbol_counter}"

    def analyze_repository(self, tests_json_path: Path | None = None) -> dict[str, Any]:
        py_files = list(self.source_root.rglob("*.py"))
        for py_file in py_files:
            try:
                self._analyze_file(py_file)
            except Exception as e:
                print(f"Warning: Failed to analyze {py_file}: {e}", file=sys.stderr)

        self._build_indexes()
        metadata = self._serialize_metadata()
        
        # Build test-level name usage index if tests.json is available
        if tests_json_path and tests_json_path.exists():
            metadata["test_name_usage_index"] = build_test_name_usage(self.source_root, tests_json_path)
        else:
            metadata["test_name_usage_index"] = {}
        
        return metadata

    def _analyze_file(self, file_path: Path) -> None:
        rel_path = file_path.relative_to(self.source_root)
        module_name = str(rel_path).replace("/", ".").replace(".py", "")
        package = ".".join(module_name.split(".")[:-1]) if "." in module_name else None

        content = file_path.read_text()
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            print(f"Warning: Syntax error in {file_path}: {e}", file=sys.stderr)
            return

        module_idx = ModuleIndex(
            module_name=module_name,
            file_path=str(rel_path),
            package=package,
        )
        self.module_index[module_name] = module_idx

        visitor = _ASTVisitor(
            analyzer=self,
            module_name=module_name,
            file_path=str(rel_path),
            module_idx=module_idx,
        )
        visitor.visit(tree)

    def _build_indexes(self) -> None:
        for sym_id, symbol in self.symbols.items():
            self.symbol_by_qname[symbol.qualified_name] = sym_id

        for defn in self.definitions:
            self.name_definitions[defn.defined_name].append(defn.defining_symbol)

        for ref in self.references:
            self.name_references[ref.referenced_name].append(ref.referencing_symbol or "unknown")

    def _serialize_metadata(self) -> dict[str, Any]:
        return {
            "module_index": {
                name: {
                    "module_name": m.module_name,
                    "file_path": m.file_path,
                    "package": m.package,
                    "symbols": m.symbols,
                    "imports": m.imports,
                    "classes": m.classes,
                    "functions": m.functions,
                }
                for name, m in self.module_index.items()
            },
            "symbol_index": {
                sym_id: {
                    "symbol_id": s.symbol_id,
                    "qualified_name": s.qualified_name,
                    "symbol_type": s.symbol_type.value,
                    "module_path": s.module_path,
                    "parent_symbol": s.parent_symbol,
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "decorators": s.decorators,
                    "confidence": s.confidence,
                    "analysis_status": s.analysis_status,
                }
                for sym_id, s in self.symbols.items()
            },
            "import_index": [
                {
                    "importing_module": i.importing_module,
                    "imported_module": i.imported_module,
                    "imported_name": i.imported_name,
                    "alias": i.alias,
                    "import_type": i.import_type,
                    "source_location": i.source_location,
                }
                for i in self.imports
            ],
            "name_definition_index": dict(self.name_definitions),
            "name_usage_index": dict(self.name_references),
        }


class _ASTVisitor(ast.NodeVisitor):
    def __init__(self, analyzer: ASTAnalyzer, module_name: str, file_path: str, module_idx: ModuleIndex):
        self.analyzer = analyzer
        self.module_name = module_name
        self.file_path = file_path
        self.module_idx = module_idx
        self.current_class: str | None = None
        self.current_function: str | None = None
        self.scope_stack: list[str] = [module_name]

    def _add_symbol(self, qualified_name: str, symbol_type: SymbolType, node: ast.AST, parent: str | None = None, decorators: list[str] | None = None) -> str:
        sym_id = self.analyzer._gen_symbol_id()
        start_line = getattr(node, "lineno", 1)
        end_line = getattr(node, "end_lineno", start_line)
        symbol = Symbol(
            symbol_id=sym_id,
            qualified_name=qualified_name,
            symbol_type=symbol_type,
            module_path=self.module_name,
            parent_symbol=parent,
            start_line=start_line,
            end_line=end_line,
            decorators=decorators or [],
        )
        self.analyzer.symbols[sym_id] = symbol
        self.module_idx.symbols.append(sym_id)
        if symbol_type == SymbolType.CLASS:
            self.module_idx.classes.append(qualified_name)
        elif symbol_type in (SymbolType.FUNCTION, SymbolType.METHOD):
            self.module_idx.functions.append(qualified_name)
        return sym_id

    def visit_Module(self, node: ast.Module) -> None:
        self._add_symbol(self.module_name, SymbolType.MODULE, node, parent=None, decorators=None)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qualified_name = f"{self.module_name}.{node.name}"
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        parent = self.current_class or self.module_name
        sym_id = self._add_symbol(qualified_name, SymbolType.CLASS, node, parent, decorators)

        old_class = self.current_class
        self.current_class = qualified_name
        self.scope_stack.append(qualified_name)

        for base in node.bases:
            if isinstance(base, ast.Name):
                self._record_reference(sym_id, base.id, ReferenceType.ATTRIBUTE, (self.file_path, node.lineno))
            elif isinstance(base, ast.Attribute):
                self._record_reference(sym_id, self._get_attr_name(base), ReferenceType.ATTRIBUTE, (self.file_path, node.lineno))

        self.generic_visit(node)

        self.current_class = old_class
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node, is_async=True)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool) -> None:
        qualified_name = f"{self.module_name}.{node.name}"
        if self.current_class:
            qualified_name = f"{self.current_class}.{node.name}"
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        parent = self.current_class or self.module_name
        sym_type = SymbolType.METHOD if self.current_class else SymbolType.FUNCTION
        sym_id = self._add_symbol(qualified_name, sym_type, node, parent, decorators)

        self.analyzer.definitions.append(Definition(
            defining_symbol=sym_id,
            defined_name=node.name,
            scope=self.scope_stack[-1],
            source_location=(self.file_path, node.lineno),
        ))
        self.analyzer.name_definitions[node.name].append(sym_id)

        old_function = self.current_function
        self.current_function = qualified_name
        self.scope_stack.append(qualified_name)

        for arg in node.args.args:
            self.analyzer.definitions.append(Definition(
                defining_symbol=sym_id,
                defined_name=arg.arg,
                scope=qualified_name,
                source_location=(self.file_path, node.lineno),
            ))
            self.analyzer.name_definitions[arg.arg].append(sym_id)

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                self._record_reference(sym_id, decorator.id, ReferenceType.NAME, (self.file_path, decorator.lineno))
            elif isinstance(decorator, ast.Attribute):
                self._record_reference(sym_id, self._get_attr_name(decorator), ReferenceType.ATTRIBUTE, (self.file_path, decorator.lineno))
            elif isinstance(decorator, ast.Call):
                self._visit_call_for_refs(decorator, sym_id)

        self.generic_visit(node)

        self.current_function = old_function
        self.scope_stack.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            imported = alias.name
            alias_name = alias.asname
            self.analyzer.imports.append(ImportRecord(
                importing_module=self.module_name,
                imported_module=imported,
                imported_name=None,
                alias=alias_name,
                import_type="import",
                source_location=(self.file_path, node.lineno),
            ))
            self.module_idx.imports.append(imported)
            name = alias_name or imported.split(".")[0]
            self.analyzer.definitions.append(Definition(
                defining_symbol=f"{self.module_name}.{name}",
                defined_name=name,
                scope=self.module_name,
                source_location=(self.file_path, node.lineno),
            ))
            self.analyzer.name_definitions[name].append(f"{self.module_name}.{name}")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        level = node.level
        if level > 0:
            parts = self.module_name.split(".")
            base = ".".join(parts[:-level]) if level <= len(parts) else ""
            if base:
                module = base + ("." + module if module else "")
            else:
                module = "." * level + module

        for alias in node.names:
            imported = f"{module}.{alias.name}" if module else alias.name
            alias_name = alias.asname
            self.analyzer.imports.append(ImportRecord(
                importing_module=self.module_name,
                imported_module=module if module else None,
                imported_name=alias.name,
                alias=alias_name,
                import_type="from_import",
                source_location=(self.file_path, node.lineno),
            ))
            if module:
                self.module_idx.imports.append(module)
            name = alias_name or alias.name
            self.analyzer.definitions.append(Definition(
                defining_symbol=f"{self.module_name}.{name}",
                defined_name=name,
                scope=self.module_name,
                source_location=(self.file_path, node.lineno),
            ))
            self.analyzer.name_definitions[name].append(f"{self.module_name}.{name}")

    def visit_Call(self, node: ast.Call) -> None:
        self._visit_call_for_refs(node, self.current_function or self.current_class or self.module_name)
        self.generic_visit(node)

    def _visit_call_for_refs(self, node: ast.Call, referencing_symbol: str) -> None:
        if isinstance(node.func, ast.Name):
            self._record_reference(referencing_symbol, node.func.id, ReferenceType.CALL, (self.file_path, node.lineno))
        elif isinstance(node.func, ast.Attribute):
            self._record_reference(referencing_symbol, self._get_attr_name(node.func), ReferenceType.CALL, (self.file_path, node.lineno))

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.ctx, ast.Load):
            attr_name = self._get_attr_name(node)
            ref_symbol = self.current_function or self.current_class or self.module_name
            self._record_reference(ref_symbol, attr_name, ReferenceType.ATTRIBUTE, (self.file_path, node.lineno))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            ref_symbol = self.current_function or self.current_class or self.module_name
            self._record_reference(ref_symbol, node.id, ReferenceType.NAME, (self.file_path, node.lineno))
        elif isinstance(node.ctx, ast.Store):
            self.analyzer.definitions.append(Definition(
                defining_symbol=self.current_function or self.current_class or self.module_name,
                defined_name=node.id,
                scope=self.scope_stack[-1],
                source_location=(self.file_path, node.lineno),
            ))
            self.analyzer.name_definitions[node.id].append(self.current_function or self.current_class or self.module_name)
        self.generic_visit(node)

    def _get_decorator_name(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attr_name(node)
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "<unknown>"

    def _get_attr_name(self, node: ast.Attribute) -> str:
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))

    def _record_reference(self, referencing_symbol: str | None, referenced_name: str, ref_type: ReferenceType, location: tuple[str, int]) -> None:
        self.analyzer.references.append(Reference(
            referencing_symbol=referencing_symbol,
            referenced_name=referenced_name,
            source_location=location,
            reference_type=ref_type,
        ))
        self.analyzer.name_references[referenced_name].append(referencing_symbol or "unknown")


def main() -> int:
    import sys
    source_root = Path("/app/sqlglot") if Path("/app/sqlglot").exists() else Path(".")
    tests_json_path = Path("/data/tests.json") if Path("/data/tests.json").exists() else Path("tests.json")
    analyzer = ASTAnalyzer(source_root)
    metadata = analyzer.analyze_repository(tests_json_path)

    import json
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
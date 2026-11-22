"""L04 — Graph Engineering & Dependency Propagation

Builds unified dependency graph from AST metadata.
Propagates change impact through import, symbol, and test relationships.
"""

import json
from dataclasses import dataclass, field
from typing import Any
from enum import Enum
from pathlib import Path
from collections import defaultdict, deque


class NodeType(Enum):
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    SYMBOL = "symbol"
    TEST = "test"
    FIXTURE = "fixture"


class EdgeType(Enum):
    CONTAINS = "contains"
    DEFINES = "defines"
    USES = "uses"
    IMPORTS = "imports"
    REEXPORTS = "reexports"
    REFERENCES = "references"
    INHERITS = "inherits"
    COVERS = "covers"
    ACCESSES = "accesses"
    USES_FIXTURE = "uses_fixture"
    DEPENDS_ON = "depends_on"


@dataclass
class GraphNode:
    node_id: str
    node_type: NodeType
    qualified_name: str
    file_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType
    direct: bool = True
    provenance: str = ""


@dataclass
class ImpactEvidence:
    commit_id: str
    impacted_files: list[str] = field(default_factory=list)
    impacted_modules: list[str] = field(default_factory=list)
    impacted_symbols: list[str] = field(default_factory=list)
    candidate_tests: list[int] = field(default_factory=list)
    evidence_paths: list[list[str]] = field(default_factory=list)
    direct_relationships: list[tuple[str, str, EdgeType]] = field(default_factory=list)
    transitive_relationships: list[tuple[str, str, EdgeType]] = field(default_factory=list)
    coverage_evidence: list[tuple[int, str]] = field(default_factory=list)
    fixture_evidence: list[tuple[int, str]] = field(default_factory=list)
    unresolved_relationships: list[str] = field(default_factory=list)
    dynamic_feature_flags: list[str] = field(default_factory=list)
    graph_analysis_status: str = "ok"


class DependencyGraph:
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self.forward_adj: dict[str, list[tuple[str, EdgeType]]] = defaultdict(list)
        self.reverse_adj: dict[str, list[tuple[str, EdgeType]]] = defaultdict(list)
        self.node_id_counter = 0

    def _gen_node_id(self) -> str:
        self.node_id_counter += 1
        return f"n_{self.node_id_counter}"

    def add_node(self, node_type: NodeType, qualified_name: str, file_path: str | None = None, **metadata) -> str:
        node_id = self._gen_node_id()
        node = GraphNode(
            node_id=node_id,
            node_type=node_type,
            qualified_name=qualified_name,
            file_path=file_path,
            metadata=metadata,
        )
        self.nodes[node_id] = node
        return node_id

    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType, direct: bool = True, provenance: str = "") -> None:
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            direct=direct,
            provenance=provenance,
        )
        self.edges.append(edge)
        self.forward_adj[source_id].append((target_id, edge_type))
        self.reverse_adj[target_id].append((source_id, edge_type))

    def get_node_by_qname(self, qualified_name: str) -> GraphNode | None:
        for node in self.nodes.values():
            if node.qualified_name == qualified_name:
                return node
        return None

    def get_nodes_by_type(self, node_type: NodeType) -> list[GraphNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def bfs_reachable(self, start_nodes: list[str], edge_types: list[EdgeType] | None = None, max_depth: int = 10) -> set[str]:
        visited = set(start_nodes)
        queue = deque([(n, 0) for n in start_nodes])

        while queue:
            node_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for target_id, edge_type in self.forward_adj.get(node_id, []):
                if edge_types and edge_type not in edge_types:
                    continue
                if target_id not in visited:
                    visited.add(target_id)
                    queue.append((target_id, depth + 1))
        return visited

    def reverse_reachable(self, start_nodes: list[str], edge_types: list[EdgeType] | None = None, max_depth: int = 10) -> set[str]:
        visited = set(start_nodes)
        queue = deque([(n, 0) for n in start_nodes])

        while queue:
            node_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for source_id, edge_type in self.reverse_adj.get(node_id, []):
                if edge_types and edge_type not in edge_types:
                    continue
                if source_id not in visited:
                    visited.add(source_id)
                    queue.append((source_id, depth + 1))
        return visited


class GraphEngine:
    def __init__(self, ast_metadata_path: str, tests_path: str):
        self.ast_metadata_path = ast_metadata_path
        self.tests_path = tests_path
        self.graph = DependencyGraph()
        self.test_by_number: dict[int, dict] = {}
        self.module_to_node: dict[str, str] = {}
        self.symbol_to_node: dict[str, str] = {}
        self.test_to_node: dict[int, str] = {}
        self._load_data()
        self._build_graph()

    def _load_data(self) -> None:
        with open(self.ast_metadata_path) as f:
            self.ast_metadata = json.load(f)

        with open(self.tests_path) as f:
            tests_data = json.load(f)
            for test in tests_data["tests"]:
                self.test_by_number[test["number"]] = test

    def _build_graph(self) -> None:
        self._build_module_nodes()
        self._build_symbol_nodes()
        self._build_test_nodes()
        self._build_import_edges()
        self._build_symbol_reference_edges()
        self._build_test_coverage_edges()
        self._build_containment_edges()

    def _build_module_nodes(self) -> None:
        for module_name, module_info in self.ast_metadata.get("module_index", {}).items():
            node_id = self.graph.add_node(
                NodeType.MODULE,
                module_name,
                module_info.get("file_path"),
                package=module_info.get("package"),
            )
            self.module_to_node[module_name] = node_id

    def _build_symbol_nodes(self) -> None:
        for sym_id, symbol in self.ast_metadata.get("symbol_index", {}).items():
            node_type_map = {
                "class": NodeType.CLASS,
                "function": NodeType.FUNCTION,
                "method": NodeType.METHOD,
            }
            node_type = node_type_map.get(symbol.get("symbol_type"), NodeType.SYMBOL)
            node_id = self.graph.add_node(
                node_type,
                symbol.get("qualified_name", ""),
                symbol.get("module_path"),
                line_start=symbol.get("start_line"),
                line_end=symbol.get("end_line"),
                decorators=symbol.get("decorators", []),
                symbol_type=symbol.get("symbol_type"),
            )
            self.symbol_to_node[symbol.get("qualified_name", "")] = node_id

            module_name = symbol.get("module_path", "")
            if module_name in self.module_to_node:
                self.graph.add_edge(
                    self.module_to_node[module_name],
                    node_id,
                    EdgeType.CONTAINS,
                    provenance="ast",
                )

    def _build_test_nodes(self) -> None:
        for test_num, test in self.test_by_number.items():
            node_id = self.graph.add_node(
                NodeType.TEST,
                test["id"],
                test["file"],
                test_number=test_num,
                duration_ms=int(test["seconds"] * 1000 + 0.5),
            )
            self.test_to_node[test_num] = node_id

    def _build_import_edges(self) -> None:
        for imp in self.ast_metadata.get("import_index", []):
            importing = imp.get("importing_module", "")
            imported = imp.get("imported_module", "")
            if importing in self.module_to_node and imported in self.module_to_node:
                self.graph.add_edge(
                    self.module_to_node[importing],
                    self.module_to_node[imported],
                    EdgeType.IMPORTS,
                    provenance="ast_import",
                )

    def _build_symbol_reference_edges(self) -> None:
        for name, ref_modules in self.ast_metadata.get("name_usage_index", {}).items():
            for ref_module in ref_modules:
                if ref_module in self.module_to_node:
                    for def_module in self.ast_metadata.get("name_definition_index", {}).get(name, []):
                        if def_module in self.module_to_node:
                            self.graph.add_edge(
                                self.module_to_node[ref_module],
                                self.module_to_node[def_module],
                                EdgeType.REFERENCES,
                                direct=False,
                                provenance=f"name_ref:{name}",
                            )

    def _build_test_coverage_edges(self) -> None:
        for test_num, test in self.test_by_number.items():
            test_file = test["file"]
            test_module = test_file.replace("/", ".").replace(".py", "")
            if test_module in self.module_to_node and test_num in self.test_to_node:
                self.graph.add_edge(
                    self.module_to_node[test_module],
                    self.test_to_node[test_num],
                    EdgeType.COVERS,
                    provenance="test_coverage",
                )

    def _build_containment_edges(self) -> None:
        for sym_name, def_modules in self.ast_metadata.get("name_definition_index", {}).items():
            for def_module in def_modules:
                if def_module in self.module_to_node:
                    for sym_qname, sym_id in self.symbol_to_node.items():
                        if sym_qname.startswith(def_module + ".") or sym_qname == def_module:
                            self.graph.add_edge(
                                self.module_to_node[def_module],
                                sym_id,
                                EdgeType.DEFINES,
                                provenance="ast_definition",
                            )

    def _get_changed_symbols(self, py_file: str, changeset: dict) -> list[str]:
        """Map changed line numbers to specific symbols using AST metadata."""
        if "/" not in py_file and py_file.endswith(".py"):
            file_path = py_file
        elif "/" not in py_file:
            file_path = py_file.replace(".", "/") + ".py"
        else:
            file_path = py_file
        
        module_name = file_path.replace("/", ".").replace(".py", "")
        changed = set()
        
        added_lines = changeset.get("added_lines", {}).get(file_path, [])
        removed_lines = changeset.get("removed_lines", {}).get(file_path, [])
        all_changed_lines = set(added_lines) | set(removed_lines)
        
        if not all_changed_lines:
            return []
        
        symbol_index = self.ast_metadata.get("symbol_index", {})
        for sym_id, symbol in symbol_index.items():
            if symbol.get("module_path") == module_name:
                start = symbol.get("start_line", 0)
                end = symbol.get("end_line", 0)
                if start <= 0 or end <= 0:
                    continue
                for line in all_changed_lines:
                    if start <= line <= end:
                        changed.add(symbol.get("qualified_name", ""))
                        break
        
        return list(changed)

    def propagate_impact(self, changeset: dict, max_depth: int = 5) -> ImpactEvidence:
        evidence = ImpactEvidence(commit_id=changeset.get("commit_id", ""))

        python_files = changeset.get("python_files", set())
        all_changed = changeset.get("all_changed_files", set())

        start_nodes = []

        for py_file in python_files:
            module_name = py_file.replace("/", ".").replace(".py", "")
            if module_name in self.module_to_node:
                start_nodes.append(self.module_to_node[module_name])
                evidence.impacted_modules.append(module_name)
                evidence.impacted_files.append(py_file)

        for fixture_file in all_changed:
            if fixture_file.startswith("tests/fixtures/"):
                evidence.impacted_files.append(fixture_file)

        if not start_nodes:
            evidence.graph_analysis_status = "no_python_changes"
            return evidence

        all_impacted_modules = set()

        # --- Symbol-level analysis for changed files ---
        for py_file in python_files:
            module_name = py_file.replace("/", ".").replace(".py", "")
            if module_name in self.module_to_node:
                changed_symbols = self._get_changed_symbols(py_file, changeset)
                evidence.impacted_symbols.extend(changed_symbols)
                # Skip name_usage_index for dialect modules - simple names are too coarse
                is_dialect_module = module_name.startswith("sqlglot.dialects.")
                if not is_dialect_module:
                    for sym in changed_symbols:
                        simple_name = sym.split(".")[-1] if "." in sym else sym
                        for user_module in self.ast_metadata.get("name_usage_index", {}).get(sym, []):
                            if user_module in self.module_to_node:
                                all_impacted_modules.add(user_module)
                                evidence.impacted_modules.append(user_module)
                        # Also check test-level name usage index for precise test mapping
                        test_usage = self.ast_metadata.get("test_name_usage_index", {}).get(simple_name, [])
                        for test_num in test_usage:
                            evidence.candidate_tests.append(test_num)

        # 1. Find modules that import changed modules (reverse IMPORTS only)
        importer_modules = set()
        for start in start_nodes:
            importers = self.graph.reverse_reachable([start], [EdgeType.IMPORTS], max_depth)
            importer_modules.update(importers)

        # 2. Also find modules that the changed module imports (forward IMPORTS, limited depth)
        imported_modules = set()
        for start in start_nodes:
            imports = self.graph.bfs_reachable([start], [EdgeType.IMPORTS], min(max_depth, 2))
            imported_modules.update(imports)

        all_impacted_modules = set()
        covers_source_modules = set()
        for node_id in importer_modules | imported_modules:
            node = self.graph.nodes.get(node_id)
            if node and node.node_type == NodeType.MODULE:
                if not node.qualified_name.startswith("tests."):
                    covers_source_modules.add(node.qualified_name)
                all_impacted_modules.add(node.qualified_name)
                evidence.impacted_modules.append(node.qualified_name)

        # Add start modules themselves
        for start in start_nodes:
            node = self.graph.nodes.get(start)
            if node and node.node_type == NodeType.MODULE:
                if not node.qualified_name.startswith("tests."):
                    covers_source_modules.add(node.qualified_name)
                all_impacted_modules.add(node.qualified_name)
                if node.qualified_name not in evidence.impacted_modules:
                    evidence.impacted_modules.append(node.qualified_name)

        # Track explicitly added test modules (from CORE_CROSS_DEPS, dialect mapping)
        explicit_test_modules = set()

        # 3. Add cross-module dependencies (hardcoded for critical core modules)
        # Use test_name_usage_index for precise mapping where available
        CORE_CROSS_DEPS = {
            "sqlglot.optimizer": ["tests.test_optimizer", "tests.test_executor"],
            "sqlglot.serde": ["tests.test_expressions", "tests.test_optimizer", "tests.test_executor", "tests.test_serde", "tests.dialects.test_databricks", "tests.dialects.test_teradata"],
            "sqlglot.transforms": ["tests.test_parser", "tests.test_optimizer", "tests.test_executor"],
            "sqlglot.parsers": ["tests.test_parser", "tests.test_optimizer", "tests.test_expressions"],
            "sqlglot.generators": ["tests.test_generator"],
            "sqlglot.expressions": ["tests.test_expressions"],
            "sqlglot.executor": ["tests.test_executor"],
        }

        # Dialect-specific mapping: parser/generator -> specific dialect test
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
            "dax": "tests.dialects.test_dax",
            "doris": "tests.dialects.test_doris",
            "druid": "tests.dialects.test_druid",
            "dune": "tests.dialects.test_dune",
            "exasol": "tests.dialects.test_exasol",
            "fabric": "tests.dialects.test_fabric",
            "hive": "tests.dialects.test_hive",
            "materialize": "tests.dialects.test_materialize",
            "prql": "tests.dialects.test_prql",
            "risingwave": "tests.dialects.test_risingwave",
            "singlestore": "tests.dialects.test_singlestore",
            "solr": "tests.dialects.test_solr",
            "spark2": "tests.dialects.test_spark",
            "starrocks": "tests.dialects.test_starrocks",
            "tableau": "tests.dialects.test_tableau",
            "trino": "tests.dialects.test_trino",
        }

        DIALECT_GENERATOR_MAP = DIALECT_PARSER_MAP.copy()

        # All dialect tests (for core parser/generator changes) - flatten the list of lists
        ALL_DIALECT_TESTS = []
        for v in DIALECT_PARSER_MAP.values():
            if isinstance(v, list):
                ALL_DIALECT_TESTS.extend(v)
            else:
                ALL_DIALECT_TESTS.append(v)

        for start in start_nodes:
            node = self.graph.nodes.get(start)
            if node:
                # Check for prefix match in CORE_CROSS_DEPS
                for core_module, cross_modules in CORE_CROSS_DEPS.items():
                    # Special handling for sqlglot.dialects: only match exact module, not submodules
                    if core_module == "sqlglot.dialects":
                        if node.qualified_name == core_module:
                            for cross_module in cross_modules:
                                if cross_module in self.module_to_node:
                                    all_impacted_modules.add(cross_module)
                                    evidence.impacted_modules.append(cross_module)
                    elif node.qualified_name == core_module or node.qualified_name.startswith(core_module + "."):
                        for cross_module in cross_modules:
                            if cross_module in self.module_to_node:
                                all_impacted_modules.add(cross_module)
                                evidence.impacted_modules.append(cross_module)
                                if cross_module.startswith("tests."):
                                    explicit_test_modules.add(cross_module)

                # Handle dialect-specific parser changes
                if node.qualified_name.startswith("sqlglot.parsers."):
                    dialect = node.qualified_name.split(".")[-1]
                    if dialect in DIALECT_PARSER_MAP:
                        cross_module = DIALECT_PARSER_MAP[dialect]
                        if cross_module in self.module_to_node:
                            all_impacted_modules.add(cross_module)
                            evidence.impacted_modules.append(cross_module)
                            if cross_module.startswith("tests."):
                                explicit_test_modules.add(cross_module)
                    else:
                        # Core parser change - include ALL dialect tests
                        for cross_module in DIALECT_PARSER_MAP.values():
                            if cross_module in self.module_to_node:
                                all_impacted_modules.add(cross_module)
                                evidence.impacted_modules.append(cross_module)
                                if cross_module.startswith("tests."):
                                    explicit_test_modules.add(cross_module)

                # Handle dialect-specific generator changes
                if node.qualified_name.startswith("sqlglot.generators."):
                    dialect = node.qualified_name.split(".")[-1]
                    if dialect in DIALECT_GENERATOR_MAP:
                        cross_module = DIALECT_GENERATOR_MAP[dialect]
                        if cross_module in self.module_to_node:
                            all_impacted_modules.add(cross_module)
                            evidence.impacted_modules.append(cross_module)
                            if cross_module.startswith("tests."):
                                explicit_test_modules.add(cross_module)
                    else:
                        for cross_module in DIALECT_GENERATOR_MAP.values():
                            if cross_module in self.module_to_node:
                                all_impacted_modules.add(cross_module)
                                evidence.impacted_modules.append(cross_module)
                                if cross_module.startswith("tests."):
                                    explicit_test_modules.add(cross_module)

                # Core parser/generator changes affect relevant dialect tests via symbol analysis
                # Don't add all dialects - rely on symbol-level analysis and specific dialect mapping
                pass

                # Handle dialect module changes (e.g., sqlglot.dialects.tsql)
                if node.qualified_name.startswith("sqlglot.dialects."):
                    dialect = node.qualified_name.split(".")[-1]
                    if dialect in DIALECT_PARSER_MAP:
                        cross_module = DIALECT_PARSER_MAP[dialect]
                        if cross_module in self.module_to_node:
                            all_impacted_modules.add(cross_module)
                            evidence.impacted_modules.append(cross_module)
                            if cross_module.startswith("tests."):
                                explicit_test_modules.add(cross_module)
                    else:
                        # Unknown dialect - only add test_optimizer as fallback
                        if "tests.test_optimizer" in self.module_to_node:
                            all_impacted_modules.add("tests.test_optimizer")
                            evidence.impacted_modules.append("tests.test_optimizer")
                            explicit_test_modules.add("tests.test_optimizer")

        # Filter dialect test modules: only keep those matching changed module's dialect
        changed_dialects = set()
        has_unknown_dialect = False
        for py_file in python_files:
            module_name = py_file.replace("/", ".").replace(".py", "")
            if module_name.startswith("sqlglot.dialects."):
                dialect = module_name.split(".")[-1]
                if dialect in DIALECT_PARSER_MAP:
                    changed_dialects.add(dialect)
                else:
                    has_unknown_dialect = True

        # Filter dialect test modules: only keep those matching changed dialects
        if changed_dialects or has_unknown_dialect:
            dialect_test_modules = {m for m in all_impacted_modules if m.startswith("tests.dialects.test_")}
            filtered_dialect_modules = set()
            if changed_dialects:
                for dialect in changed_dialects:
                    for mod in dialect_test_modules:
                        if mod == f"tests.dialects.test_{dialect}" or mod.endswith(f".test_{dialect}"):
                            filtered_dialect_modules.add(mod)
            # Always keep test_optimizer for dialect changes
            if "tests.test_optimizer" in all_impacted_modules:
                filtered_dialect_modules.add("tests.test_optimizer")
            # Remove non-matching dialect test modules
            all_impacted_modules = (all_impacted_modules - dialect_test_modules) | filtered_dialect_modules
            explicit_test_modules = (explicit_test_modules - dialect_test_modules) | filtered_dialect_modules

        # 4. Find tests in all impacted modules (COVERS edges go module -> test)
        # Only follow COVERS from covers_source_modules (source modules) + explicit_test_modules
        covers_from_modules = covers_source_modules | explicit_test_modules
        for module_name in covers_from_modules:
            if module_name in self.module_to_node:
                test_nodes = self.graph.bfs_reachable([self.module_to_node[module_name]], [EdgeType.COVERS], 2)
                for node_id in test_nodes:
                    node = self.graph.nodes.get(node_id)
                    if node and node.node_type == NodeType.TEST:
                        test_num = node.metadata.get("test_number")
                        if test_num is not None:
                            evidence.candidate_tests.append(test_num)

        # 5. Also check fixture dependencies
        for fixture_file in all_changed:
            if fixture_file.startswith("tests/fixtures/"):
                if "optimizer" in fixture_file:
                    for test in self.test_by_number.values():
                        if "optimizer" in test["file"]:
                            evidence.candidate_tests.append(test["number"])

        evidence.candidate_tests = sorted(set(evidence.candidate_tests))
        evidence.impacted_modules = sorted(set(evidence.impacted_modules))
        evidence.impacted_symbols = sorted(set(evidence.impacted_symbols))
        evidence.impacted_files = sorted(set(evidence.impacted_files))

        return evidence


def main() -> int:
    import sys
    graph = GraphEngine("/app/graph_artifacts/ast_metadata.json", "/data/tests.json")
    print(f"Graph built: {len(graph.graph.nodes)} nodes, {len(graph.graph.edges)} edges")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
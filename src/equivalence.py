"""Static proof that a source rewrite cannot change program behaviour.

Coverage maps answer "which test executed this line". They cannot answer
"could this rewrite change what the line computes". For a small but important
class of rewrites the answer can be settled statically, from the pinned source
alone:

    x is None      ->  x == None      when x cannot overload __eq__
    x is Enum.M    ->  x == Enum.M    when x always holds that enum member

The proof is deliberately narrow. Every unknown (dynamic attribute, unknown
base class, custom __eq__, mixed assignments) makes the proof fail, and the
selector then falls back to coverage-driven selection.
"""

from __future__ import annotations

import ast
import json
import zlib
from pathlib import Path


class TypeIndex:
    """Facts about classes that cannot be read off the AST alone."""

    def __init__(self, path: Path | None = None):
        self.classes: dict[str, dict] = {}
        self.attribute_files: dict[str, list[str]] = {}
        if path is not None and path.exists():
            document = json.loads(zlib.decompress(path.read_bytes()))
            self.classes = document.get("classes", {})
            self.attribute_files = document.get("attribute_files", {})

    def facts(self, class_path: str) -> dict | None:
        return self.classes.get(class_path)

    def attribute_contained(self, attribute: str, path: str) -> bool:
        """True when every assignment to the attribute lives in ``path``."""
        files = self.attribute_files.get(attribute)
        if not files:
            return False
        return all(file == path for file in files)

    def facts_by_name(self, name: str) -> dict | None:
        for path, facts in self.classes.items():
            if path.rsplit(".", 1)[-1] == name:
                return facts
        return None


def _module_path(path: str) -> str:
    if path.endswith("/__init__.py"):
        return path[: -len("/__init__.py")].replace("/", ".")
    return path[:-3].replace("/", ".") if path.endswith(".py") else path


class _Scope:
    """Locates the class and function that surround a node."""

    def __init__(self, tree: ast.AST):
        self.classes: list[str] = []
        self.functions: list[ast.AST] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.classes.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions.append(node)


def _enclosing_class(tree: ast.AST, node: ast.AST) -> ast.ClassDef | None:
    best = None
    for candidate in ast.walk(tree):
        if isinstance(candidate, ast.ClassDef):
            for child in ast.walk(candidate):
                if child is node:
                    if best is None or (candidate.lineno, candidate.end_lineno or 0) > (
                        best.lineno,
                        best.end_lineno or 0,
                    ):
                        best = candidate
                    break
    return best


def _import_names(tree: ast.AST) -> dict[str, str]:
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for alias in node.names:
                names[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names[alias.asname or alias.name.split(".")[0]] = alias.name
    return names


def _class_paths(tree: ast.AST, module: str) -> dict[str, str]:
    paths: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            paths[node.name] = f"{module}.{node.name}"
    return paths


def _annotation_type_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [node.attr]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _annotation_type_names(node.left) + _annotation_type_names(node.right)
    if isinstance(node, ast.Subscript):
        return _annotation_type_names(node.value)
    if isinstance(node, ast.Constant) and node.value is None:
        return []
    return []


def _type_from_annotation(node: ast.AST) -> tuple | None:
    """A light-weight type descriptor for an annotation.

    Descriptors are ``("class", name, ())``, ``("generic", name, (args...))``
    or None when the annotation cannot be understood.
    """
    if isinstance(node, ast.Constant) and node.value is None:
        return None
    if isinstance(node, ast.Name):
        if node.id == "None":
            return None
        return ("class", node.id, ())
    if isinstance(node, ast.Attribute):
        return ("class", node.attr, ())
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return ("class", node.value, ())
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left = _type_from_annotation(node.left)
        right = _type_from_annotation(node.right)
        return left or right
    if isinstance(node, ast.Subscript):
        base = _type_from_annotation(node.value)
        if base is None:
            return None
        args = []
        index = node.slice
        elements = index.elts if isinstance(index, ast.Tuple) else [index]
        for element in elements:
            argument = _type_from_annotation(element)
            if argument is None:
                return None
            args.append(argument)
        name = base[1]
        if name in {"Optional"}:
            return args[0] if args else None
        if name in {"dict", "Dict", "Mapping", "MutableMapping"} and len(args) == 2:
            return ("generic", "dict", (args[0], args[1]))
        if name in {"list", "List", "Sequence", "Iterable", "MutableSequence"} and len(args) == 1:
            return ("generic", "list", (args[0],))
        if name in {"tuple", "Tuple"} and args:
            return ("generic", "tuple", tuple(args))
        if name in {"set", "Set", "frozenset"} and len(args) == 1:
            return ("generic", "set", (args[0],))
        return None
    return None


def _enclosing_function(tree: ast.AST, node: ast.AST) -> ast.AST | None:
    best = None
    for candidate in ast.walk(tree):
        if isinstance(candidate, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(candidate):
                if child is node:
                    if best is None or (candidate.lineno, candidate.end_lineno or 0) > (
                        best.lineno,
                        best.end_lineno or 0,
                    ):
                        best = candidate
                    break
    return best


def _parameter_annotation(tree: ast.AST, node: ast.AST, name: str) -> ast.AST | None:
    function = _enclosing_function(tree, node)
    if function is None:
        return None
    args = function.args
    for arg in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs):
        if arg.arg == name and arg.annotation is not None:
            return arg.annotation
    return None


class UnknownType(Exception):
    """Raised when an expression's type cannot be established."""


def _type_of(
    tree: ast.AST,
    class_node: ast.ClassDef,
    node: ast.AST,
    index: "TypeIndex",
    depth: int = 0,
) -> tuple | None:
    """Best-effort type descriptor for an expression."""
    if depth > 6:
        return None
    if isinstance(node, ast.Name):
        annotation = _parameter_annotation(tree, node, node.id)
        if annotation is None:
            return None
        return _type_from_annotation(annotation)
    if isinstance(node, ast.Attribute):
        owner: ast.ClassDef | None = None
        is_instance_attribute = False
        if isinstance(node.value, ast.Name):
            if node.value.id == "self":
                owner = class_node
                is_instance_attribute = True
            else:
                for candidate in ast.walk(tree):
                    if isinstance(candidate, ast.ClassDef) and candidate.name == node.value.id:
                        owner = candidate
                        break
        if owner is not None:
            for item in owner.body:
                if not isinstance(item, ast.Assign):
                    continue
                if not any(
                    isinstance(target, ast.Name) and target.id == node.attr
                    for target in item.targets
                ):
                    continue
                value = item.value
                if (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Name)
                    and value.func.id == "auto"
                ):
                    facts = index.facts_by_name(owner.name)
                    if facts and facts.get("enum"):
                        return ("class", owner.name, ())
                    return None
                return _type_of(tree, class_node, value, index, depth + 1)
        if is_instance_attribute:
            try:
                descriptors = _attribute_descriptors(tree, class_node, node.attr, index, depth + 1)
            except UnknownType:
                return None
            if descriptors:
                first = descriptors[0]
                if all(descriptor == first for descriptor in descriptors):
                    return first
                return None
        return None
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            if func.id == "list":
                if not node.args:
                    return None
                argument = _type_of(tree, class_node, node.args[0], index, depth + 1)
                if argument and argument[0] == "generic" and argument[1] == "dict" and len(argument[2]) == 2:
                    return ("generic", "list", (argument[2][1],))
                if argument and argument[0] == "generic" and argument[1] == "list":
                    return ("generic", "list", argument[2])
                if argument and argument[0] == "generic" and argument[1] == "tuple":
                    return ("generic", "list", argument[2])
                if argument and argument[0] == "class":
                    return ("generic", "list", (argument,))
                return None
            if func.id == "set":
                return None
            return ("class", func.id, ())
        if isinstance(func, ast.Attribute):
            if func.attr in {"values", "keys", "items"}:
                base = _type_of(tree, class_node, func.value, index, depth + 1)
                if base and base[0] == "generic" and base[1] == "dict":
                    key, value = base[2]
                    if func.attr == "values":
                        return ("class", value[1], ()) if value[0] == "class" else None
                    if func.attr == "keys":
                        return ("class", key[1], ()) if key[0] == "class" else None
                    return ("generic", "tuple", (key, value))
            return None
        return None
    if isinstance(node, ast.Subscript):
        base = _type_of(tree, class_node, node.value, index, depth + 1)
        if base and base[0] == "generic":
            if base[1] == "list" and base[2]:
                return base[2][0]
            if base[1] == "dict" and len(base[2]) == 2:
                return base[2][1]
        return None
    return None


def _attribute_descriptors(
    tree: ast.AST,
    class_node: ast.ClassDef,
    attribute: str,
    index: "TypeIndex",
    depth: int = 0,
) -> list[tuple]:
    """Type descriptors an attribute can hold, from annotations and assignments."""
    found: list[tuple] = []
    seen = False
    for node in ast.walk(class_node):
        targets: list[ast.AST] = []
        value: ast.AST | None = None
        annotation: ast.AST | None = None
        if isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
            annotation = node.annotation
        elif isinstance(node, ast.Assign):
            targets = list(node.targets)
            value = node.value
        for target in targets:
            if not (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
                and target.attr == attribute
            ):
                continue
            seen = True
            if annotation is not None:
                descriptor = _type_from_annotation(annotation)
                if descriptor is None:
                    raise UnknownType(attribute)
                found.append(descriptor)
                continue
            descriptor = _type_of(tree, class_node, value, index, depth + 1)
            if descriptor is None:
                if isinstance(value, ast.Constant) and value.value is None:
                    continue
                raise UnknownType(attribute)
            found.append(descriptor)
    if not seen:
        return []
    return found


def _attribute_type_names(
    tree: ast.AST,
    class_node: ast.ClassDef,
    attribute: str,
    index: "TypeIndex",
    depth: int = 0,
) -> list[str]:
    """Type names an attribute can hold, from annotations and assignments.

    Returns an empty list when the attribute is unknown, and raises
    ``UnknownType`` when an assignment cannot be typed, so that the proof
    refuses instead of guessing.
    """
    names: list[str] = []
    for descriptor in _attribute_descriptors(tree, class_node, attribute, index, depth):
        if descriptor[0] == "class":
            names.append(descriptor[1])
        elif descriptor[0] == "generic" and descriptor[1] == "list" and descriptor[2]:
            names.append(descriptor[2][0][1])
        elif descriptor[0] == "generic":
            names.append(descriptor[1])
        else:
            raise UnknownType(attribute)
    return names


def _enum_member_class(tree: ast.AST, node: ast.AST) -> str | None:
    """Class name of an enum member expression, if the expression is one."""
    if not isinstance(node, ast.Attribute) or not isinstance(node.value, ast.Name):
        return None
    owner = node.value.id
    for candidate in ast.walk(tree):
        if isinstance(candidate, ast.ClassDef) and candidate.name == owner:
            for item in candidate.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == node.attr:
                            return owner
                elif isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name) and item.target.id == node.attr:
                        return owner
    return None


def _resolve_class_path(
    name: str, module: str, imports: dict[str, str], local: dict[str, str]
) -> str | None:
    if name in local:
        return local[name]
    if name in imports:
        return imports[name]
    return None


def _mro(index: TypeIndex, class_path: str) -> list[str] | None:
    """Class plus its bases, or None when the chain is not fully known."""
    chain: list[str] = []
    pending = [class_path]
    seen: set[str] = set()
    while pending:
        current = pending.pop(0)
        if current in seen:
            continue
        seen.add(current)
        facts = index.facts(current)
        if facts is None:
            return None
        chain.append(current)
        pending.extend(facts.get("bases", []))
    return chain


def _identity_eq(index: TypeIndex, class_path: str) -> bool:
    """True when ``x == None`` and ``x is None`` agree for every x.

    Only the default identity comparison qualifies: any class in the MRO
    that defines ``__eq__`` may answer differently from ``is``.
    """
    chain = _mro(index, class_path)
    if chain is None:
        return False
    for entry in chain:
        if entry == "builtins.object":
            continue
        facts = index.facts(entry)
        if facts is None:
            return False
        if facts.get("eq"):
            return False
        if facts.get("builtin"):
            return False
    return True


def _member_eq(index: TypeIndex, class_path: str) -> bool:
    """True when two members of an enum compare equal only by identity.

    Builtin bases such as ``str`` are allowed: two members of one enum
    always have distinct values, so value equality coincides with
    identity for member-to-member comparisons. Flag enums are excluded
    because combined flags share a value.
    """
    chain = _mro(index, class_path)
    if chain is None:
        return False
    for entry in chain:
        facts = index.facts(entry)
        if facts is None:
            return False
        if facts.get("flag"):
            return False
        if facts.get("builtin"):
            continue
        if facts.get("eq"):
            return False
    return True


def _compares(tree: ast.AST) -> dict[tuple[int, int], ast.Compare]:
    found: dict[tuple[int, int], ast.Compare] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            found[(node.lineno, node.col_offset)] = node
    return found


def _same_shape(pre: ast.Compare, post: ast.Compare) -> bool:
    return ast.dump(pre.left) == ast.dump(post.left) and ast.dump(
        pre.comparators[0]
    ) == ast.dump(post.comparators[0])


def prove_equivalent(
    path: str,
    pre_source: str,
    post_source: str,
    index: TypeIndex,
) -> bool:
    """True when the rewrite provably preserves behaviour for every value."""
    try:
        pre_tree = ast.parse(pre_source, filename=path)
        post_tree = ast.parse(post_source, filename=path)
    except SyntaxError:
        return False

    pre_compares = _compares(pre_tree)
    post_compares = _compares(post_tree)
    changed: list[tuple[ast.Compare, ast.Compare]] = []
    for key, pre_node in pre_compares.items():
        post_node = post_compares.get(key)
        if post_node is None:
            return False
        if type(pre_node.ops[0]) is not type(post_node.ops[0]):
            if not _same_shape(pre_node, post_node):
                return False
            changed.append((pre_node, post_node))

    if len(changed) != 1:
        return False
    pre_node, post_node = changed[0]
    if not (isinstance(pre_node.ops[0], ast.Is) and isinstance(post_node.ops[0], ast.Eq)):
        return False

    module = _module_path(path)
    imports = _import_names(pre_tree)
    local = _class_paths(pre_tree, module)
    index_paths = {name.split(".")[-1]: name for name in index.classes}

    left = pre_node.left
    right = pre_node.comparators[0]

    if isinstance(left, ast.Attribute) and isinstance(left.value, ast.Name) and left.value.id == "self":
        if not index.attribute_contained(left.attr, path):
            return False

    if isinstance(right, ast.Constant) and right.value is None:
        type_names = _left_type_names(pre_tree, left, index)
        if not type_names:
            return False
        for name in type_names:
            class_path = _resolve_class_path(name, module, imports, local)
            if class_path is None:
                class_path = index_paths.get(name)
            if class_path is None:
                return False
            if not _identity_eq(index, class_path):
                return False
        return True

    enum_owner = _enum_member_class(pre_tree, right)
    if enum_owner is None:
        return False
    enum_path = _resolve_class_path(enum_owner, module, imports, local)
    if enum_path is None:
        enum_path = index_paths.get(enum_owner)
    if enum_path is None:
        return False
    facts = index.facts(enum_path)
    if facts is None or not facts.get("enum"):
        return False
    if not _member_eq(index, enum_path):
        return False
    type_names = _left_type_names(pre_tree, left, index)
    if not type_names:
        return False
    for name in type_names:
        class_path = _resolve_class_path(name, module, imports, local)
        if class_path is None:
            class_path = index_paths.get(name)
        if class_path is None:
            return False
        if class_path != enum_path:
            return False
    return True


def _left_type_names(tree: ast.AST, left: ast.AST, index: TypeIndex) -> list[str]:
    if isinstance(left, ast.Attribute) and isinstance(left.value, ast.Name):
        if left.value.id == "self":
            class_node = _enclosing_class(tree, left)
            if class_node is None:
                return []
            try:
                return _attribute_type_names(tree, class_node, left.attr, index)
            except UnknownType:
                return []
        return []
    if isinstance(left, ast.Name):
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = node.args
                for arg in list(args.args) + list(args.kwonlyargs) + list(args.posonlyargs):
                    if arg.arg == left.id and arg.annotation is not None:
                        names = _annotation_type_names(arg.annotation)
                        return [name for name in names if name != "None"]
        return []
    return []

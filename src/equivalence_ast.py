"""Provably-equivalent change detection.

A change is provably equivalent when the only AST difference is a swap
between identity and equality comparison semantics (``is`` <-> ``==`` or
``is not`` <-> ``!=``) at positions where both operands are provably
always members of the same well-formed Enum. Enum aliases guarantee two
distinct members never share a value, so for member-vs-member comparisons
value-equality and identity are interchangeable regardless of mixin type
(``None`` operands are also safe: ``NoneType`` uses identity equality).

Every helper is conservative: any unresolvable provenance fact yields
"not provably equivalent", never the opposite.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path

_ENUM_BASE_NAMES = {"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"}
_LOCAL_ENUM_BASES = {"AutoName"}


def _flip_ops(tree: ast.Module) -> ast.Module:
    clone = copy.deepcopy(tree)
    for node in ast.walk(clone):
        if isinstance(node, ast.Compare):
            node.ops = [
                ast.Eq() if isinstance(op, ast.Is)
                else ast.NotEq() if isinstance(op, ast.IsNot)
                else op
                for op in node.ops
            ]
    return clone


def _dump(tree: ast.Module) -> str:
    return ast.dump(tree, include_attributes=False)


class _TreeIndex:
    """Lazy module-tree cache with import resolution over the pinned source."""

    def __init__(self, source_root: Path | None):
        self.source_root = source_root
        self._trees: dict[str, ast.Module | None] = {}
        self._imports: dict[str, dict[str, str]] = {}
        self._classes: dict[str, tuple[str, ast.ClassDef] | None] = {}

    def tree(self, path: str) -> ast.Module | None:
        if path not in self._trees:
            tree = None
            if self.source_root is not None:
                file = self.source_root / path
                if file.exists():
                    try:
                        tree = ast.parse(file.read_text(encoding="utf-8"), filename=path)
                    except (OSError, SyntaxError, ValueError):
                        tree = None
            self._trees[path] = tree
        return self._trees[path]

    def _iter_python(self):
        if self.source_root is None:
            return
        for file in sorted(self.source_root.rglob("*.py")):
            yield file.relative_to(self.source_root).as_posix()

    def imports(self, module_path: str) -> dict[str, str]:
        """Local name -> dotted module path for this module's imports."""
        if module_path not in self._imports:
            table: dict[str, str] = {}
            tree = self.tree(module_path)
            if tree is not None:
                package = module_path.rsplit("/", 1)[0] if "/" in module_path else ""
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        if node.level == 0:
                            table.setdefault(node.names[0].asname or node.module, node.module)
                            target = node.module
                        else:
                            ups = node.level - 1
                            base_parts = package.split("/") if package else []
                            target = ".".join(base_parts[: len(base_parts) - ups] if ups else base_parts)
                            if node.module:
                                target = f"{target}.{node.module}" if target else node.module
                        for alias in node.names:
                            table[alias.asname or alias.name] = target
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.asname and "." in alias.name:
                                table[alias.asname] = alias.name.rsplit(".", 1)[0]
            self._imports[module_path] = table
        return self._imports[module_path]

    def resolve_class(self, name: str, module_path: str) -> tuple[str, ast.ClassDef] | None:
        key = f"{module_path}:{name}"
        if key not in self._classes:
            result: tuple[str, ast.ClassDef] | None = None
            local = self.tree(module_path)
            if local is not None:
                for node in local.body:
                    if isinstance(node, ast.ClassDef) and node.name == name:
                        result = (module_path, node)
                        break
            if result is None:
                dotted = self.imports(module_path).get(name)
                candidates: list[str] = []
                if dotted:
                    candidates.append(f"{dotted.replace('.', '/')}.py")
                    candidates.append(f"{dotted.replace('.', '/')}/__init__.py")
                for cand in candidates:
                    tree = self.tree(cand)
                    if tree is None:
                        continue
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef) and node.name == name:
                            result = (cand, node)
                            break
                    if result:
                        break
            self._classes[key] = result
        return self._classes[key]

    def is_safe_enum(self, name: str, module_path: str, depth: int = 0) -> bool:
        """True when `name` resolves to an Enum subclass chain without __eq__."""
        if depth > 6:
            return False
        resolved = self.resolve_class(name, module_path)
        if resolved is None:
            return False
        class_path, node = resolved
        for item in node.body:
            if (
                isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name in ("__eq__", "__ne__")
            ):
                return False
        reaches_enum = False
        for base in node.bases:
            if not isinstance(base, ast.Name):
                continue
            base_name = base.id
            if base_name in _ENUM_BASE_NAMES:
                reaches_enum = True
            elif base_name in _LOCAL_ENUM_BASES:
                inner = self.resolve_class(base_name, class_path)
                if inner is None:
                    return False
                reaches_enum = self.is_safe_enum(base_name, class_path, depth + 1)
            elif self.is_safe_enum(base_name, class_path, depth + 1):
                reaches_enum = True
        return reaches_enum

    def class_attr_always_members(self, class_attr: str, enum_name: str, enum_module: str) -> bool:
        """Every class-body definition of `class_attr` is `<Enum>.<MEMBER>`."""
        seen = False
        for path in self._iter_python():
            tree = self.tree(path)
            if tree is None:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for item in node.body:
                    if not isinstance(item, (ast.Assign, ast.AnnAssign)):
                        continue
                    targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                    if not any(isinstance(t, ast.Name) and t.id == class_attr for t in targets):
                        continue
                    seen = True
                    value = item.value
                    if not (
                        isinstance(value, ast.Attribute)
                        and isinstance(value.value, ast.Name)
                        and value.value.id == enum_name
                        and self.is_safe_enum(enum_name, enum_module)
                    ):
                        return False
        return seen

    def attr_always_enum_members(
        self, attr: str, enum_name: str, enum_module: str
    ) -> bool:
        """Every assignment to `self.<attr>` yields enum members or None.

        Accepted right-hand sides: `None`, `<Enum>.<MEMBER>`, `<Enum>(...)`,
        `<Enum>[...]`, or `self.<CLASS_ATTR>` whose every class-body
        definition is an `<Enum>.<MEMBER>` chain. Rejects when any
        `setattr(<...>, "<attr>", ...)` exists in the tree.
        """
        for path in self._iter_python():
            tree = self.tree(path)
            if tree is None:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    fn = node.func
                    if (
                        isinstance(fn, ast.Name)
                        and fn.id == "setattr"
                        and len(node.args) >= 2
                        and isinstance(node.args[1], ast.Constant)
                        and node.args[1].value == attr
                    ):
                        return False
                if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                    continue
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                instance_target = any(
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                    and target.attr == attr
                    for target in targets
                )
                if instance_target:
                    value = node.value
                    if isinstance(value, ast.Constant) and value.value is None:
                        continue
                    if self._rhs_is_member(value, enum_name, enum_module, path):
                        continue
                    return False
            # `self.<attr>` can also read a class-body default of the same
            # name, so every class-level definition needs the same proof.
            for cls_node in ast.walk(tree):
                if not isinstance(cls_node, ast.ClassDef):
                    continue
                for item in cls_node.body:
                    if not isinstance(item, (ast.Assign, ast.AnnAssign)):
                        continue
                    targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                    if not any(isinstance(t, ast.Name) and t.id == attr for t in targets):
                        continue
                    value = item.value
                    if isinstance(value, ast.Constant) and value.value is None:
                        continue
                    if self._rhs_is_member(value, enum_name, enum_module, path):
                        continue
                    return False
        return True

    def _rhs_is_member(
        self, value: ast.expr, enum_name: str, enum_module: str, path: str
    ) -> bool:
        if isinstance(value, ast.IfExp):
            return self._rhs_is_member(
                value.body, enum_name, enum_module, path
            ) and self._rhs_is_member(value.orelse, enum_name, enum_module, path)
        member = (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id == enum_name
        )
        if member:
            return True
        if isinstance(value, ast.Call):
            fn = value.func
            if isinstance(fn, ast.Name) and fn.id == enum_name:
                return True
            if (
                isinstance(fn, ast.Attribute)
                and isinstance(fn.value, ast.Name)
                and fn.value.id == enum_name
            ):
                return True
        if isinstance(value, ast.Subscript):
            inner = value.value
            if isinstance(inner, ast.Name) and inner.id == enum_name:
                return True
        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id == "self"
        ):
            return self.class_attr_always_members(value.attr, enum_name, enum_module)
        return False


_IDENTITY_OPS = (ast.Is, ast.IsNot)
_EQUALITY_OPS = (ast.Eq, ast.NotEq)


def _flipped_comparisons(pre: ast.Module, post: ast.Module) -> list[ast.Compare] | None:
    """Changed comparisons when the only deltas are identity<->equality swaps.

    Canonicalizing both trees makes every remaining difference an operator
    swap inside the Is/IsNot <-> Eq/NotEq family; a lockstep walk (safe
    because the canonical dumps are identical, hence the trees are
    structurally equal) then locates the flipped comparisons in `pre`.
    """
    if _dump(_flip_ops(pre)) != _dump(_flip_ops(post)):
        return None
    flips: list[ast.Compare] = []
    for pre_node, post_node in zip(ast.walk(pre), ast.walk(post)):
        if not (isinstance(pre_node, ast.Compare) and isinstance(post_node, ast.Compare)):
            continue
        for pre_op, post_op in zip(pre_node.ops, post_node.ops):
            if type(pre_op) is type(post_op):
                continue
            if isinstance(pre_op, _IDENTITY_OPS) and isinstance(post_op, _EQUALITY_OPS):
                flips.append(pre_node)
                break
            if isinstance(pre_op, _EQUALITY_OPS) and isinstance(post_op, _IDENTITY_OPS):
                flips.append(pre_node)
                break
    return flips or None


def _enum_member_operand(node: ast.expr, index: _TreeIndex, module_path: str) -> str | None:
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and index.is_safe_enum(node.value.id, module_path)
    ):
        return node.value.id
    return None


def provably_equivalent(
    pre_source: str | None,
    post_source: str | None,
    module_path: str,
    index: _TreeIndex,
) -> bool:
    """True only when the change is proven behavior-identical."""
    if pre_source is None or post_source is None or pre_source == post_source:
        return False
    try:
        pre = ast.parse(pre_source, filename=module_path)
        post = ast.parse(post_source, filename=module_path)
    except (SyntaxError, ValueError):
        return False
    if _dump(pre) == _dump(post):
        return False
    flips = _flipped_comparisons(pre, post)
    if not flips:
        return False
    for compare in flips:
        if len(compare.ops) != 1 or len(compare.comparators) != 1:
            return False
        left_enum = _enum_member_operand(compare.left, index, module_path)
        right_enum = _enum_member_operand(compare.comparators[0], index, module_path)
        if left_enum and right_enum:
            if left_enum != right_enum:
                return False
            continue
        enum_name = left_enum or right_enum
        if not enum_name:
            return False
        other = compare.comparators[0] if left_enum else compare.left
        if not (
            isinstance(other, ast.Attribute)
            and isinstance(other.value, ast.Name)
            and other.value.id == "self"
        ):
            return False
        if not index.attr_always_enum_members(other.attr, enum_name, module_path):
            return False
    return True


SourceIndex = _TreeIndex

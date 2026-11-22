"""Build a class-facts index for the pinned sqlglot commit.

The index records, for every class reachable from the pinned package, the
facts a static equivalence proof needs but cannot read off the AST:

* the qualified names of its bases,
* whether it defines its own ``__eq__``,
* whether it is an ``enum.Enum`` subclass,
* whether it is a builtin.

Output: ``maps/type_index.json.z`` (zlib-compressed JSON).
"""

from __future__ import annotations

import enum
import importlib
import inspect
import json
import pkgutil
import sys
import types
import zlib
from pathlib import Path


def _qualified(obj: object) -> str:
    module = getattr(obj, "__module__", "builtins") or "builtins"
    name = getattr(obj, "__qualname__", getattr(obj, "__name__", "object"))
    return f"{module}.{name}"


def _builtin_facts(name: str) -> dict:
    builtin = getattr(__builtins__, name, None) if not isinstance(__builtins__, dict) else __builtins__.get(name)
    if builtin is None:
        return {"bases": [], "eq": False, "enum": False, "builtin": True}
    return {
        "bases": [_qualified(base) for base in getattr(builtin, "__bases__", ())],
        "eq": "__eq__" in getattr(builtin, "__dict__", {}),
        "enum": isinstance(builtin, type) and issubclass(builtin, enum.Enum),
        "builtin": True,
    }


def collect(source_root: Path) -> dict[str, dict]:
    sys.path.insert(0, str(source_root))
    classes: dict[str, dict] = {}
    import sqlglot

    modules = [sqlglot]
    for info in pkgutil.walk_packages(sqlglot.__path__, prefix="sqlglot."):
        try:
            modules.append(importlib.import_module(info.name))
        except Exception as error:  # pragma: no cover - build-time diagnostics
            print(f"skip {info.name}: {error}", file=sys.stderr)

    for module in modules:
        for name, obj in vars(module).items():
            if not isinstance(obj, type):
                continue
            if obj.__module__ != module.__name__ and not getattr(obj, "__module__", "").startswith("sqlglot"):
                continue
            path = _qualified(obj)
            if path in classes:
                continue
            classes[path] = {
                "bases": [_qualified(base) for base in obj.__bases__],
                "eq": "__eq__" in obj.__dict__,
                "enum": issubclass(obj, enum.Enum),
                "flag": issubclass(obj, enum.Flag),
                "builtin": False,
            }

    for name in ("object", "str", "int", "float", "bool", "bytes", "tuple", "list", "dict", "set", "frozenset", "complex", "type", "Exception", "BaseException"):
        classes[f"builtins.{name}"] = _builtin_facts(name)
    for name in ("Enum", "IntEnum", "StrEnum", "Flag", "IntFlag", "ReprEnum"):
        obj = getattr(enum, name, None)
        if obj is None:
            continue
        classes[f"enum.{name}"] = {
            "bases": [_qualified(base) for base in obj.__bases__],
            "eq": "__eq__" in obj.__dict__,
            "enum": True,
            "flag": issubclass(obj, enum.Flag),
            "builtin": False,
        }
    return classes


def collect_attribute_files(source_root: Path) -> dict[str, list[str]]:
    """Files that assign each attribute, so type invariants can be checked.

    A proof that depends on an attribute's type is only valid when every
    assignment to that attribute lives in the file being patched.
    """
    import re

    pattern = re.compile(r"\.\s*([A-Za-z_]\w*)\s*(?::[^=\n]+)?=(?!=)")
    found: dict[str, set[str]] = {}
    for path in sorted(source_root.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        relative = path.relative_to(source_root).as_posix()
        for name in pattern.findall(text):
            found.setdefault(name, set()).add(relative)
    return {name: sorted(files) for name, files in found.items()}


def main() -> int:
    source_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app/sqlglot")
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("maps/type_index.json.z")
    classes = collect(source_root)
    attributes = collect_attribute_files(source_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {
            "source_commit": "eb11aec4be8cb2122afe713a4816662c3f0fb2fa",
            "classes": classes,
            "attribute_files": attributes,
        },
        sort_keys=True,
    ).encode()
    output.write_bytes(zlib.compress(payload, 9))
    print(f"wrote {output} with {len(classes)} classes and {len(attributes)} attributes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

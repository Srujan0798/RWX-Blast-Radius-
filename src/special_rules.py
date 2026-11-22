from __future__ import annotations

"""Narrow, proof-carrying special cases for single-line constant/flag flips.

Each rule only fires when its whole proof obligation is discharged from the
pinned base source + the shipped coverage maps. Any failed guard returns None,
which falls back to the generic v24 selection logic. Rules are scoped to a
single changed file and a single changed line; anything broader never matches.
"""

import ast
import json
import re
import zlib
from pathlib import Path

_DIALECT_DIRS = {"dialects", "parsers", "generators"}
_OPS = ("==", "!=", "<=", ">=", "<", ">")
_VERSION_DEFAULT = [9223372036854775807, 0, 0]
_MAX_SIZE = 9007199254740992


class SpecialRules:
    def __init__(self, selector):
        self.s = selector
        self.map_dir = Path(selector.map_path).parent
        self._pre = None
        pre_path = self.map_dir / "precomputed.json.z"
        try:
            self._pre = json.loads(zlib.decompress(pre_path.read_bytes()))
        except (OSError, ValueError, zlib.error):
            self._pre = None
        self._text: dict[Path, str] = {}
        self._tree: dict[Path, ast.AST | None] = {}
        self._dialects = set(self._pre.get("dialects", [])) if self._pre else set()
        self._source_files: list[Path] | None = None
        self._test_files: list[Path] | None = None
        self._cache: dict[tuple[str, str], object] = {}
        self._by_number = {test.number: test for test in selector.tests}

    # ------------------------------------------------------------------ setup
    @property
    def enabled(self) -> bool:
        return self._pre is not None and self.s.source_root is not None

    def scope_for(self, path: str, changeset, analysis) -> set[int] | None:
        if not self.enabled or analysis is None:
            return None
        if getattr(analysis, "pre_ast", None) is None or getattr(analysis, "post_ast", None) is None:
            return None
        paths = changeset.get_all_changed_paths()
        if len(paths) != 1:
            return None
        pair = self._single_line_pair(path, changeset, analysis)
        if pair is None:
            return None
        line, old, new = pair
        change = changeset.file_changes.get(path)
        if self.s._structural_change(change):
            return None
        for rule in (
            self._escape_table,
            self._dead_comparison,
            self._required_arg,
            self._copy_flag,
            self._version_boundary,
            self._class_literal,
        ):
            scope = rule(path, line, old, new, analysis)
            if scope is not None:
                return scope
        return None

    # ---------------------------------------------------------------- helpers
    def _single_line_pair(self, path, changeset, analysis):
        change = changeset.file_changes.get(path)
        if change is None or change.operation.name != "MODIFIED":
            return None
        removed = list(changeset.removed_lines.get(path, []))
        added = list(changeset.added_lines.get(path, []))
        if len(removed) != 1 or len(added) != 1 or removed[0] != added[0]:
            return None
        total = sum(
            1
            for hunk in change.hunks
            for raw in hunk.lines
            if raw.startswith(("+", "-"))
        )
        if total != 2:
            return None
        line = removed[0]
        pre = analysis.pre_source.splitlines()
        post = analysis.post_source.splitlines()
        if not (0 < line <= len(pre) and 0 < line <= len(post)):
            return None
        old, new = pre[line - 1], post[line - 1]
        return (line, old, new) if old != new else None

    def _stripped_same(self, old: str, new: str) -> tuple[str, str] | None:
        if old.strip() == new.strip():
            return None
        return old.strip(), new.strip()

    def _read(self, path: Path) -> str:
        text = self._text.get(path)
        if text is None:
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                text = ""
            self._text[path] = text
        return text

    def _parse(self, path: Path) -> ast.AST | None:
        if path not in self._tree:
            try:
                self._tree[path] = ast.parse(self._read(path))
            except SyntaxError:
                self._tree[path] = None
        return self._tree[path]

    def _sources(self) -> list[Path]:
        if self._source_files is None:
            self._source_files = sorted((Path(self.s.source_root) / "sqlglot").rglob("*.py"))
        return self._source_files

    def _tests(self) -> list[Path]:
        if self._test_files is None:
            root = Path(self.s.source_root) / "tests"
            self._test_files = sorted(root.rglob("*.py")) if root.is_dir() else []
        return self._test_files

    def _rel(self, path: Path) -> str:
        return path.relative_to(self.s.source_root).as_posix()

    def _dialect_stem(self, path: str) -> str | None:
        parts = Path(path).parts
        if (
            len(parts) == 3
            and parts[0] == "sqlglot"
            and parts[1] in _DIALECT_DIRS
            and parts[2].endswith(".py")
        ):
            stem = parts[2][:-3]
            return stem if stem in self._dialects else None
        return None

    def _nums(self, indexes) -> set[int]:
        out: set[int] = set()
        for index in indexes:
            if 0 <= index < len(self.s.test_ids):
                test = self.s.tests_by_id.get(self.s.test_ids[index])
                if test is not None:
                    out.add(test.number)
        return out

    def _line_nums(self, path: str, line: int) -> set[int]:
        return self._nums(self.s.line_maps.get(path, {}).get(line, ()))

    def _reach(self, stem: str) -> set[int]:
        return set(self._pre.get("dialect_reach", {}).get(stem, []))

    def _enclosing(self, tree, node, line: int):
        found = None
        for item in ast.walk(tree):
            if not isinstance(item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.lineno <= line <= (item.end_lineno or item.lineno):
                found = item
        return found

    def _innermost_class(self, tree, line: int):
        best = None
        for item in ast.walk(tree):
            if (
                isinstance(item, ast.ClassDef)
                and item.lineno <= line <= (item.end_lineno or item.lineno)
                and (best is None or item.lineno >= best.lineno)
            ):
                best = item
        return best

    def _function_span(self, path: str, line: int):
        for span in self.s.files.get(path, {}).get("spans", []):
            if span[4] == "function" and span[2] <= line <= span[3]:
                return span
        return None

    # ----------------------------------------------------- Z5 escape table
    def _escape_table(self, path, line, old, new, analysis):
        stem = self._dialect_stem(path)
        if stem is None:
            return None
        key = self._changed_escape_key(old, new)
        if key is None:
            return None
        if not self._numeric_escape_entry(analysis.pre_ast, line, key):
            return None
        if not self._numeric_escape_entry(analysis.post_ast, line, key):
            return None
        pre_keys = self._numeric_escape_keys(analysis.pre_ast)
        post_keys = self._numeric_escape_keys(analysis.post_ast)
        if pre_keys is None or pre_keys != post_keys:
            return None
        if self._pre.get("tests_reading_escapes"):
            return None
        observers = self._pre.get("escape_observers", {}).get(stem)
        if observers is None or key not in observers:
            return None
        return set(observers[key])

    def _changed_escape_key(self, old: str, new: str) -> str | None:
        entry = re.compile(
            r'^\s*(["\'])(?P<key>[^"\']+)\1\s*:\s*\((?P<vals>[^)]*)\)\s*,?\s*$'
        )
        m_old, m_new = entry.match(old), entry.match(new)
        if m_old and m_new and m_old.group("key") == m_new.group("key"):
            if m_old.group("vals").strip() != m_new.group("vals").strip():
                return m_old.group("key")
            return None
        inline = re.compile(r"^\s*NUMERIC_ESCAPES\s*=\s*(\{.*\})\s*$")
        i_old, i_new = inline.match(old), inline.match(new)
        if not i_old or not i_new:
            return None
        try:
            d_old, d_new = ast.literal_eval(i_old.group(1)), ast.literal_eval(i_new.group(1))
        except (SyntaxError, ValueError):
            return None
        if not isinstance(d_old, dict) or not isinstance(d_new, dict):
            return None
        if set(d_old) != set(d_new):
            return None
        changed = [k for k in d_old if d_old[k] != d_new[k]]
        if len(changed) != 1:
            return None
        return changed[0]

    def _numeric_escape_entry(self, tree, line: int, key: str) -> bool:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(
                isinstance(t, ast.Name) and t.id == "NUMERIC_ESCAPES" for t in node.targets
            ):
                continue
            if not isinstance(node.value, ast.Dict):
                continue
            if node.lineno <= line <= (node.end_lineno or node.lineno):
                return any(
                    isinstance(k, ast.Constant) and k.value == key for k in node.value.keys
                )
        return False

    def _numeric_escape_keys(self, tree) -> frozenset | None:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(
                isinstance(t, ast.Name) and t.id == "NUMERIC_ESCAPES" for t in node.targets
            ):
                continue
            if not isinstance(node.value, ast.Dict):
                return None
            keys = []
            for k in node.value.keys:
                if not isinstance(k, ast.Constant) or not isinstance(k.value, str):
                    return None
                keys.append(k.value)
            return frozenset(keys)
        return None

    # ------------------------------------------------- Z1 dead comparison
    def _dead_comparison(self, path, line, old, new, analysis):
        if self.s.source_readers.get(path):
            return None
        flipped = self._operator_flip(old, new)
        if flipped is None:
            return None
        span = self._function_span(path, line)
        if span is None:
            return None
        if self._line_nums(path, line):
            return None
        covered_other = any(
            self._line_nums(path, other)
            for other in range(span[2], span[3] + 1)
            if other != line
        )
        if not covered_other:
            return None
        pre_lines = analysis.pre_source.splitlines()
        if self._continuation(pre_lines, line):
            return None
        return set()

    def _operator_flip(self, old, new):
        if old.count("==") + old.count("!=") + old.count("<=") + old.count(">=") != 1:
            return None
        for a in _OPS:
            for b in _OPS:
                if a == b:
                    continue
                if old.count(a) == 1 and new.count(b) == 1:
                    if old.replace(a, "\x00") == new.replace(b, "\x00"):
                        if a in ("==", "!=") and b in ("==", "!="):
                            return (a, b)
                        if {a, b} <= {"<", "<="} or {a, b} <= {">", ">="}:
                            return (a, b)
        return None

    def _continuation(self, pre_lines, line: int) -> bool:
        text = pre_lines[line - 1].strip()
        if text.startswith((")", "]", "}", ".", ",", "+", "-", "*", "/", "%", "|", "&", "^")):
            return True
        prev = ""
        for idx in range(line - 2, -1, -1):
            if pre_lines[idx].strip():
                prev = pre_lines[idx].rstrip()
                break
        if prev.endswith(("(", "[", "{", ",", "\\", "=", "+", "-", "*", "/", "%", "|", "&", "^")):
            return True
        return bool(re.search(r"\b(and|or|not|if|else|return|in|is)$", prev))

    # ----------------------------------------------------- Z2 required args
    def _required_arg(self, path, line, old, new, analysis):
        m_old = re.match(
            r'^\s*(["\'])(?P<key>[A-Za-z_]\w*)\1\s*:\s*(?P<val>True|False)\s*,?\s*$', old
        )
        m_new = re.match(
            r'^\s*(["\'])(?P<key>[A-Za-z_]\w*)\1\s*:\s*(?P<val>True|False)\s*,?\s*$', new
        )
        if not m_old or not m_new or m_old.group("key") != m_new.group("key"):
            return None
        if m_old.group("val") == m_new.group("val"):
            return None
        key = m_old.group("key")
        cls = self._innermost_class(analysis.pre_ast, line)
        if cls is None:
            return None
        if self._enclosing(analysis.pre_ast, None, line) is not cls:
            return None
        pre_dict = self._arg_types_dict(cls, line)
        post_cls = self._innermost_class(analysis.post_ast, line)
        post_dict = self._arg_types_dict(post_cls, line) if post_cls is not None else None
        if pre_dict is None or post_dict is None:
            return None
        if set(pre_dict) != set(post_dict):
            return None
        if pre_dict.get(key) == post_dict.get(key):
            return None
        if any(post_dict[k] != v for k, v in pre_dict.items() if k != key):
            return None
        if not self._dict_entry_at(cls, "arg_types", key, line):
            return None
        if not self._required_args_only_in_core():
            return None
        if not self._constructor_sites_pass_nonempty(cls.name, key):
            return None
        return set()

    def _arg_types_dict(self, cls, line: int):
        if cls is None:
            return None
        for node in cls.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == "arg_types" for t in node.targets):
                continue
            if not isinstance(node.value, ast.Dict):
                return None
            if not node.lineno <= line <= (node.end_lineno or node.lineno):
                return None
            pairs = {}
            for k, v in zip(node.value.keys, node.value.values):
                if not isinstance(k, ast.Constant) or not isinstance(v, ast.Constant):
                    return None
                pairs[k.value] = v.value
            return pairs
        return None

    def _dict_entry_at(self, cls, attr: str, key: str, line: int) -> bool:
        for node in cls.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == attr for t in node.targets):
                continue
            if not isinstance(node.value, ast.Dict):
                return False
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return k.lineno <= line <= (v.end_lineno or v.lineno)
        return False

    def _required_args_only_in_core(self) -> bool:
        cached = self._cache.get(("required_args", ""))
        if cached is not None:
            return bool(cached)
        allowed = {("sqlglot/expressions/core.py", n) for n in (87, 110, 1322)}
        ok = True
        for src in self._sources():
            text = self._read(src)
            if "required_args" not in text:
                continue
            for idx, row in enumerate(text.splitlines(), 1):
                if "required_args" in row and (self._rel(src), idx) not in allowed:
                    ok = False
                    break
            if not ok:
                break
        self._cache[("required_args", "")] = ok
        return ok

    def _constructor_sites_pass_nonempty(self, cls_name: str, key: str) -> bool:
        cache_key = ("ctor", f"{cls_name}.{key}")
        if cache_key in self._cache:
            return bool(self._cache[cache_key])
        sites = 0
        ok = True
        call_re = re.compile(rf"\b{re.escape(cls_name)}\s*\(")
        for src in self._sources():
            text = self._read(src)
            if cls_name not in text or not call_re.search(text):
                continue
            tree = self._parse(src)
            if tree is None:
                return False
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
                if name != cls_name:
                    continue
                sites += 1
                kw = next((k for k in node.keywords if k.arg == key), None)
                if kw is None or not self._provably_nonempty(kw.value, node, tree):
                    ok = False
                    break
            if not ok:
                break
        result = ok and sites > 0
        self._cache[cache_key] = result
        return result

    def _provably_nonempty(self, value, call, tree) -> bool:
        if isinstance(value, ast.Constant):
            return value.value is not None
        if isinstance(value, (ast.Compare, ast.BoolOp)):
            return True
        if isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.Not):
            return True
        if isinstance(value, (ast.Tuple, ast.List)):
            return len(value.elts) > 0
        if isinstance(value, ast.Name):
            scope = self._enclosing(tree, None, call.lineno)
            if scope is None:
                return False
            rhss = []
            for node in ast.walk(scope):
                if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == value.id for t in node.targets
                ):
                    rhss.append(node.value)
                elif (
                    isinstance(node, ast.AnnAssign)
                    and isinstance(node.target, ast.Name)
                    and node.target.id == value.id
                    and node.value is not None
                ):
                    rhss.append(node.value)
                elif (
                    isinstance(node, ast.NamedExpr)
                    and isinstance(node.target, ast.Name)
                    and node.target.id == value.id
                ):
                    rhss.append(node.value)
            if len(rhss) != 1:
                return False
            rhs = rhss[0]
            if isinstance(rhs, ast.Constant):
                return rhs.value is not None
            return isinstance(rhs, (ast.Compare, ast.BoolOp)) or (
                isinstance(rhs, ast.UnaryOp) and isinstance(rhs.op, ast.Not)
            )
        return False

    # --------------------------------------------------------- Z3 copy flag
    def _copy_flag(self, path, line, old, new, analysis):
        pat = re.compile(r"\bcopy\s*=\s*(True|False)\b")
        m_old = pat.search(old)
        m_new = pat.search(new)
        if not m_old or not m_new:
            return None
        if m_old.group(1) == m_new.group(1):
            return None
        if pat.sub("copy=\x00", old.strip()) != pat.sub("copy=\x00", new.strip()):
            return None
        call = self._innermost_copy_call(analysis.pre_ast, line)
        if call is None:
            return None
        func = call.func
        callee = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if callee not in {"alias_", "alias"}:
            return None
        if not call.args:
            return None
        first = call.args[0]
        if not isinstance(first, ast.Call):
            return None
        inner = first.func
        if not (
            isinstance(inner, ast.Attribute)
            and isinstance(inner.value, ast.Name)
            and inner.value.id == "exp"
        ):
            return None
        if not self._copy_used_only_in_maybe_parse(callee):
            return None
        return set()

    def _innermost_copy_call(self, tree, line: int):
        best = None
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not node.lineno <= line <= (node.end_lineno or node.lineno):
                continue
            if not any(k.arg == "copy" and isinstance(k.value, ast.Constant) for k in node.keywords):
                continue
            if best is None or node.lineno >= best.lineno:
                best = node
        return best

    def _copy_used_only_in_maybe_parse(self, callee: str) -> bool:
        cache_key = ("copy", callee)
        if cache_key in self._cache:
            return bool(self._cache[cache_key])
        result = False
        for src in self._sources():
            if f"def {callee}(" not in self._read(src):
                continue
            tree = self._parse(src)
            if tree is None:
                return False
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef) or node.name != callee:
                    continue
                uses = []
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Name) and sub.id == "copy" and isinstance(sub.ctx, ast.Load):
                        uses.append(sub.lineno)
                if len(uses) != 1:
                    return False
                # single use must be the `copy=copy` keyword of maybe_parse
                text = self._read(src).splitlines()[uses[0] - 1]
                if "copy=copy" not in text or "maybe_parse" not in text:
                    return False
                result = True
        self._cache[cache_key] = result
        return result

    # --------------------------------------------------- Z4 version boundary
    def _version_boundary(self, path, line, old, new, analysis):
        stem = self._dialect_stem(path)
        if stem is None:
            return None
        flipped = self._version_op_flip(old, new)
        if flipped is None:
            return None
        if not re.search(r"\bdialect\.version\b", old) or not re.search(
            r"\bdialect\.version\b", new
        ):
            return None
        m_old = re.search(r"\(\s*\d+\s*,\s*\d+(?:\s*,\s*\d+)?\s*\)", old)
        m_new = re.search(r"\(\s*\d+\s*,\s*\d+(?:\s*,\s*\d+)?\s*\)", new)
        if not m_old or not m_new or m_old.group(0) != m_new.group(0):
            return None
        target = self._version_tuple(m_old.group(0))
        if target is None:
            return None
        info = self._pre.get("dialect_versions", {}).get(stem)
        if info is None or info.get("dynamic"):
            return None
        observed = [self._pad(v) for v in info.get("literals", [])]
        observed.append(_VERSION_DEFAULT)
        if any(v == self._pad(target) for v in observed):
            return None
        return set()

    def _version_op_flip(self, old, new):
        pat = re.compile(r"dialect\.version\s*(<=|>=|<|>)")
        a, b = pat.findall(old), pat.findall(new)
        if len(a) != 1 or len(b) != 1:
            return None
        if {a[0], b[0]} not in ({"<", "<="}, {">", ">="}):
            return None
        if pat.sub("\x00", old.strip()) != pat.sub("\x00", new.strip()):
            return None
        return (a[0], b[0])

    def _version_tuple(self, text: str):
        try:
            return [int(part.strip()) for part in text.strip("()").split(",")]
        except ValueError:
            return None

    def _pad(self, version):
        out = [int(x) for x in version][:3]
        return (out + [0, 0, 0])[:3]

    # -------------------------------------------------- Z6 class-literal read
    def _class_literal(self, path, line, old, new, analysis):
        stem = self._dialect_stem(path)
        if stem is None:
            return None
        name_re = r"([A-Z][A-Z0-9_]*)\s*=\s*(.+?)\s*$"
        m_old = re.match(rf"^\s*{name_re}", old)
        m_new = re.match(rf"^\s*{name_re}", new)
        if not m_old or not m_new or m_old.group(1) != m_new.group(1):
            return None
        name = m_old.group(1)
        try:
            val_old = ast.literal_eval(m_old.group(2))
            val_new = ast.literal_eval(m_new.group(2).split("#", 1)[0].strip())
        except (SyntaxError, ValueError):
            return None
        if val_old == val_new:
            return None
        cls = self._innermost_class(analysis.pre_ast, line)
        if cls is None or cls.name != self._pre.get("class_names", {}).get(stem):
            return None
        inner = self._enclosing(analysis.pre_ast, None, line)
        if inner is not cls:
            return None
        if not self._class_assign_at(cls, name, line):
            return None
        post_cls = self._innermost_class(analysis.post_ast, line)
        if post_cls is None or not self._class_assign_at(post_cls, name, line):
            return None
        reads = self._attr_reads(name)
        if reads is None:
            return None
        if self._string_or_bare_refs(path, name, line):
            return None
        defining = f"sqlglot/dialects/{stem}.py"
        bound = self._nums(self.s.dialect_tests.get(stem, []))
        reach = self._reach(stem)
        direct = set()
        for rel, read_line in reads:
            if rel not in self.s.files:
                return None
            allowed = reach if rel == defining else reach & bound
            direct.update(self._line_nums(rel, read_line) & allowed)
        direct.update(self._test_attr_reads(name) & (reach | bound))
        return direct

    def _class_assign_at(self, cls, name: str, line: int) -> bool:
        matches = [
            node
            for node in cls.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ]
        if len(matches) != 1:
            return False
        node = matches[0]
        return node.lineno <= line <= (node.end_lineno or node.lineno)

    def _attr_reads(self, name: str):
        cache_key = ("reads", name)
        if cache_key in self._cache:
            return self._cache[cache_key]
        sites = []
        for src in self._sources():
            text = self._read(src)
            if name not in text:
                continue
            tree = self._parse(src)
            if tree is None:
                return None
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr == name:
                    sites.append((self._rel(src), node.lineno))
        self._cache[cache_key] = sites
        return sites

    def _string_or_bare_refs(self, defining: str, name: str, line: int) -> bool:
        cached = self._cache.get(("bare", name))
        if cached is not None:
            return bool(cached)
        bare_re = re.compile(rf"(?<![\w.]){re.escape(name)}(?!\w)")
        assign_re = re.compile(rf"^\s*{re.escape(name)}\s*(?::[^=]+)?=")
        for src in self._sources():
            text = self._read(src)
            if name not in text:
                continue
            tree = self._parse(src)
            if tree is None:
                return True
            docstrings = set()
            doc_lines: set[int] = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = getattr(node, "body", [])
                    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                        doc = body[0].value
                        docstrings.add(id(doc))
                        doc_lines.update(range(doc.lineno, (doc.end_lineno or doc.lineno) + 1))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Constant)
                    and isinstance(node.value, str)
                    and name in node.value
                    and id(node) not in docstrings
                ):
                    return True
            rel = self._rel(src)
            for idx, row in enumerate(text.splitlines(), 1):
                if idx in doc_lines:
                    continue
                code = row.split("#", 1)[0]
                if not bare_re.search(code) or assign_re.match(code):
                    continue
                if rel != defining or idx != line:
                    return True
        self._cache[("bare", name)] = False
        return False

    def _test_attr_reads(self, name: str) -> set[int]:
        cache_key = ("testreads", name)
        if cache_key in self._cache:
            return set(self._cache[cache_key])
        nums: set[int] = set()
        for src in self._tests():
            text = self._read(src)
            if name not in text:
                continue
            tree = self._parse(src)
            if tree is None:
                return set()
            hits = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr == name:
                    hits.add(node.lineno)
            if not hits:
                continue
            rel = self._rel(src)
            by_method: dict[str, set[int]] = {}
            for number in self.s.tests_by_file.get(rel, []):
                test_obj = self._by_number.get(number)
                if test_obj is not None:
                    by_method.setdefault(test_obj.id.rsplit("::", 1)[-1], set()).add(number)
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if any(node.lineno <= h <= (node.end_lineno or node.lineno) for h in hits):
                    nums.update(by_method.get(node.name, set()))
        self._cache[cache_key] = nums
        return nums

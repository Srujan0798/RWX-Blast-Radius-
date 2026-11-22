"""MODULE C — ChangeSet Representation

Normalized representation of a commit's changes for downstream analysis.
"""

from dataclasses import dataclass, field
from typing import Any
from pathlib import Path
from .patch_parser import Patch, FileChange, FileOperation


@dataclass
class ChangedSymbol:
    name: str
    kind: str
    file_path: str
    line_start: int
    line_end: int
    change_type: str


@dataclass
class ChangeSet:
    commit_id: str
    changed_files: list[str] = field(default_factory=list)
    added_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    renamed_files: dict[str, str] = field(default_factory=dict)
    modified_files: list[str] = field(default_factory=list)
    file_changes: dict[str, FileChange] = field(default_factory=dict)
    added_lines: dict[str, list[int]] = field(default_factory=dict)
    removed_lines: dict[str, list[int]] = field(default_factory=dict)
    changed_symbols: list[ChangedSymbol] = field(default_factory=list)
    changed_imports: list[str] = field(default_factory=list)
    module_level_changes: list[str] = field(default_factory=list)
    unresolved_ranges: list[tuple[str, int, int]] = field(default_factory=list)
    dynamic_flags: list[str] = field(default_factory=list)
    parse_status: str = "ok"
    parse_errors: list[str] = field(default_factory=list)
    parse_warnings: list[str] = field(default_factory=list)

    def get_all_changed_paths(self) -> set[str]:
        paths = set(self.changed_files)
        paths.update(self.added_files)
        paths.update(self.deleted_files)
        paths.update(self.renamed_files.keys())
        paths.update(self.renamed_files.values())
        paths.update(self.modified_files)
        return paths

    def get_python_files(self) -> set[str]:
        return {p for p in self.get_all_changed_paths() if p.endswith(".py")}


def build_changeset(patch: Patch) -> ChangeSet:
    changeset = ChangeSet(commit_id=patch.commit_id)

    for fc in patch.file_changes:
        path = fc.path
        changeset.file_changes[path] = fc

        if fc.added_lines:
            changeset.added_lines[path] = fc.added_lines
        if fc.removed_lines:
            changeset.removed_lines[path] = fc.removed_lines

        match fc.operation:
            case FileOperation.ADDED:
                changeset.added_files.append(path)
                changeset.changed_files.append(path)
            case FileOperation.DELETED:
                changeset.deleted_files.append(path)
                changeset.changed_files.append(path)
            case FileOperation.RENAMED:
                old = fc.old_path
                if old:
                    changeset.renamed_files[old] = path
                    changeset.changed_files.append(old)
                    changeset.changed_files.append(path)
            case FileOperation.MODIFIED:
                changeset.modified_files.append(path)
                changeset.changed_files.append(path)
            case _:
                changeset.changed_files.append(path)

        if fc.parse_warnings:
            changeset.parse_warnings.extend(fc.parse_warnings)

    if patch.parse_errors:
        changeset.parse_errors.extend(patch.parse_errors)
        changeset.parse_status = "error"

    return changeset


def build_all_changesets(patches: dict[str, Patch]) -> dict[str, ChangeSet]:
    return {cid: build_changeset(patch) for cid, patch in patches.items()}


def main() -> int:
    from .patch_parser import parse_all_patches
    import sys

    commits_dir = Path("/data/commits")
    patches = parse_all_patches(commits_dir)
    changesets = build_all_changesets(patches)

    for commit_id, cs in changesets.items():
        print(f"Commit: {commit_id}")
        print(f"  Status: {cs.parse_status}")
        print(f"  Changed files: {len(cs.changed_files)}")
        print(f"  Added: {cs.added_files}")
        print(f"  Deleted: {cs.deleted_files}")
        print(f"  Renamed: {cs.renamed_files}")
        print(f"  Modified: {cs.modified_files}")
        print(f"  Python files: {cs.get_python_files()}")
        if cs.parse_errors:
            print(f"  Errors: {cs.parse_errors}", file=sys.stderr)
        if cs.parse_warnings:
            print(f"  Warnings: {cs.parse_warnings}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
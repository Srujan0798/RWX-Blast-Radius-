"""MODULE B — Patch Processing

Reads unified diffs, identifies changed files, tracks additions/deletions,
handles renames, detects unsupported structures.
"""

import re
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field
from enum import Enum


class FileOperation(Enum):
    MODIFIED = "modified"
    ADDED = "added"
    DELETED = "deleted"
    RENAMED = "renamed"
    UNKNOWN = "unknown"


@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: list[str] = field(default_factory=list)


@dataclass
class FileChange:
    path: str
    operation: FileOperation
    old_path: str | None = None
    hunks: list[Hunk] = field(default_factory=list)
    added_lines: list[int] = field(default_factory=list)
    removed_lines: list[int] = field(default_factory=list)
    parse_warnings: list[str] = field(default_factory=list)


@dataclass
class Patch:
    commit_id: str
    file_changes: list[FileChange] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)


class PatchParser:
    HEADER_PATTERN = re.compile(r"^--- (?:a/)?(.+)$")
    NEW_HEADER_PATTERN = re.compile(r"^\+\+\+ (?:b/)?(.+)$")
    HUNK_PATTERN = re.compile(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")

    def parse_patch_file(self, patch_path: Path) -> Patch:
        commit_id = patch_path.stem
        content = patch_path.read_text()
        return self.parse_patch_content(commit_id, content)

    def parse_patch_content(self, commit_id: str, content: str) -> Patch:
        patch = Patch(commit_id=commit_id)
        lines = content.splitlines(keepends=True)
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith("diff --git"):
                i = self._parse_diff_header(lines, i, patch)
            elif line.startswith("--- ") or line.startswith("+++ "):
                self._validation_error(patch, f"Unexpected header outside diff block at line {i+1}")
                i += 1
            else:
                i += 1

        if content.strip() and not patch.file_changes and not patch.parse_errors:
            self._validation_error(patch, "Nonempty patch contains no file changes")
        return patch

    def _parse_diff_header(self, lines: list[str], start_idx: int, patch: Patch) -> int:
        i = start_idx
        old_path = None
        new_path = None

        if i >= len(lines):
            return i

        while i < len(lines) and not lines[i].startswith("--- "):
            if lines[i].startswith("+++ "):
                match = self.NEW_HEADER_PATTERN.match(lines[i])
                if match:
                    new_path = match.group(1)
            i += 1

        if i >= len(lines):
            self._validation_error(patch, "Missing --- header after diff --git")
            return i

        match = self.HEADER_PATTERN.match(lines[i])
        if match:
            old_path = match.group(1)
        i += 1

        if i >= len(lines) or not lines[i].startswith("+++ "):
            self._validation_error(patch, f"Missing +++ header after --- at line {i+1}")
            return i

        match = self.NEW_HEADER_PATTERN.match(lines[i])
        if match:
            new_path = match.group(1)
        i += 1

        if old_path == "/dev/null" and new_path != "/dev/null":
            operation = FileOperation.ADDED
            path = new_path
            old_path = None
        elif new_path == "/dev/null" and old_path != "/dev/null":
            operation = FileOperation.DELETED
            path = old_path
            new_path = None
        elif old_path and new_path and old_path != new_path:
            operation = FileOperation.RENAMED
            path = new_path
        else:
            operation = FileOperation.MODIFIED
            path = new_path or old_path

        file_change = FileChange(
            path=path or "",
            operation=operation,
            old_path=old_path if operation == FileOperation.RENAMED else None,
        )

        i = self._parse_hunks(lines, i, file_change)
        patch.file_changes.append(file_change)
        return i

    def _parse_hunks(self, lines: list[str], start_idx: int, file_change: FileChange) -> int:
        i = start_idx
        current_old_line = 0
        current_new_line = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith("diff --git"):
                break

            if line.startswith("@@"):
                match = self.HUNK_PATTERN.match(line)
                if not match:
                    file_change.parse_warnings.append(f"Malformed hunk header at line {i+1}: {line.strip()}")
                    i += 1
                    continue

                old_start = int(match.group(1))
                old_count = int(match.group(2)) if match.group(2) else 1
                new_start = int(match.group(3))
                new_count = int(match.group(4)) if match.group(4) else 1

                current_old_line = old_start
                current_new_line = new_start

                hunk = Hunk(
                    old_start=old_start,
                    old_count=old_count,
                    new_start=new_start,
                    new_count=new_count,
                )
                file_change.hunks.append(hunk)
                i += 1
                continue

            if file_change.hunks:
                hunk = file_change.hunks[-1]
                hunk.lines.append(line)

                if line.startswith("+"):
                    file_change.added_lines.append(current_new_line)
                    current_new_line += 1
                elif line.startswith("-"):
                    file_change.removed_lines.append(current_old_line)
                    current_old_line += 1
                elif line.startswith(" "):
                    current_old_line += 1
                    current_new_line += 1
                else:
                    file_change.parse_warnings.append(f"Unexpected line in hunk at line {i+1}: {line[:50]}")
            else:
                file_change.parse_warnings.append(f"Line outside hunk at line {i+1}: {line[:50]}")

            i += 1

        return i

    def _validation_error(self, patch: Patch, message: str) -> None:
        patch.parse_errors.append(message)


def parse_all_patches(commits_dir: Path) -> dict[str, Patch]:
    parser = PatchParser()
    patches = {}
    for patch_file in sorted(commits_dir.glob("*.patch")):
        patches[patch_file.stem] = parser.parse_patch_file(patch_file)
    return patches


def main() -> int:
    import sys
    commits_dir = Path("/data/commits")
    patches = parse_all_patches(commits_dir)

    for commit_id, patch in patches.items():
        print(f"Commit: {commit_id}")
        print(f"  Files changed: {len(patch.file_changes)}")
        for fc in patch.file_changes:
            print(f"    {fc.operation.value}: {fc.path} ({len(fc.hunks)} hunks, +{len(fc.added_lines)}/-{len(fc.removed_lines)} lines)")
        if patch.parse_errors:
            print(f"  Errors: {patch.parse_errors}", file=sys.stderr)
        for fc in patch.file_changes:
            if fc.parse_warnings:
                print(f"  Warnings ({fc.path}): {fc.parse_warnings}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
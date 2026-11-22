import unittest

from src.changeset import build_changeset
from src.patch_parser import FileOperation, PatchParser


class PatchParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = PatchParser()

    def test_nonempty_garbage_is_an_error(self):
        patch = self.parser.parse_patch_content("bad", "this is not a unified diff\n")
        self.assertEqual(patch.file_changes, [])
        self.assertTrue(patch.parse_errors)
        changeset = build_changeset(patch)
        self.assertEqual(changeset.parse_status, "error")

    def test_empty_patch_is_a_noop(self):
        patch = self.parser.parse_patch_content("empty", " \n\n")
        self.assertEqual(patch.file_changes, [])
        self.assertEqual(patch.parse_errors, [])

    def test_incomplete_diff_header_is_an_error(self):
        patch = self.parser.parse_patch_content("bad", "diff --git a/a.py b/a.py\n")
        self.assertTrue(any("Missing --- header" in error for error in patch.parse_errors))

    def test_hunk_content_that_looks_like_file_headers_is_retained(self):
        patch = self.parser.parse_patch_content(
            "content",
            "diff --git a/a.py b/a.py\n"
            "--- a/a.py\n"
            "+++ b/a.py\n"
            "@@ -1,2 +1,2 @@\n"
            "--- old\n"
            "+++ new\n"
            " unchanged\n",
        )
        self.assertEqual(patch.parse_errors, [])
        self.assertEqual(len(patch.file_changes), 1)
        change = patch.file_changes[0]
        self.assertEqual(change.operation, FileOperation.MODIFIED)
        self.assertEqual(change.hunks[0].lines, ["--- old\n", "+++ new\n", " unchanged\n"])
        self.assertEqual(change.removed_lines, [1])
        self.assertEqual(change.added_lines, [1])
        self.assertEqual(change.parse_warnings, [])


if __name__ == "__main__":
    unittest.main()

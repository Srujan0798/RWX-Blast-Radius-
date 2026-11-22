"""Tests for the one-command candidate harness parsing and ledger fields."""

import unittest

from build.candidate_harness import (
    compute_base_and_count,
    duration_ms,
    ledger_row,
    parse_probe,
    parse_score_report,
    parse_unittest_summary,
    sha256_bytes,
)
from argparse import Namespace


class TestCandidateHarness(unittest.TestCase):
    def test_parse_unittest_ok(self):
        summary = parse_unittest_summary("Ran 78 tests in 0.1s\n\nOK\n")
        self.assertEqual(summary["tests_run"], 78)
        self.assertTrue(summary["ok"])
        self.assertFalse(summary["failed"])

    def test_parse_unittest_failure(self):
        summary = parse_unittest_summary("Ran 78 tests in 0.1s\n\nFAILED (failures=1)\n")
        self.assertTrue(summary["failed"])
        self.assertFalse(summary["ok"])

    def test_parse_score_report(self):
        report = parse_score_report("Simulated: 171.626 s\nMisses:    0 (0.000 s of the simulated time)\n")
        self.assertEqual(report["simulated_seconds"], 171.626)
        self.assertEqual(report["misses"], 0)
        self.assertIsNone(report["rejected"])

    def test_parse_score_rejection(self):
        report = parse_score_report("Rejected: not_json on line 3\n")
        self.assertEqual(report["rejected"], "not_json")
        self.assertIsNone(report["simulated_seconds"])

    def test_parse_probe(self):
        probe = parse_probe("HARNESS_CPU_US=1221000\nHARNESS_MAXRSS_KB=168832\n")
        self.assertAlmostEqual(probe["cpu_seconds"], 1.221)
        self.assertAlmostEqual(probe["peak_memory_mb"], 164.875, places=3)

    def test_duration_ms_rounds_halves_up(self):
        self.assertEqual(duration_ms(0.0015), 2)
        self.assertEqual(duration_ms(0.031), 31)

    def test_compute_base_and_count(self):
        output = b'{"commit":"a","workers":[[1,2],[3]]}\n{"commit":"b","workers":[[1,3]]}\n'
        tests = [{"number": 1, "seconds": 1.0}, {"number": 2, "seconds": 0.5}, {"number": 3, "seconds": 0.25}]
        base_ms, count = compute_base_and_count(output, tests)
        self.assertEqual(base_ms, (1500 + 4000) + (1250 + 2000))
        self.assertEqual(count, 5)

    def test_sha256_bytes(self):
        self.assertEqual(sha256_bytes(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_ledger_row_field_count(self):
        result = {
            "selected_test_count": 5,
            "misses": 0,
            "base_seconds": 171.626,
            "simulated_seconds": 171.626,
            "cpu_seconds": 1.221,
            "median_wall_seconds": 0.973,
            "peak_memory_mb": 164.8,
            "result_status": "VERIFIED_ZERO_MISS",
            "output_sha256": "abc",
            "stdout_bytes": 25152,
            "unit_tests": {"tests_run": 78},
            "mutation": {"status": "not_run"},
        }
        args = Namespace(
            benchmark_id="H-1",
            source_revision="candidate",
            architecture_version="candidate",
            hash_seeds=[1, 2, 3],
        )
        row = ledger_row(result, args)
        self.assertEqual(len(row.split(",")), 15)


if __name__ == "__main__":
    unittest.main()

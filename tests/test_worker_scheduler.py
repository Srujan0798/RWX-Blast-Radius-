"""Tests for WorkerScheduler - deterministic adaptive LPT scheduling."""

import unittest
from src.worker_scheduler import WorkerScheduler, WorkerAssignment
from src.input_validator import TestMetadata


def make_tests(durations: dict[int, float]) -> list[TestMetadata]:
    return [TestMetadata(number=n, id=f"test_{n}", file="test.py", seconds=s) for n, s in durations.items()]


class TestWorkerScheduler(unittest.TestCase):
    def test_empty_selection_returns_empty_assignment(self):
        tests = make_tests({1: 0.1, 2: 0.2})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([])
        self.assertEqual(assignment.workers, [])
        self.assertEqual(assignment.worker_count, 0)
        self.assertEqual(assignment.max_load, 0)
        self.assertEqual(assignment.total_score_contribution_ms, 0)

    def test_single_test_single_worker(self):
        tests = make_tests({5: 0.150})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([5])
        self.assertEqual(assignment.workers, [[5]])
        self.assertEqual(assignment.worker_count, 1)
        self.assertEqual(assignment.max_load, 150)
        self.assertEqual(assignment.total_score_contribution_ms, 150 + 2000)

    def test_skewed_durations_prefers_fewer_workers(self):
        tests = make_tests({1: 10.0, 2: 0.1, 3: 0.1, 4: 0.1})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4])
        self.assertEqual(assignment.worker_count, 1)
        self.assertEqual(assignment.workers[0], [1, 2, 3, 4])

    def test_deterministic_ties_by_test_number(self):
        tests = make_tests({1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4])
        self.assertEqual(assignment.worker_count, 1)
        self.assertEqual(sorted([t for w in assignment.workers for t in w]), [1, 2, 3, 4])
        self.assertEqual(assignment.max_load, 4000)
        self.assertEqual(assignment.total_score_contribution_ms, 6000)

    def test_all_k_evaluated(self):
        tests = make_tests({i: 1.0 for i in range(1, 9)})
        scheduler = WorkerScheduler(tests)
        assignments = scheduler._evaluate_all_worker_counts(list(range(1, 9)))
        self.assertEqual(len(assignments), 8)
        for k, a in enumerate(assignments, 1):
            self.assertEqual(a.worker_count, k)

    def test_exact_once_assignment(self):
        tests = make_tests({1: 0.1, 2: 0.2, 3: 0.3, 4: 0.4, 5: 0.5})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4, 5])
        all_assigned = [t for w in assignment.workers for t in w]
        self.assertEqual(len(all_assigned), len(set(all_assigned)))
        self.assertEqual(set(all_assigned), {1, 2, 3, 4, 5})

    def test_free_fill_zero_ms_tests(self):
        tests = make_tests({1: 1.0, 2: 0.0, 3: 0.0, 4: 0.5, 5: 0.0})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4])
        all_assigned = [t for w in assignment.workers for t in w]
        self.assertIn(2, all_assigned)
        self.assertIn(3, all_assigned)
        self.assertIn(5, all_assigned)
        self.assertEqual(assignment.max_load, 1500)

    def test_free_fill_nonzero_within_slack(self):
        tests = make_tests({1: 2.0, 2: 2.0, 3: 0.5, 4: 0.5, 5: 1.0})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4])
        all_assigned = [t for w in assignment.workers for t in w]
        self.assertNotIn(5, all_assigned)
        self.assertEqual(assignment.max_load, 2500)

    def test_free_fill_does_not_increase_max_load_or_workers(self):
        tests = make_tests({1: 2.0, 2: 2.0, 3: 1.5, 4: 1.5, 5: 2.0})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4])
        self.assertEqual(assignment.max_load, 3500)
        self.assertEqual(assignment.worker_count, 2)

    def test_no_empty_workers_in_output(self):
        tests = make_tests({1: 1.0, 2: 1.0})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2])
        for w in assignment.workers:
            self.assertTrue(len(w) > 0)

    def test_worker_count_never_exceeds_8(self):
        tests = make_tests({i: 1.0 for i in range(1, 21)})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule(list(range(1, 21)))
        self.assertLessEqual(assignment.worker_count, 8)

    def test_stable_tie_breaking_fewer_workers(self):
        tests = make_tests({1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4, 5, 6])
        self.assertEqual(assignment.worker_count, 2)

    def test_free_fill_cost_invariant(self):
        tests = make_tests({1: 1.0, 2: 1.0, 3: 0.0, 4: 0.5, 5: 0.0})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4])
        self.assertEqual(assignment.total_score_contribution_ms, assignment.max_load + 2000 * assignment.worker_count)

    def test_free_fill_adds_excluded_catalog_tests(self):
        tests = make_tests({1: 1.0, 2: 1.0, 3: 0.0, 4: 0.5, 5: 0.0, 6: 0.5})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3, 4])
        all_assigned = [t for w in assignment.workers for t in w]
        self.assertIn(5, all_assigned)
        self.assertNotIn(6, all_assigned)
        self.assertEqual(assignment.max_load, 2500)
        self.assertEqual(assignment.worker_count, 1)

    def test_free_fill_uses_actual_excluded_catalog_slack(self):
        tests = make_tests({1: 4.0, 2: 2.0, 3: 1.0, 4: 1.0})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2, 3])
        self.assertEqual(assignment.workers, [[1], [2, 3, 4]])
        self.assertEqual(assignment.max_load, 4000)
        self.assertEqual(assignment.worker_count, 2)

    def test_duration_ms_rounding(self):
        tests = make_tests({1: 0.0015, 2: 0.0025})
        scheduler = WorkerScheduler(tests)
        assignment = scheduler.schedule([1, 2])
        self.assertEqual(assignment.max_load, 5)
        self.assertEqual(assignment.worker_count, 1)
        self.assertEqual(assignment.total_score_contribution_ms, 2005)


if __name__ == "__main__":
    unittest.main()
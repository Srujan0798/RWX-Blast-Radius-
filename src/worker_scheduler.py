"""MODULE F — Worker Scheduler

Implements deterministic adaptive LPT (Longest Processing Time First) scheduling
over k=1..min(8,n) to minimize official score: max_load_ms + 2000*worker_count.
"""

from dataclasses import dataclass
from typing import Any
from .input_validator import TestMetadata


WORKER_COST_MS = 2_000
MAX_WORKERS = 8


@dataclass
class WorkerAssignment:
    workers: list[list[int]]
    worker_loads: list[int]
    max_load: int
    worker_count: int
    worker_overhead_ms: int
    cpu_cost_ms: int
    total_score_contribution_ms: int

    def to_official_format(self) -> dict:
        return {"commit": "", "workers": self.workers}


class WorkerScheduler:
    def __init__(self, tests: list[TestMetadata]):
        self.duration_by_test = {t.number: t.duration_ms for t in tests}
        self.test_count = len(tests)

    def schedule(self, selected_test_numbers: list[int]) -> WorkerAssignment:
        if not selected_test_numbers:
            return WorkerAssignment(
                workers=[],
                worker_loads=[],
                max_load=0,
                worker_count=0,
                worker_overhead_ms=0,
                cpu_cost_ms=0,
                total_score_contribution_ms=0
            )

        n = len(selected_test_numbers)
        max_workers = min(MAX_WORKERS, n)

        assignments = self._evaluate_all_worker_counts(selected_test_numbers)
        best = min(assignments, key=lambda a: (a.total_score_contribution_ms, a.worker_count))
        best = self._free_fill(best, selected_test_numbers)
        return best

    def _lpt_schedule(self, test_numbers: list[int], worker_count: int) -> WorkerAssignment:
        workers: list[list[int]] = [[] for _ in range(worker_count)]
        loads = [0] * worker_count

        sorted_tests = sorted(test_numbers, key=lambda t: (-self.duration_by_test.get(t, 0), t))

        for test_num in sorted_tests:
            duration = self.duration_by_test.get(test_num, 0)
            lightest_idx = loads.index(min(loads))
            workers[lightest_idx].append(test_num)
            loads[lightest_idx] += duration

        occupied_workers = [w for w in workers if w]
        occupied_loads = [loads[i] for i, w in enumerate(workers) if w]

        max_load = max(occupied_loads) if occupied_loads else 0
        actual_worker_count = len(occupied_workers)
        worker_overhead = WORKER_COST_MS * actual_worker_count
        total_score = max_load + worker_overhead

        return WorkerAssignment(
            workers=occupied_workers,
            worker_loads=occupied_loads,
            max_load=max_load,
            worker_count=actual_worker_count,
            worker_overhead_ms=worker_overhead,
            cpu_cost_ms=0,
            total_score_contribution_ms=total_score
        )

    def _evaluate_all_worker_counts(self, test_numbers: list[int]) -> list[WorkerAssignment]:
        if not test_numbers:
            return [WorkerAssignment(
                workers=[], worker_loads=[], max_load=0,
                worker_count=0, worker_overhead_ms=0, cpu_cost_ms=0, total_score_contribution_ms=0
            )]

        n = len(test_numbers)
        max_workers = min(MAX_WORKERS, n)
        assignments = []

        for k in range(1, max_workers + 1):
            assignments.append(self._lpt_schedule(test_numbers, k))

        return assignments

    def _free_fill(self, assignment: WorkerAssignment, all_selected: list[int]) -> WorkerAssignment:
        if assignment.worker_count == 0:
            return assignment

        assigned = set()
        for w in assignment.workers:
            assigned.update(w)

        selected_set = set(all_selected)
        catalog_tests = set(self.duration_by_test.keys())
        unselected_from_catalog = [t for t in catalog_tests if t not in selected_set]
        
        zero_ms = sorted(t for t in unselected_from_catalog if self.duration_by_test.get(t, 0) == 0)
        nonzero_unselected = [t for t in unselected_from_catalog if self.duration_by_test.get(t, 0) > 0]

        new_workers = [list(w) for w in assignment.workers]
        new_loads = list(assignment.worker_loads)
        current_max = assignment.max_load

        for test_num in zero_ms:
            lightest_idx = new_loads.index(min(new_loads))
            new_workers[lightest_idx].append(test_num)

        sorted_nonzero = sorted(nonzero_unselected, key=lambda t: (self.duration_by_test.get(t, 0), t))
        for test_num in sorted_nonzero:
            duration = self.duration_by_test.get(test_num, 0)
            for i in range(len(new_workers)):
                if new_loads[i] + duration <= current_max:
                    new_workers[i].append(test_num)
                    new_loads[i] += duration
                    break

        return WorkerAssignment(
            workers=new_workers,
            worker_loads=new_loads,
            max_load=max(new_loads) if new_loads else 0,
            worker_count=len(new_workers),
            worker_overhead_ms=WORKER_COST_MS * len(new_workers),
            cpu_cost_ms=0,
            total_score_contribution_ms=max(new_loads) + WORKER_COST_MS * len(new_workers) if new_loads else 0
        )


def main() -> int:
    from .input_validator import InputValidator
    from .test_selector import ConservativeTestSelector
    from .patch_parser import parse_all_patches
    from .changeset import build_all_changesets
    from pathlib import Path
    import sys

    validator = InputValidator()
    result = validator.validate_all()
    if not result.success:
        return 1

    commits_dir = Path("/data/commits")
    patches = parse_all_patches(commits_dir)
    changesets = build_all_changesets(patches)

    selector = ConservativeTestSelector(validator.tests)
    scheduler = WorkerScheduler(validator.tests)

    for commit_id, cs in changesets.items():
        decision = selector.select_tests(cs)
        assignment = scheduler.schedule(decision.selected_test_numbers)

        print(f"Commit: {commit_id}")
        print(f"  Selected: {len(decision.selected_test_numbers)} tests")
        print(f"  Workers: {assignment.worker_count}")
        print(f"  Max load: {assignment.max_load}ms")
        print(f"  Worker overhead: {assignment.worker_overhead_ms}ms")
        print(f"  CPU cost: {assignment.cpu_cost_ms}ms")
        print(f"  Score contrib: {assignment.total_score_contribution_ms}ms")
        for i, (worker, load) in enumerate(zip(assignment.workers, assignment.worker_loads)):
            print(f"    Worker {i}: {len(worker)} tests, {load}ms")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
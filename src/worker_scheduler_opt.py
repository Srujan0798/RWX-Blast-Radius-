"""Deterministic worker scheduling with partition refinement.

The optimizer keeps the original LPT assignment as a candidate, then searches
for lower-load partitions with exact bounded packing, capacity-guided lookahead,
and deterministic best-transfer/swap local search. Every candidate is scored
with the official cost: max_load_ms + 2000 * occupied_worker_count.
"""

from __future__ import annotations

from .input_validator import TestMetadata
from .worker_scheduler import MAX_WORKERS, WORKER_COST_MS, WorkerAssignment


_EXACT_ITEM_LIMIT = 120
_EXACT_NODE_LIMIT = 100_000
_SWAP_ITEMS_PER_WORKER = 48
_MAX_REFINEMENT_PASSES = 128


class _SearchLimitReached(Exception):
    pass


class _SearchBudget:
    def __init__(self, remaining: int):
        self.remaining = remaining

    def consume(self) -> None:
        if self.remaining <= 0:
            raise _SearchLimitReached
        self.remaining -= 1


class WorkerScheduler:
    def __init__(self, tests: list[TestMetadata]):
        self.duration_by_test = {t.number: t.duration_ms for t in tests}
        self.test_count = len(tests)

    def schedule(self, selected_test_numbers: list[int]) -> WorkerAssignment:
        selected = self._normalize_selected(selected_test_numbers)
        if not selected:
            return self._empty_assignment()

        assignments = self._evaluate_all_worker_counts(selected)
        best = min(assignments, key=self._assignment_key)
        return self._free_fill(best, selected)

    def _normalize_selected(self, selected_test_numbers: list[int]) -> list[int]:
        seen: set[int] = set()
        selected: list[int] = []
        for test_number in selected_test_numbers:
            if test_number in seen:
                continue
            seen.add(test_number)
            selected.append(test_number)
        return selected

    def _empty_assignment(self) -> WorkerAssignment:
        return WorkerAssignment(
            workers=[],
            worker_loads=[],
            max_load=0,
            worker_count=0,
            worker_overhead_ms=0,
            cpu_cost_ms=0,
            total_score_contribution_ms=0,
        )

    def _evaluate_all_worker_counts(
        self, test_numbers: list[int]
    ) -> list[WorkerAssignment]:
        if not test_numbers:
            return [self._empty_assignment()]

        max_workers = min(MAX_WORKERS, len(test_numbers))
        baselines = [
            self._lpt_schedule(test_numbers, worker_count)
            for worker_count in range(1, max_workers + 1)
        ]
        baseline_best_cost = min(
            assignment.total_score_contribution_ms for assignment in baselines
        )

        assignments: list[WorkerAssignment] = []
        exact_budget = _SearchBudget(_EXACT_NODE_LIMIT)
        for worker_count, baseline in enumerate(baselines, start=1):
            candidates = [baseline]
            lower_bound = self._load_lower_bound(test_numbers, worker_count)

            refined = self._refine_schedule(baseline, test_numbers, lower_bound)
            candidates.append(refined)

            if lower_bound + WORKER_COST_MS * worker_count <= baseline_best_cost:
                exact = self._exact_schedule(
                    test_numbers,
                    worker_count,
                    lower_bound,
                    baseline.max_load,
                    exact_budget,
                )
                if exact is not None:
                    candidates.append(exact)

            lookahead = self._lookahead_schedule(
                test_numbers,
                worker_count,
                lower_bound,
                baseline.max_load,
            )
            if lookahead is not None:
                candidates.append(lookahead)

            assignments.append(min(candidates, key=self._partition_key))
        return assignments

    def _lpt_schedule(
        self, test_numbers: list[int], worker_count: int
    ) -> WorkerAssignment:
        workers: list[list[int]] = [[] for _ in range(worker_count)]
        loads = [0] * worker_count
        sorted_tests = sorted(
            test_numbers,
            key=lambda test_number: (
                -self.duration_by_test.get(test_number, 0),
                test_number,
            ),
        )

        for test_number in sorted_tests:
            duration = self.duration_by_test.get(test_number, 0)
            worker_index = loads.index(min(loads))
            workers[worker_index].append(test_number)
            loads[worker_index] += duration

        return self._make_assignment(workers)

    def _load_lower_bound(self, test_numbers: list[int], worker_count: int) -> int:
        durations = [
            self.duration_by_test.get(test_number, 0) for test_number in test_numbers
        ]
        total = sum(durations)
        largest = max(durations, default=0)
        average_bound = (total + worker_count - 1) // worker_count
        return max(largest, average_bound)

    def _lookahead_schedule(
        self,
        test_numbers: list[int],
        worker_count: int,
        lower_bound: int,
        upper_bound: int,
    ) -> WorkerAssignment | None:
        items = self._positive_items(test_numbers)
        if not items or upper_bound <= lower_bound:
            return None

        best: WorkerAssignment | None = None
        for capacity in self._capacity_targets(lower_bound, upper_bound):
            for workers in (
                self._lookahead_lpt_partition(items, worker_count, capacity),
                self._best_fit_partition(items, worker_count, capacity),
            ):
                if workers is None:
                    continue
                refined_workers = self._refine_workers(workers, lower_bound)
                zero_tests = [
                    test_number
                    for test_number in test_numbers
                    if self.duration_by_test.get(test_number, 0) == 0
                ]
                refined_workers = self._append_zero_tests(refined_workers, zero_tests)
                candidate = self._make_assignment(refined_workers)
                if best is None or self._partition_key(candidate) < self._partition_key(
                    best
                ):
                    best = candidate
            if best is not None and best.max_load <= lower_bound:
                break
        return best

    def _capacity_targets(self, lower_bound: int, upper_bound: int) -> list[int]:
        if upper_bound <= lower_bound:
            return [lower_bound]

        targets = {lower_bound, upper_bound, (lower_bound + upper_bound) // 2}
        for delta in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024):
            target = lower_bound + delta
            if target < upper_bound:
                targets.add(target)
        return sorted(targets)

    def _positive_items(self, test_numbers: list[int]) -> list[tuple[int, int]]:
        items = [
            (self.duration_by_test.get(test_number, 0), test_number)
            for test_number in test_numbers
            if self.duration_by_test.get(test_number, 0) > 0
        ]
        return sorted(items, key=lambda item: (-item[0], item[1]))

    def _lookahead_lpt_partition(
        self,
        items: list[tuple[int, int]],
        worker_count: int,
        capacity: int,
    ) -> list[list[int]] | None:
        workers: list[list[int]] = [[] for _ in range(worker_count)]
        loads = [0] * worker_count

        for item_index, (duration, test_number) in enumerate(items):
            future_items = items[item_index + 1 : item_index + 3]
            best_choice: tuple[tuple[int, int, int, int, int], int] | None = None

            for worker_index in range(worker_count):
                post_load = loads[worker_index] + duration
                if post_load > capacity:
                    continue

                simulated_loads = list(loads)
                simulated_loads[worker_index] = post_load
                simulated_max = post_load
                feasible = True
                for future_duration, _ in future_items:
                    choices = [
                        index
                        for index, load in enumerate(simulated_loads)
                        if load + future_duration <= capacity
                    ]
                    if not choices:
                        feasible = False
                        simulated_max = max(simulated_max, capacity + future_duration)
                        break
                    next_worker = min(
                        choices, key=lambda index: (simulated_loads[index], index)
                    )
                    simulated_loads[next_worker] += future_duration
                    simulated_max = max(simulated_max, simulated_loads[next_worker])

                score = (
                    0 if feasible else 1,
                    simulated_max,
                    post_load,
                    loads[worker_index],
                    worker_index,
                )
                if best_choice is None or score < best_choice[0]:
                    best_choice = (score, worker_index)

            if best_choice is None:
                return None

            worker_index = best_choice[1]
            workers[worker_index].append(test_number)
            loads[worker_index] += duration

        return workers

    def _best_fit_partition(
        self,
        items: list[tuple[int, int]],
        worker_count: int,
        capacity: int,
    ) -> list[list[int]] | None:
        workers: list[list[int]] = [[] for _ in range(worker_count)]
        loads = [0] * worker_count

        for duration, test_number in items:
            choices = [
                index for index, load in enumerate(loads) if load + duration <= capacity
            ]
            if not choices:
                return None
            worker_index = min(choices, key=lambda index: (-loads[index], index))
            workers[worker_index].append(test_number)
            loads[worker_index] += duration

        return workers

    def _refine_schedule(
        self,
        assignment: WorkerAssignment,
        test_numbers: list[int],
        lower_bound: int,
    ) -> WorkerAssignment:
        positive_workers = [
            [
                test_number
                for test_number in worker
                if self.duration_by_test.get(test_number, 0) > 0
            ]
            for worker in assignment.workers
        ]
        refined_workers = self._refine_workers(positive_workers, lower_bound)
        zero_tests = [
            test_number
            for test_number in test_numbers
            if self.duration_by_test.get(test_number, 0) == 0
        ]
        refined_workers = self._append_zero_tests(refined_workers, zero_tests)
        return self._make_assignment(refined_workers)

    def _append_zero_tests(
        self,
        workers: list[list[int]],
        zero_tests: list[int],
    ) -> list[list[int]]:
        if not zero_tests:
            return workers
        if not workers:
            return [list(zero_tests)]

        new_workers = [list(worker) for worker in workers]
        loads = [self._worker_load(worker) for worker in new_workers]
        worker_index = min(
            range(len(new_workers)), key=lambda index: (loads[index], index)
        )
        new_workers[worker_index].extend(zero_tests)
        return new_workers

    def _refine_workers(
        self,
        workers: list[list[int]],
        lower_bound: int,
    ) -> list[list[int]]:
        new_workers = [list(worker) for worker in workers if worker]
        if len(new_workers) <= 1:
            return new_workers

        loads = [self._worker_load(worker) for worker in new_workers]
        current_objective = self._partition_objective(loads)
        if current_objective[0] <= lower_bound:
            return new_workers

        for _ in range(_MAX_REFINEMENT_PASSES):
            transfer = self._best_transfer(new_workers, loads, current_objective)
            swap = self._best_swap(new_workers, loads, current_objective)
            operation = (
                transfer
                if transfer is not None and (swap is None or transfer[0] <= swap[0])
                else swap
            )
            if operation is None:
                break

            objective = operation[0]
            if objective >= current_objective:
                break
            _, operation_type, source, destination, source_test, destination_test = (
                operation
            )
            if operation_type == "transfer":
                new_workers[source].remove(source_test)
                new_workers[destination].append(source_test)
            else:
                source_position = new_workers[source].index(source_test)
                destination_position = new_workers[destination].index(destination_test)
                new_workers[source][source_position] = destination_test
                new_workers[destination][destination_position] = source_test

            loads = [self._worker_load(worker) for worker in new_workers]
            current_objective = self._partition_objective(loads)
            if current_objective[0] <= lower_bound:
                break

        return [worker for worker in new_workers if worker]

    def _best_transfer(
        self,
        workers: list[list[int]],
        loads: list[int],
        current_objective: tuple[int, int, tuple[int, ...]],
    ) -> tuple[tuple[int, int, tuple[int, ...]], str, int, int, int, int] | None:
        best: (
            tuple[tuple[int, int, tuple[int, ...]], str, int, int, int, int] | None
        ) = None
        for source in range(len(workers)):
            for test_number in workers[source]:
                duration = self.duration_by_test.get(test_number, 0)
                for destination in range(len(workers)):
                    if source == destination:
                        continue
                    candidate_loads = list(loads)
                    candidate_loads[source] -= duration
                    candidate_loads[destination] += duration
                    objective = self._partition_objective(candidate_loads)
                    if objective >= current_objective:
                        continue
                    operation = (
                        objective,
                        "transfer",
                        source,
                        destination,
                        test_number,
                        0,
                    )
                    if best is None or self._operation_key(
                        operation
                    ) < self._operation_key(best):
                        best = operation
        return best

    def _best_swap(
        self,
        workers: list[list[int]],
        loads: list[int],
        current_objective: tuple[int, int, tuple[int, ...]],
    ) -> tuple[tuple[int, int, tuple[int, ...]], str, int, int, int, int] | None:
        best: (
            tuple[tuple[int, int, tuple[int, ...]], str, int, int, int, int] | None
        ) = None
        for source in range(len(workers)):
            for destination in range(source + 1, len(workers)):
                difference = abs(loads[source] - loads[destination])
                target_duration = difference / 2
                source_candidates = self._swap_candidates(
                    workers[source], target_duration
                )
                destination_candidates = self._swap_candidates(
                    workers[destination],
                    target_duration,
                )
                for source_test, source_duration in source_candidates:
                    for (
                        destination_test,
                        destination_duration,
                    ) in destination_candidates:
                        candidate_loads = list(loads)
                        candidate_loads[source] += (
                            destination_duration - source_duration
                        )
                        candidate_loads[destination] += (
                            source_duration - destination_duration
                        )
                        objective = self._partition_objective(candidate_loads)
                        if objective >= current_objective:
                            continue
                        operation = (
                            objective,
                            "swap",
                            source,
                            destination,
                            source_test,
                            destination_test,
                        )
                        if best is None or self._operation_key(
                            operation
                        ) < self._operation_key(best):
                            best = operation
        return best

    def _swap_candidates(
        self,
        worker: list[int],
        target_duration: float,
    ) -> list[tuple[int, int]]:
        if len(worker) <= _SWAP_ITEMS_PER_WORKER:
            return [
                (test_number, self.duration_by_test.get(test_number, 0))
                for test_number in worker
            ]

        ranked = sorted(
            worker,
            key=lambda test_number: (
                -self.duration_by_test.get(test_number, 0),
                test_number,
            ),
        )
        closest = sorted(
            worker,
            key=lambda test_number: (
                abs(self.duration_by_test.get(test_number, 0) - target_duration),
                self.duration_by_test.get(test_number, 0),
                test_number,
            ),
        )
        selected = set(ranked[:_SWAP_ITEMS_PER_WORKER])
        selected.update(ranked[-16:])
        selected.update(closest[:32])
        return [
            (test_number, self.duration_by_test.get(test_number, 0))
            for test_number in sorted(selected)
        ]

    def _partition_objective(
        self,
        loads: list[int],
    ) -> tuple[int, int, tuple[int, ...]]:
        if not loads:
            return 0, 0, ()
        sorted_loads = tuple(sorted(loads, reverse=True))
        return max(loads), sum(load * load for load in loads), sorted_loads

    def _operation_key(self, operation: tuple) -> tuple:
        objective = operation[0]
        if operation[1] == "transfer":
            return objective, operation[1], operation[2], operation[3], operation[4]
        return (
            objective,
            operation[1],
            operation[2],
            operation[3],
            operation[4],
            operation[5],
        )

    def _exact_schedule(
        self,
        test_numbers: list[int],
        worker_count: int,
        lower_bound: int,
        upper_bound: int,
        budget: _SearchBudget,
    ) -> WorkerAssignment | None:
        items = self._positive_items(test_numbers)
        if not items or len(items) > _EXACT_ITEM_LIMIT or upper_bound <= lower_bound:
            return None

        low = lower_bound
        high = upper_bound - 1
        best_workers: list[list[int]] | None = None
        while low <= high:
            capacity = (low + high) // 2
            status, workers = self._pack_under_capacity(
                items,
                worker_count,
                capacity,
                budget,
            )
            if status == "feasible":
                best_workers = workers
                high = capacity - 1
            elif status == "infeasible":
                low = capacity + 1
            else:
                break

        if best_workers is None:
            return None

        zero_tests = [
            test_number
            for test_number in test_numbers
            if self.duration_by_test.get(test_number, 0) == 0
        ]
        best_workers = self._append_zero_tests(best_workers, zero_tests)
        return self._make_assignment(best_workers)

    def _pack_under_capacity(
        self,
        items: list[tuple[int, int]],
        worker_count: int,
        capacity: int,
        budget: _SearchBudget,
    ) -> tuple[str, list[list[int]] | None]:
        loads = [0] * worker_count
        choices: list[int] = []
        failed_states: set[tuple[int, tuple[int, ...]]] = set()

        def search(item_index: int) -> bool:
            if item_index == len(items):
                return True

            state = (item_index, tuple(sorted(loads)))
            if state in failed_states:
                return False

            budget.consume()

            duration, _ = items[item_index]
            tried_loads: set[int] = set()
            worker_order = sorted(
                range(worker_count),
                key=lambda index: (-loads[index], index),
            )
            for worker_index in worker_order:
                load = loads[worker_index]
                if load in tried_loads:
                    continue
                tried_loads.add(load)
                if load + duration > capacity:
                    continue

                loads[worker_index] += duration
                choices.append(worker_index)
                if search(item_index + 1):
                    return True
                choices.pop()
                loads[worker_index] -= duration

            failed_states.add(state)
            return False

        try:
            feasible = search(0)
        except _SearchLimitReached:
            return "unknown", None

        if not feasible:
            return "infeasible", None

        workers: list[list[int]] = [[] for _ in range(worker_count)]
        for (_, test_number), worker_index in zip(items, choices):
            workers[worker_index].append(test_number)
        return "feasible", workers

    def _make_assignment(self, workers: list[list[int]]) -> WorkerAssignment:
        occupied_workers = [list(worker) for worker in workers if worker]
        worker_loads = [self._worker_load(worker) for worker in occupied_workers]
        max_load = max(worker_loads, default=0)
        worker_count = len(occupied_workers)
        worker_overhead = WORKER_COST_MS * worker_count
        total_score = max_load + worker_overhead
        return WorkerAssignment(
            workers=occupied_workers,
            worker_loads=worker_loads,
            max_load=max_load,
            worker_count=worker_count,
            worker_overhead_ms=worker_overhead,
            cpu_cost_ms=0,
            total_score_contribution_ms=total_score,
        )

    def _worker_load(self, worker: list[int]) -> int:
        return sum(self.duration_by_test.get(test_number, 0) for test_number in worker)

    def _partition_key(self, assignment: WorkerAssignment) -> tuple:
        loads = tuple(sorted(assignment.worker_loads, reverse=True))
        squared_load = sum(load * load for load in assignment.worker_loads)
        signature = tuple(
            sorted(tuple(sorted(worker)) for worker in assignment.workers)
        )
        return (
            assignment.max_load,
            assignment.worker_count,
            squared_load,
            loads,
            signature,
        )

    def _assignment_key(self, assignment: WorkerAssignment) -> tuple:
        loads = tuple(sorted(assignment.worker_loads, reverse=True))
        squared_load = sum(load * load for load in assignment.worker_loads)
        signature = tuple(
            sorted(tuple(sorted(worker)) for worker in assignment.workers)
        )
        return (
            assignment.total_score_contribution_ms,
            assignment.worker_count,
            assignment.max_load,
            squared_load,
            loads,
            signature,
        )

    def _free_fill(
        self,
        assignment: WorkerAssignment,
        all_selected: list[int],
    ) -> WorkerAssignment:
        if assignment.worker_count == 0:
            return assignment

        selected_set = set(all_selected)
        catalog_tests = set(self.duration_by_test.keys())
        unselected_from_catalog = [
            test_number
            for test_number in catalog_tests
            if test_number not in selected_set
        ]
        zero_ms = sorted(
            test_number
            for test_number in unselected_from_catalog
            if self.duration_by_test.get(test_number, 0) == 0
        )
        nonzero_unselected = sorted(
            (
                test_number
                for test_number in unselected_from_catalog
                if self.duration_by_test.get(test_number, 0) > 0
            ),
            key=lambda test_number: (
                self.duration_by_test.get(test_number, 0),
                test_number,
            ),
        )

        new_workers = [list(worker) for worker in assignment.workers]
        new_loads = list(assignment.worker_loads)
        current_max = assignment.max_load

        for test_number in zero_ms:
            worker_index = new_loads.index(min(new_loads))
            new_workers[worker_index].append(test_number)

        for test_number in nonzero_unselected:
            duration = self.duration_by_test.get(test_number, 0)
            for worker_index in range(len(new_workers)):
                if new_loads[worker_index] + duration <= current_max:
                    new_workers[worker_index].append(test_number)
                    new_loads[worker_index] += duration
                    break

        return self._make_assignment(new_workers)


OptimizedWorkerScheduler = WorkerScheduler

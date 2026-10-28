from collections import deque


def round_robin(jobs: list[tuple[str, int]], quantum: int) -> list[tuple[str, int]]:
    if quantum < 1:
        raise ValueError(f"quantum must be at least 1, got {quantum}")
    queue = deque((name, work) for name, work in jobs if work > 0)
    slices = []
    while queue:
        name, left = queue.popleft()
        ran = min(quantum, left)
        slices.append((name, ran))
        if left - ran > 0:
            queue.append((name, left - ran))
    return slices


def finish_order(jobs: list[tuple[str, int]], quantum: int) -> list[str]:
    remaining = {}
    for name, work in jobs:
        remaining[name] = work
    order = []
    for name, ran in round_robin(jobs, quantum):
        remaining[name] -= ran
        if remaining[name] == 0:
            order.append(name)
    return order

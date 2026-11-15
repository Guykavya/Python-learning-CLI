## Approach

The ready queue is a FIFO of unfinished work. Each step takes the oldest waiting job, runs one slice, and either retires it (recording the clock) or sends it to the back, behind everyone who was waiting. The bound is checked only in `submit`; a job that is re-queued has just left the queue, so the size never exceeds the capacity.

## Code

```python
from collections import deque


class Scheduler:
    def __init__(self, quantum, capacity):
        if quantum <= 0:
            raise ValueError("quantum must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.quantum = quantum
        self.capacity = capacity
        self.ready = deque()                 # (name, work left)
        self.clock = 0
        self.finished = []

    def submit(self, name, work):
        if work <= 0:
            raise ValueError("work must be positive")
        if len(self.ready) >= self.capacity:
            return False
        self.ready.append((name, work))
        return True

    def step(self):
        if not self.ready:
            return None
        name, left = self.ready.popleft()
        run = min(self.quantum, left)
        self.clock += run
        left -= run
        if left:
            self.ready.append((name, left))     # not done: back of the line
        else:
            self.finished.append((name, self.clock))
        return name

    def run_all(self):
        while self.ready:
            self.step()
        return list(self.finished)

    def __len__(self):
        return len(self.ready)
```

## Complexity

`submit`, `step` and `len` are `O(1)`. `run_all` performs one step per slice: a job with work `w` needs `ceil(w / quantum)` slices, so the total is the sum of those, plus `O(1)` per step. Memory is `O(capacity + finished jobs)`.

## Another way

Store mutable `[name, left]` lists and change `left` in place; it saves creating a new tuple per slice but makes it easier to share a job object by accident. A real scheduler would also track **arrival times** and give each job a waiting time and turnaround time (`finish - arrival`); adding a `submit(name, work, arrival)` and a clock that jumps forward when the queue is empty is a good extension.

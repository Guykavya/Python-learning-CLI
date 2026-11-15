## Hint 1

Store the ready queue as `deque` of `(name, work_left)` pairs. `submit` checks `len(self.ready) >= self.capacity` before appending. In `step`, which deque method takes the front job, and which puts it back at the end?

## Hint 2

```
def step(self):
    if not self.ready: return None
    name, left = self.ready.popleft()
    run = min(self.quantum, left)
    self.clock += run; left -= run
    if left: self.ready.append((name, left))
    else: self.finished.append((name, self.clock))
    return name
```

Trace the example with this by hand before you run the tests.

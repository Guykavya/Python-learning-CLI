## Approach

The recipe of the `heapq` documentation: every heap entry is a **list** `[priority, count, task]`.

- `count` comes from `itertools.count()`; it makes the entries unique and orders equal priorities by the time of the last `add`. The heap compares priority first, then count; two entries never have the same count, so the task field (which may not be comparable) is never compared.
- A dictionary `entries` maps each live task to its entry, for `O(1)` lookup.
- To change or remove a task, the entry in the heap is **marked** (its task field is replaced by a marker). It stays in the heap, and its fields `priority` and `count` do not change, so the heap rule still holds. The task field is never part of a comparison, so changing it is safe.
- `pop` takes entries from the top and skips the marked ones.
- To keep the heap from growing without limit, rebuild it from `entries.values()` (all live entries) when it holds more than `2 * live + 8` entries. A rebuild costs `O(live)` and removes at least `live + 8` stale entries; each stale entry was made by one `add` or `remove`, so the cost per operation stays `O(log n)` on average.

## Code

```python
import heapq
import itertools

class LazyPQ:
    REMOVED = object()

    def __init__(self):
        self.heap = []
        self.entries = {}
        self.counter = itertools.count()

    def add(self, task, priority):
        if task in self.entries:
            self.entries[task][-1] = self.REMOVED       # the old entry becomes stale
        entry = [priority, next(self.counter), task]
        self.entries[task] = entry
        heapq.heappush(self.heap, entry)
        self._compact_if_needed()

    def remove(self, task):
        entry = self.entries.pop(task)                  # KeyError if the task is not there
        entry[-1] = self.REMOVED
        self._compact_if_needed()

    def pop(self):
        while self.heap:
            priority, _, task = heapq.heappop(self.heap)
            if task is not self.REMOVED:
                del self.entries[task]
                self._compact_if_needed()
                return task
        raise KeyError("pop from an empty priority queue")

    def __len__(self):
        return len(self.entries)

    def __contains__(self, task):
        return task in self.entries

    def stored(self):
        return len(self.heap)

    def _compact_if_needed(self):
        if len(self.heap) > 2 * len(self.entries) + 8:
            self.heap = list(self.entries.values())
            heapq.heapify(self.heap)
```

## Complexity

`add`, `remove` and `pop`: `O(log n)` amortised (a rebuild is `O(n)` but happens only after `n` stale entries have been made). Memory: `O(n)`, and at most `2n + 8` entries at any time after an operation.

## Another way

- **Versions instead of markers.** Keep `info[task] = (priority, count)` for the live tasks and push immutable tuples `(priority, count, task)`. An entry from the heap is live only if `info.get(task) == (priority, count)`. No entry is ever changed; the same rebuild rule applies.
- **An indexed heap** (problem p030) moves the entry instead of leaving a stale copy: there are never more entries than tasks, but the code is longer.

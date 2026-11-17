## Approach

An ordinary binary heap stored in two parallel lists, `keys` and `prios`, plus a dictionary `pos` that tells the **position** of every key in the lists. All movement of items goes through one function, `_swap(i, j)`, which also fixes `pos`; so `pos` is always right, and every key can be found in `O(1)`.

With the position known, a change is local:

- `update`: change the priority at that position and call `_restore(i)`. If the new priority is smaller than the parent's, the item must go **up**; otherwise it may have to go **down**. (Exactly one of the two moves can happen, never both.)
- `remove(key)`: to keep the shape of the heap (a complete tree), swap the item with the last one, cut off the last position, and then restore the heap at the position `i`. The former last item is a leaf of some other branch: compared with its new neighbours it may be smaller than its new parent (go up) or bigger than its new children (go down). `_restore` handles both.
- `pop_min` is `remove` of position 0, and returns the pair that was there.
- `push` appends and sifts up.

No stale entries exist, so `stored()` is always `len(pq)`; each operation is `O(log n)`.

## Code

```python
class IndexedPQ:
    def __init__(self):
        self.keys = []                       # keys[i] is the key at heap position i
        self.prios = []                      # prios[i] is its priority
        self.pos = {}                        # key -> position

    def __len__(self):
        return len(self.keys)

    def __contains__(self, key):
        return key in self.pos

    def stored(self):
        return len(self.keys)

    def peek(self):
        if not self.keys:
            raise IndexError("peek from an empty queue")
        return self.keys[0], self.prios[0]

    def priority(self, key):
        return self.prios[self.pos[key]]

    def push(self, key, priority):
        if key in self.pos:
            raise ValueError(f"{key!r} is already in the queue")
        self.keys.append(key)
        self.prios.append(priority)
        self.pos[key] = len(self.keys) - 1
        self._sift_up(len(self.keys) - 1)

    def update(self, key, priority):
        i = self.pos[key]
        self.prios[i] = priority
        self._restore(i)

    def remove(self, key):
        self._remove_at(self.pos[key])

    def pop_min(self):
        if not self.keys:
            raise IndexError("pop from an empty queue")
        item = (self.keys[0], self.prios[0])
        self._remove_at(0)
        return item

    def _swap(self, i, j):
        self.keys[i], self.keys[j] = self.keys[j], self.keys[i]
        self.prios[i], self.prios[j] = self.prios[j], self.prios[i]
        self.pos[self.keys[i]] = i
        self.pos[self.keys[j]] = j

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.prios[i] < self.prios[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self.keys)
        while True:
            smallest = i
            left, right = 2 * i + 1, 2 * i + 2
            if left < n and self.prios[left] < self.prios[smallest]:
                smallest = left
            if right < n and self.prios[right] < self.prios[smallest]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def _restore(self, i):
        if i > 0 and self.prios[i] < self.prios[(i - 1) // 2]:
            self._sift_up(i)
        else:
            self._sift_down(i)

    def _remove_at(self, i):
        last = len(self.keys) - 1
        if i != last:
            self._swap(i, last)
        key = self.keys.pop()
        self.prios.pop()
        del self.pos[key]
        if i != last:
            self._restore(i)
```

## Complexity

`push`, `update`, `remove`, `pop_min`: `O(log n)` (a sift moves along one path; the dictionary costs `O(1)`). `peek`, `priority`, `len`, `in`: `O(1)`. Memory `O(n)`, exactly `n` entries, no more.

## Another way

- **Lazy deletion** (p029) uses only `heapq`; a change pushes a new entry and leaves a stale one behind. The code is shorter; the heap holds more entries than keys, and you have to rebuild it from time to time.
- **`update` as `remove` followed by `push`**: correct and shorter (two `O(log n)` calls), but it does two moves instead of one.
- **Hole instead of swaps**: when sifting, keep the moving item in a variable and copy the other items into the hole, writing the moving item once at the end. It halves the writes; `pos` is then updated once per copied item. The result is the same.
- This structure is the heart of **Dijkstra's algorithm with decrease-key** (dsa.12) and of schedulers that must change priorities (timers, task queues).

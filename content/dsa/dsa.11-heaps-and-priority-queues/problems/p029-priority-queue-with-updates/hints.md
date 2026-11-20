## Hint 1

Look at the recipe in chapter section 11: entries `[priority, count, task]`, a dictionary `task -> entry` and a marker for dead entries. What does the unique, increasing `count` give you? Think of two tasks with the same priority and tasks that are `object()`s, which cannot be compared with `<`.

## Hint 2

Changing a priority and removing a task are the **same** thing at the start: mark the old entry as dead (replace its task by a marker object) and drop it from the dictionary. A change then pushes a new entry. `pop` takes entries from the heap until it finds one that is not marked. Do not forget `len`: it is the size of the **dictionary**, not of the heap.

## Hint 3

For the size rule keep `stored()` small: after every operation, if the heap list has more than `2 * len(self) + 8` entries, rebuild it from the live entries and call `heapify`:

```
def _compact_if_needed(self):
    if len(self.heap) > 2 * len(self.entries) + 8:
        self.heap = list(self.entries.values())     # only the live entries
        heapq.heapify(self.heap)
```

Call it at the end of `add`, `remove` and `pop`. Why is it correct to rebuild from the dictionary? Why does it not make `add` slower than `O(log n)` on average? (Each rebuild removes at least `len` stale entries, and each stale entry was created by one operation.)

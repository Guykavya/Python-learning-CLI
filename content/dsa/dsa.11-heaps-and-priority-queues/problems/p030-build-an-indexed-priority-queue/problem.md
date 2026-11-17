# Build an indexed priority queue

In problem p029 a change of priority left a stale entry in the heap. Here you build the other solution mentioned at the end of chapter section 11: a **binary heap that knows where each key is**, so that a priority can be changed, or a key removed, **in place** in `O(log n)`, with no stale entries. Write the class `IndexedPQ`. The heap is written by you, with lists and swaps: the tests reject `heapq`, `bisect`, `sorted` and `.sort`.

A **key** identifies an item (any hashable object, not necessarily comparable); a **priority** is a number. A **smaller** priority comes out first.

| Call | What it does |
|---|---|
| `push(key, priority)` | add a new key. If the key is already there: `ValueError` |
| `update(key, priority)` | change the priority of a key that is in the queue (bigger or smaller). `KeyError` if it is not there |
| `remove(key)` | take the key out, wherever it is in the heap. `KeyError` if it is not there |
| `pop_min()` | remove the key with the smallest priority and return the pair `(key, priority)`. `IndexError` if the queue is empty |
| `peek()` | the pair `(key, priority)` with the smallest priority, without removing it. `IndexError` if the queue is empty |
| `priority(key)` | the current priority of a key. `KeyError` if it is not there |
| `len(pq)` | the number of keys |
| `key in pq` | whether the key is in the queue |
| `pq.stored()` | the number of entries the heap holds. It must **always** be equal to `len(pq)` (no stale entries) |

If two keys in the queue have the **same priority**, which of them comes first is not specified, and the tests never put two equal priorities in the queue at the same time.

## Example

```python
>>> pq = IndexedPQ()
>>> pq.push("write", 5); pq.push("test", 3); pq.push("deploy", 8)
>>> pq.peek()
('test', 3)
>>> pq.update("deploy", 1)             # a better priority: it moves up
>>> pq.update("test", 9)               # a worse priority: it moves down
>>> pq.remove("write")                 # from the middle of the heap
>>> len(pq), pq.stored()
(2, 2)
>>> pq.pop_min(), pq.pop_min()
(('deploy', 1), ('test', 9))
>>> len(pq)
0
```

## Constraints

- Up to 100,000 operations. The big test (15,000 keys, 60,000 updates, then removals and pops) runs in a separate process with a 10-second limit. Searching for a key in a list costs `O(n)` and does not fit.
- Priorities are numbers (integers or floats). Keys are hashable and may be objects that cannot be compared with `<`.
- The chapter only names this structure ("an indexed heap"); the hints teach it.

## Think about

A normal heap can only find the root quickly. What extra information must be kept, and **when must it be updated**? Which operation of your heap changes the position of items? After you change the priority of an item, is it always right to move it up? What if the priority became bigger? When you remove an item from the middle by putting the last item into its place, which direction may that last item have to move?

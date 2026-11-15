# Merge k sorted lists

`lists` is a Python list of `k` heads (some may be `None`); each chain is sorted in non-decreasing order. Write `merge_k(lists)` that links all their nodes into one sorted list and returns its head (`None` if there are no nodes at all). Reuse the nodes; do not change values.

Merging the lists one after another is too slow when `k` is large (the result grows and is walked again for every new list). Aim for `O(N log k)`, where `N` is the total number of nodes (chapter section 8):

- a **min-heap** (`heapq`, dsa.06) holding the current front node of each list, or
- **divide and conquer**: merge the lists in pairs, then the results in pairs, ... (using `merge_two` from problem 23).

Heap trap: two entries `(5, node)` and `(5, other)` make `heapq` compare the nodes, and nodes cannot be compared (`TypeError`). Put a tie-breaker between the value and the node, for example the list index.

## Example

```python
>>> to_list(merge_k([from_list([1, 4, 5]), from_list([1, 3, 4]), from_list([2, 6])]))
[1, 1, 2, 3, 4, 4, 5, 6]
>>> merge_k([]) is None, merge_k([None, None]) is None
(True, True)
```

## Constraints

- `0 <= k <= 10**4`, total nodes `N <= 2 * 10**4` in the tests; 5,000 lists of 4 nodes must merge within a few seconds.

## Think about

How many entries does the heap hold at most? Why does that give `log k` and not `log N` per step?

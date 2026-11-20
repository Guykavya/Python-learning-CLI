## Model answer

A min-heap keeps one rule: **every item is smaller than or equal to its children** (the item at index `i` is `<=` the items at `2i + 1` and `2i + 2`). Because of that rule the root is the smallest item, `heappop` can take it, and the repair after taking it (the last item goes to the root and sinks down) restores the rule again, so the pops come out in sorted order. The first line is `[1, 2, 3, 4, 5, 7, 8]` for that reason.

The assignment `heap[3] = 0` writes a `0` below its parent `3` (index 1). The tree of `[1, 3, 2, 0, 5, 4, 7]` has `3` as the parent and `0` as the child, so the rule "parent `<=` child" is false at this edge. The list now prints `[1, 3, 2, 0, 5, 4, 7]`, and the pops print `[1, 2, 3, 0, 4, 5, 7]`.

The number `0` comes out **after** `1`, `2` and `3`. `heappop` looks only at the root and at the items on the path along which the moved item sinks. It never searches the whole list, so it does not know that a smaller number is hidden deep in the tree: `0` stays under `3` until `3` itself reaches the root and leaves. The heap trusts the rule; once the rule is broken somewhere, every answer that depends on the root being the minimum can be wrong, not only the position that was edited.

There are two correct ways. **Lazy deletion:** do not touch the entry, mark it as removed and push a new entry with the new priority; `pop` throws away the stale entries when they reach the top. A change costs `O(log n)`, and the heap keeps stale entries until they surface (memory is `O(number of changes)` unless you rebuild now and then). **Edit and repair:** change the item, then restore the rule: `heapq.heapify(heap)` rebuilds the whole heap in `O(n)` (after it, draining the example gives the sorted `[0, 1, 2, 3, 4, 5, 7]`), which is too slow if you do it after every change; a repair of one position (moving it up or down) costs `O(log n)` but needs to know the position of the item.

Entries as lists `[priority, count, task]` are compared field by field: first the priority, then the count; the task is compared only if priority and count are equal, and the unique count makes that impossible. So changing the **task** field never changes a comparison result, and the heap rule stays true. Changing the **priority** field changes a comparison result, exactly like `heap[3] = 0`.

To change a priority in `O(log n)` without stale entries, the heap must know **where each item is** (a dictionary from item to index that is updated at every swap): this is the **indexed heap**. After the change the item is moved up or down from its own position.

## Checklist

Your answer should mention
- [ ] the heap rule: every parent is `<=` its children, so the root is the minimum
- [ ] `heap[3] = 0` puts a smaller value below a bigger parent: the rule is broken at that edge
- [ ] `heappop` looks only at the root and at the sift path: it cannot see a violation deep in the heap
- [ ] the real output: the pops are `[1, 2, 3, 0, 4, 5, 7]`, not sorted
- [ ] lazy deletion: mark the old entry, push a new one; cost `O(log n)` per change, stale entries stay until they surface
- [ ] repair by `heapq.heapify`: `O(n)`; or repair one position from its index in `O(log n)`
- [ ] changing the task field of a `[priority, count, task]` entry is safe: the comparison never reaches it
- [ ] changing the priority field is not safe: it changes comparisons
- [ ] an indexed heap keeps a dictionary item -> position, so a change costs `O(log n)` without stale entries

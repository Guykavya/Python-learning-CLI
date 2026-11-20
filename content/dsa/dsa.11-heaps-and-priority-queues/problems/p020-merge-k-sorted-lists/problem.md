# Merge k sorted lists with a heap

You get `lists`, a list of `k` lists of numbers. Every inner list is sorted from small to large. Return **one** sorted list with all the numbers of all the inner lists. Write `merge_k_sorted(lists)`.

Rules:

- Inner lists may be empty, and `lists` itself may be empty.
- Numbers repeat, within a list and between lists.
- Do not change the input lists.
- Use a heap that holds **one item per list** (section 9 of the chapter). The tests reject `sorted`, `.sort`, and `merge` (`heapq.merge` would do the whole task for you), so write the loop yourself.

## Example

```python
>>> merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]])
[1, 1, 2, 3, 4, 4, 5, 6]
>>> merge_k_sorted([[], [7], []])
[7]
>>> merge_k_sorted([])
[]
```

## Constraints

- Up to 2,000 lists and 400,000 numbers in total. The big test runs in a separate process with a 10-second limit.
- Time `O(N log k)` for `N` numbers in total, extra memory `O(k)` besides the result.

## Think about

When you take the smallest of the first items, which single item must you add to the heap next? What goes wrong if two lists have the same first number and the heap has to compare the next part of the entry?

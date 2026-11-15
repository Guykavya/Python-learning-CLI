# Middle of the list

Write `middle_node(head)` that returns the **middle node** of a non-empty list. For an even number of nodes there are two middles; return the **second** one. Return the node object itself and do not change the list.

Use **fast and slow pointers** (chapter section 7): `slow` moves one step, `fast` moves two. When `fast` reaches the end, `slow` is in the middle.

## Example

```python
>>> middle_node(from_list([1, 2, 3, 4, 5])).val
3
>>> middle_node(from_list([1, 2, 3, 4, 5, 6])).val       # middles 3 and 4: the second
4
>>> middle_node(from_list([7])).val
7
```

## Constraints

- `1 <= n <= 10**5`. One walk, `O(1)` extra memory (no Python list of nodes or values).

## Think about

Try both loop conditions on lists of length 4 and 5: `while fast and fast.next` and `while fast.next and fast.next.next`. Which one gives the second middle and which one the first?

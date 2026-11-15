# Rotate right by k

Write `rotate_right(head, k)` that rotates the list to the right by `k` places and returns the new head: the last `k` nodes move, in order, to the front.

```text
1 -> 2 -> 3 -> 4 -> 5,  k = 2    gives    4 -> 5 -> 1 -> 2 -> 3
```

`k` can be **larger** than the length `n`: rotating by `n` gives the same list, so only `k % n` matters. Do not walk `k` times; `k` can be `10**12`.

Rewire nodes (no new nodes, no value changes).

## Example

```python
>>> to_list(rotate_right(from_list([1, 2, 3, 4, 5]), 2))
[4, 5, 1, 2, 3]
>>> to_list(rotate_right(from_list([0, 1, 2]), 4))         # 4 % 3 = 1
[2, 0, 1]
>>> to_list(rotate_right(from_list([1, 2]), 0))
[1, 2]
```

## Constraints

- `0 <= n <= 10**5`, `0 <= k <= 10**12`.

## Think about

Rotating is "cut the list after node `n - k` and put the second piece in front". Which three links are involved? Which node becomes the new tail?

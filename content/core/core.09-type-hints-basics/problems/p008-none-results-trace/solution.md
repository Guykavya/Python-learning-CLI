## Walkthrough

1. `add_item(cart, "tea")` appends and returns `None`, so `r1` is `None`. Nothing printed.
2. `show(cart)` prints `1 items` (during the call) and returns `None`, so `r2` is `None`.
3. `print(r1, r2)` prints `None None`.
4. `print(cart)` prints `['tea']`.
5. `print(nums.sort())`: `sort` sorts in place and returns `None`, so it prints `None`.
6. `print(nums)` shows the sorted list `[1, 2, 3]`.
7. `print(sorted([3, 1, 2]))` prints the new sorted list `[1, 2, 3]`.

## The exact output

```text
1 items
None None
['tea']
None
[1, 2, 3]
[1, 2, 3]
```

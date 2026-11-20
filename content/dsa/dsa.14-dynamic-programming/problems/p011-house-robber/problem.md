# House robber

Houses stand in a row, and house `i` holds `nums[i]` money. You may not rob two **adjacent** houses (the alarms are linked). Write `rob(nums)` that returns the most money you can take (chapter section 5).

## Example

```python
>>> rob([2, 7, 9, 3, 1])         # houses with 2, 9 and 1
12
>>> rob([1, 2, 3, 1])            # 1 + 3
4
>>> rob([2, 1, 1, 2])            # the two ends: skipping two houses in a row is allowed
4
>>> rob([])
0
```

## Constraints

- `0 <= len(nums) <= 10**5`, `0 <= nums[i] <= 400`.
- Return an `int` (the chapter's version returns `(best, table)`; return only `best`).
- `O(n)` time. A recursion `n` deep fails for `n = 10**5`, and a recursion without a memo is exponential.

## Think about

Look at the **last** house. Either you rob it or you skip it. In each case, what is left is the same problem on fewer houses. Which one?

# Assign cookies

Child `i` has a **greed** `greed[i]`: the smallest cookie size that makes them happy. Cookie `j` has a **size** `sizes[j]`. Each child gets at most one cookie and each cookie goes to at most one child. A child is happy if their cookie's size is **at least** their greed.

Write `assign_cookies(greed, sizes)` that returns the **largest number of happy children** (chapter section 11, "Assign cookies").

## Example

```python
>>> assign_cookies([1, 2, 3], [1, 1])
1
>>> assign_cookies([1, 2], [1, 2, 3])
2
>>> assign_cookies([10, 9, 8, 7], [5, 6, 7, 8])
2
>>> assign_cookies([2], [2])        # size equal to greed is enough
1
```

## Constraints

- `0 <= len(greed), len(sizes) <= 3 * 10**4`, all values between 1 and `10**9`.
- The lists are **not** sorted. Do not change the caller's lists.

## Think about

A small cookie can satisfy several children. Which of them should get it, and why is that choice never a mistake?

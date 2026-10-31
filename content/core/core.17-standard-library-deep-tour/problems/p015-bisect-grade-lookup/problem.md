# bisect: grade lookup and counting in a range

A chain of `if score >= 90: ... elif score >= 80: ...` works, but the boundaries are buried in
code. The `bisect` module finds positions in a **sorted** list by binary search, in O(log n):

- `bisect_left(a, x)`: the first index where `x` could be inserted **before** any equal items.
- `bisect_right(a, x)` (also called `bisect`): the index **after** any items equal to `x`.

```python
a = [10, 20, 20, 30]
bisect_left(a, 20)    # 1
bisect_right(a, 20)   # 3
```

Write two functions in `solution.py`.

1. `grade(score: int, breakpoints: list[int] = [60, 70, 80, 90], grades: str = "FDCBA") -> str`
   - A score **equal** to a breakpoint belongs to the **higher** grade: 59 is `F`, 60 is `D`,
     90 is `A`, 100 is `A`.
   - Assume `len(grades) == len(breakpoints) + 1` and the breakpoints are sorted.
2. `count_in_range(sorted_nums: list[int], lo: int, hi: int) -> int`
   - How many numbers `n` in the sorted list have `lo <= n <= hi` (both ends **included**).
     Duplicates count. If `lo > hi` the answer is 0.
   - Use two bisects, not a loop over the list.

(The default list is never changed, so the "mutable default" trap from core.06 does not bite
here, but do not modify it.)

**Example**

```python
grade(59), grade(60), grade(85), grade(90)    # ('F', 'D', 'B', 'A')
grade(5, [3, 6], "xyz")                       # 'y'
count_in_range([1, 3, 3, 3, 5, 8], 3, 5)      # 4
count_in_range([1, 3, 3, 3, 5, 8], 4, 4)      # 0
```

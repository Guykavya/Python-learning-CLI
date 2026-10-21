# Append the total in place

Write `append_total(numbers)` that **changes the caller's list** by appending the sum of its
items to the end, and returns `None` (the convention for functions that change their argument,
like `list.sort()`).

**Examples**

```python
marks = [10, 20, 30]
result = append_total(marks)
marks     # [10, 20, 30, 60]
result    # None

empty = []
append_total(empty)
empty     # [0]
```

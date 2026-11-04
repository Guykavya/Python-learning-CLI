# Trace the bisect module

Predict **exactly** what this program prints. Do not run it.

```python
from bisect import bisect_left, bisect_right, insort

a = [10, 20, 20, 20, 30, 40]
print(bisect_left(a, 20), bisect_right(a, 20))
print(bisect_left(a, 25), bisect_right(a, 25))
print(bisect_left(a, 5), bisect_right(a, 45))
insort(a, 25)
print(a)
insort(a, 5)
print(a)
print(bisect_left(a, 20, 2, 4))
words = ["fig", "kiwi", "apple", "banana"]
print(bisect_left(words, 5, key=len), bisect_right(words, 4, key=len))
print(bisect_left([], 7))
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Use the rules from the chapter: `bisect_left` is the lower bound, `bisect_right` is the upper bound, `insort` inserts at the `bisect_right` position.
The optional arguments are `lo` and `hi` (a slice of the list to search) and `key` (a function applied to the **list elements**, not to the searched value).
Careful with the last lines: they test the key argument and an empty list.

## After you answer

1. Which insertion position does `insort(a, 5)` use? Which one would an `insort_left` use, and does it matter for plain numbers?
2. In `bisect_left(a, 20, 2, 4)` the answer is 2. Would the answer change if `hi` were 6? Why?
3. Why is the searched value `5` compared with the **lengths** in the `key=len` calls?

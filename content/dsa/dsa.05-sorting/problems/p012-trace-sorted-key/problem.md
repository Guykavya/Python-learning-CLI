# Trace sorted with key and reverse

Predict **exactly** what this program prints. Do not run it.

```python
words = ["pear", "fig", "apple", "kiwi", "date", "plum"]
print(sorted(words, key=len))
print(sorted(words, key=len, reverse=True))
print(sorted(words, reverse=True))
print(sorted(words, key=lambda w: (len(w), w)))
print(sorted(words, key=lambda w: (-len(w), w)))
print(sorted(words, key=lambda w: w[-1]))
print(words)
nums = [3, -1, -4, 2]
print(sorted(nums, key=abs))
print(nums.sort())
print(nums)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

For every line write the **key** next to each word first, then order by key. Python's sort is stable, **including** when `reverse=True`:
equal keys stay in their original input order (they are *not* reversed). Remember that `sorted` returns a new list and leaves `words` alone,
and that `list.sort()` sorts in place and returns `None`.

## After you answer

1. Why does line 2 not simply reverse line 1?
2. Which line shows that the tuple key `(-len(w), w)` and `reverse=True` are different tools?
3. What does `print(nums.sort())` teach about methods that change a list in place?

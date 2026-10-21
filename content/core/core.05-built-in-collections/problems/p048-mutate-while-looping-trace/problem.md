# Changing a list while looping

Predict **exactly** what this program prints, one line per printed line. Do not run it.
Draw names, lists and arrows on paper as you go.

```python
nums = [1, 2, 3, 4, 5, 6]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)
nums = [2, 2, 4, 5]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)
items = [1, 2, 3]
seen = []
for x in items:
    seen.append(x)
    if x == 2:
        items.append(10)
print(seen)
vals = [5, 6, 7]
for i in range(len(vals)):
    vals[i] = vals[i] * 2
print(vals)
for v in vals:
    v = v + 1
print(vals)
safe = [n for n in [2, 2, 4, 5] if n % 2]
print(safe)
```

Write your answer in `answer.txt`.

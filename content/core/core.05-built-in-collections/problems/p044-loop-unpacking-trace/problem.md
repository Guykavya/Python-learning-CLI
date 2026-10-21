# Unpacking inside loops

Predict **exactly** what this program prints, one line per printed line. Do not run it.

```python
scores = {"asha": 3, "ravi": 5}
for name, s in scores.items():
    print(name, s * 2)
pairs = list(zip("abc", [1, 2, 3]))
print(pairs[1])
for i, (letter, n) in enumerate(pairs):
    print(i, letter * n)
records = [("x", 1, 2, 3), ("y", 4)]
for tag, *nums in records:
    print(tag, nums, sum(nums))
a = [[1, 2], [3, 4]]
for first, second in a:
    first = first * 10
print(a)
for row in a:
    row[0] = row[0] * 10
print(a)
```

Write your answer in `answer.txt`.

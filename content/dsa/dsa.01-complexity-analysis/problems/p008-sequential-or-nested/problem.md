# Sequential or nested?

Two loops one after the other add their costs. Two loops one inside the other multiply them.
This program counts the work in four arrangements. Predict **exactly** what it prints. Do not run it.

```python
n = 8

ops = 0
for i in range(n):
    ops += 1
for j in range(n):
    ops += 1
print("sequential", ops)

ops = 0
for i in range(n):
    for j in range(n):
        ops += 1
print("nested", ops)

ops = 0
for i in range(n):
    ops += 1
    for j in range(5):
        ops += 1
print("nested constant", ops)

ops = 0
size = n
while size > 0:
    for j in range(size):
        ops += 1
    size = size // 2
print("shrinking", ops)
```

Write your answer in `answer.txt`, one line per printed line, for example `sequential 3`.

## After you answer

Give the Big-O of each of the four blocks for a general `n`. One of them looks like a nested loop but is O(n).
Which one, and why?

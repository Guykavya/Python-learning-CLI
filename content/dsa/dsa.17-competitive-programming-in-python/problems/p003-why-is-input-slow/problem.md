# Why is `input()` slow?

Two programs read the same `2 * 10**5` numbers, one per line:

```python
# A
n = int(input())
total = 0
for _ in range(n):
    total += int(input())
print(total)
```

```python
# B
import sys
data = sys.stdin.read().split()
print(sum(map(int, data[1:])))
```

On most judges B is several times faster than A. Explain **why**. Write your answer in `answer.md` (6 to 10 sentences). Then compare it with the model answer and tick the checklist.

Your answer should cover:

1. What work one call to `input()` does, and how many times that work is repeated by A.
2. What buffering is, and who does it (the operating system, the C library, Python).
3. What `readline` and `read` change, and why `read()` does the least per-line work.
4. Why the difference only matters when the input is large.
5. A situation where you must still read line by line.

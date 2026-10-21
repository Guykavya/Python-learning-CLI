# Trace a recursion tree

This function splits a problem of size `n` into two halves and solves each half the same way, until a piece has
size 1. Every call also does `n` units of its own work (in a real algorithm such as merge sort, that is the work
of combining the two halves). `calls` counts the calls and `work` adds up all the work.

(You have not written functions yet. Read `def solve(n):` as "a named piece of code that receives `n`";
`solve(n // 2)` runs that code again with a smaller number and continues after it finishes; `return` stops the
current call.)

Predict **exactly** what the program prints. Do not run it.

```python
calls = [0]
work = [0]


def solve(n):
    calls[0] += 1
    work[0] += n          # pretend this call does n steps of its own work
    if n <= 1:
        return
    solve(n // 2)
    solve(n - n // 2)


for n in [1, 2, 4, 8, 16, 10]:
    calls[0] = 0
    work[0] = 0
    solve(n)
    print(n, calls[0], work[0])
```

Write your answer in `answer.txt`, one line per printed line, three numbers separated by single spaces.

## After you answer

For `n` a power of two, write formulas for `calls` and `work`. Which Big-O do they show?

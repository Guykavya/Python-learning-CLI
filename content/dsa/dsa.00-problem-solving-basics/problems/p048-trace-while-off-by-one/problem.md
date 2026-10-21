# Trace: off-by-one in while loops

The three loops below look almost the same. They differ only in `<` versus `<=`, and in whether
the counter is increased **before** or **after** the `print`. Predict **exactly** what this program
prints, one line per printed line. Do not run it.

```python
i = 1
while i < 3:
    print("A", i)
    i += 1
print("A ends at", i)
i = 1
while i <= 3:
    i += 1
    print("B", i)
print("B ends at", i)
i = 1
while i < 3:
    i += 1
    print("C", i)
print("C ends at", i)
```

Write your answer in `answer.txt`, one line per printed line, with single spaces exactly as
`print` would put them (for example `A 1`).

Tip: for each loop, make a small table with the columns `i before check`, `condition`, `printed`,
`i after`. Pay special attention to the last check, the one that is false.

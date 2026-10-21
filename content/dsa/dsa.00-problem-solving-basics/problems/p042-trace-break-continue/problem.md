# Trace break, continue and loop else

This program uses `continue` in the inner loop, `break` in the outer loop, and an `else:` on **both** loops.

Predict **exactly** what it prints. Do not run it. Use a trace table with columns `i`, `j`, `i + j`, action, `count`.

```python
count = 0
for i in range(1, 6):
    if i == 5:
        print("stop at", i)
        break
    for j in range(1, 4):
        if (i + j) % 2 == 0:
            continue
        count += 1
        print(i, j)
    else:
        print("row", i, "done")
else:
    print("all rows done")
print("count", count)
```

Write your answer in `answer.txt`, one line per printed line. `print(i, j)` prints the two numbers with one space between them.

Pay attention to which `else` belongs to which loop (look at the indentation), and to the rule:
a loop's `else` runs when the loop ends **without** `break`. Does `continue` count as a `break`?

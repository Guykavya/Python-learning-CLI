# Explain: why does sorting help here?

Here is the loop of `combination_sum` from chapter section 7:

```python
candidates = sorted(candidates)
...
for i in range(start, len(candidates)):
    c = candidates[i]
    if c > remaining:
        break
    path.append(c)
    go(i, remaining - c)
    path.pop()
```

Answer in `answer.md` in **three sentences** (one per question):

1. Why is it correct to `break` (leave the whole loop) instead of `continue` (skip just this candidate) when `c > remaining`?
2. What would go wrong if you kept the `break` but removed the `sorted(...)` line? Give a tiny example with candidates and a target.
3. Does sorting reduce the number of **answers**, the number of **recursive calls**, or only the number of **loop iterations** compared to a version with `continue` and no sorting?

# Explain: what does this code do?

You joined a project and found this function, used in a sensor dashboard. No docstring, no
tests, and its author has left.

```python
def g(xs, k):
    r, w = [], sum(xs[:k])
    for i in range(k, len(xs)):
        r.append(w / k); w += xs[i] - xs[i - k]
    return r
```

A teammate ran it once:

```python
>>> g([2, 4, 6, 8, 10], 2)
[3.0, 5.0, 7.0]
```

Read it the way the chapter suggests (follow the data, run small cases by hand, name things),
and write `answer.md` (about 200 to 300 words) that covers:

1. **What it computes**, in one plain sentence, and a good name for the function and for
   `xs`, `k`, `r`, `w`.
2. **How it works**: what `w` holds at the top of each loop step, and why
   `w += xs[i] - xs[i - k]` is cheaper than calling `sum` again.
3. **The bug.** Look at the example output again and work out what it *should* be. Say which
   result is missing and why.
4. **Two more edge cases**: what happens for `k = 0`, and for `k` larger than `len(xs)`?
5. **A fixed version** (code), with a docstring and a check for bad `k`.

**Example of the level of detail expected for point 1**

> "It returns the averages of every run of `k` neighbouring values." Then propose names.

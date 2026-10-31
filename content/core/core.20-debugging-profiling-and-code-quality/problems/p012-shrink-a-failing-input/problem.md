# Shrink a failing input

A program crashes on a 300-line input file. Somewhere in there are the two or three lines that
actually trigger the bug, but which? Reading 300 lines is slow. A **shrinker** finds out by
experiment: remove part of the input, run the program again, and keep the removal if it
**still fails**. Repeat until nothing more can be removed. This idea is called **delta
debugging**, and testing tools such as Hypothesis do it automatically.

Write `shrink(items: list, fails) -> list` in `solution.py`.

- `fails(candidate)` takes a list and returns `True` if the bug still happens with it.
- If `fails(list(items))` is `False`, raise `ValueError` (there is nothing to shrink).
- Return a list `result` such that:
  1. `fails(result)` is `True`;
  2. `result` is a **subsequence** of `items`: some elements removed, the rest in the original
     order;
  3. `result` is **1-minimal**: removing **any single** element from it makes `fails` return
     `False`.
- Do not change `items`. Always pass `fails` a **list**.
- `fails` may be slow, so do not try every subset (that is 2^n calls). The tests allow
  20,000 calls for a 300-item input.

`fails` is not always "monotone": removing an element can make the bug disappear and removing
one more can make it come back. Your loop must still end with a 1-minimal result.

**Example**

```python
def fails(lines):
    return "import x" in lines and "x.run()" in lines

source = ["# demo", "import os", "import x", "print(1)", "x.run()", "print(2)"]
shrink(source, fails)                 # ['import x', 'x.run()']

shrink([5, 1, 4, 2, 8, 3], lambda s: sum(s) >= 15)
# [4, 8, 3] is one valid answer (sum 15; removing any one drops below 15),
# and so is [5, 4, 8]
```

The second example has several correct answers; the tests check the three rules, not one
particular list.

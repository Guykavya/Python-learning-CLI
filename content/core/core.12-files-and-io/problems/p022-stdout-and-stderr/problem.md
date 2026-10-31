# Results to stdout, warnings to stderr

Programs have two output streams. **stdout** is for results, so other programs can read it in a pipe.
**stderr** is for warnings and errors, so they do not mix into the results.

Write `sum_numbers(items)` in `solution.py`. `items` is a list of strings.

- Convert each item to `int`. If it is not a whole number, print `warning: skipping 'x'` to **stderr**
  (with the item in quotes, like `repr`) and go on.
- At the end, print `total: N` to **stdout** and return `N`.
- Nothing else may be printed.

**Example**

```python
sum_numbers(["1", "x", "5"])
# stdout: total: 6
# stderr: warning: skipping 'x'
```

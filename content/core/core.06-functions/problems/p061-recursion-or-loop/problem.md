# Recursion or a loop?

A student wrote this to add up a list:

```python
def total(items):
    if not items:
        return 0
    return items[0] + total(items[1:])

print(total(list(range(500))))      # 124750
print(total(list(range(5000))))     # RecursionError: maximum recursion depth exceeded
```

In `answer.md`, explain:

1. What happens on the call stack while `total` runs, and why the second call fails although the
   function is "correct". Mention the default recursion limit and why Python has one.
2. Why `sys.setrecursionlimit(100000)` is a poor fix.
3. Whether Python would be fine "because the recursive call is the last thing the function
   does". (What is tail-call optimisation, and does CPython do it?)
4. A second cost of this function besides stack depth (look at `items[1:]`), with its Big-O.
5. How you would write it instead, and a general rule for when recursion is the better choice in
   Python. Give one example of a problem where recursion is clearly better.

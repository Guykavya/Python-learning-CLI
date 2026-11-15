# Trace: draw the call stack

The function `f` below follows the rule `f(n) = f(n-1) + f(n-2)` with `f(n) = 1` for `n <= 2`. The list `stack` holds the arguments of the calls that are running **right now** (pushed on entry, popped on exit), so it is a picture of Python's call stack. `deepest` keeps a copy of the tallest stack seen.

Predict **exactly** what this program prints. Do not run it.

```python
stack = []
deepest = []
calls = 0


def f(n):
    global calls, deepest
    calls += 1
    stack.append(n)
    if len(stack) > len(deepest):
        deepest = stack[:]
    if n <= 2:
        result = 1
    else:
        result = f(n - 1) + f(n - 2)
    stack.pop()
    return result


print("value", f(5))
print("calls", calls)
print("max depth", len(deepest))
print("deepest stack", deepest)
print("stack at the end", stack)
```

Write your answer in `answer.txt`, one printed line per line, exactly as Python prints it (lists look like `[1, 2]`).

## How to work

Draw the recursion tree of `f(5)` first (chapter section 4): every node is one call, the children of `n` are `n-1` and `n-2`, and the nodes with `n <= 2` are leaves.
- The number of calls is the number of nodes.
- The maximum depth is the length of the longest path from the root to a leaf (counting both ends).
- The stack at any moment is the path from the root to the call that is running.

## After you answer

1. How many calls does `f(6)` make? (Use: calls of `n` = 1 + calls of `n-1` + calls of `n-2`.)
2. Why is the stack empty at the end?
3. At the deepest moment, which calls are **waiting**, and for what?

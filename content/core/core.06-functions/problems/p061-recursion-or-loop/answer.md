**1. The call stack.** Every call creates a frame that stays alive until the call returns.
`total(items)` cannot return until `total(items[1:])` returns, so for a list of n items there are
n + 1 frames alive at the deepest point (one per call, the last for the empty list), plus the
module's frame. CPython limits the depth to 1000 frames by default (`sys.getrecursionlimit()`),
so 500 items is fine but 5000 raises `RecursionError`. The limit exists because each Python call
also uses the interpreter's own C stack, which is small and fixed; without a limit, runaway
recursion would crash the whole interpreter instead of raising a clean Python error.

**2. Raising the limit.** It treats the symptom. The C stack is still finite, so a big enough
list can crash the interpreter with a segmentation fault, which cannot be caught or reported
nicely. And the code would still be slow (point 4). The limit is a safety net, not a setting to
tune.

**3. Tail calls.** Tail-call optimisation means reusing the current frame when a call is the
very last action, so the stack does not grow. CPython does not do it (by design, partly so
tracebacks show every call). Also, this function is not even tail-recursive: after the recursive
call returns, it still has to add `items[0]`.

**4. Copying.** `items[1:]` builds a new list of n - 1 items, then n - 2, and so on. That is
about n²/2 item copies: O(n²) time and lots of temporary memory, where a simple sum is O(n).

**5. Better.** Use a loop or the built-in: `return sum(items)`, or

```python
result = 0
for x in items:
    result += x
return result
```

Rule of thumb: in Python, when each step makes **one** recursive call on a slightly smaller
input (walking a sequence or counting down), use a loop. Recursion is the better choice when the
data or the problem **branches or nests**: flattening nested lists, walking a folder tree,
generating all subsets or permutations, or divide-and-conquer that halves the input (where the
depth is only log n).

Key ideas to check: one frame per pending call; limit about 1000 protects the C stack; raising it
risks a crash; no tail-call optimisation; slicing makes it O(n²); loops for linear recursion,
recursion for branching/nested problems.

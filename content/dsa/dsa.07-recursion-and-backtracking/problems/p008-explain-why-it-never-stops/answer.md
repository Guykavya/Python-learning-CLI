## Answer key

1: **A** - there is no `if` that returns, so `count` calls itself forever (0, -1, -2, ...). Fix: `if n < 0: return` (or `if n == 0: ...; return`) before the recursive call.

2: **B** - the base case `n == 0` exists, but `n - 2` jumps over it for odd `n` (5, 3, 1, -1, -3, ...). Fix: `if n <= 0: return 0`, or `if n < 2: return 0` if odd values should stop at 1.

3: **C** - `xs[:]` is a copy of the **whole** list, so the input never gets shorter. Fix: recurse on `xs[1:]`.

4: **D** - `n // 10` removes one digit, and every `n >= 0` eventually drops below 10, which is the base case. `digits(0)` is 1, `digits(12345)` is 5.

## What Python does

Every call gets a **stack frame** that stays on the **call stack** until the call returns. A recursion that never stops keeps adding frames. CPython counts them and, at its **recursion limit** (about 1000 by default, see `sys.getrecursionlimit()`), raises `RecursionError: maximum recursion depth exceeded`. The limit exists to protect the interpreter: without it the real C stack would overflow and the whole program would crash instead of raising a clean exception you can read.

Checklist: your answer should mention
- [ ] the labels **1-A, 2-B, 3-C, 4-D**
- [ ] snippet 2 fails only for **odd** `n` (it skips 0)
- [ ] snippet 3 copies the whole list (`xs[:]`), so there is **no progress**
- [ ] **RecursionError** and the **recursion limit** (about 1000)
- [ ] the **stack frames** piling up on the **call stack**

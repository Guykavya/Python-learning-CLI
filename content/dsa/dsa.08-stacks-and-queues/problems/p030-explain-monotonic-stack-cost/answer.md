## Model answer

The classmate multiplies the **worst case of one `while` loop** by the number of `for` steps. That bound is correct but not tight, because the `while` loops are not independent: a pop removes an index forever, so a long `while` loop "uses up" the stack and later loops have less to pop.

One `while` loop can indeed run `n - 1` times: for `[5, 4, 3, 2, 1, 9]` the last step pops all five waiting indices. But then the stack is almost empty, and that cannot happen again until many new indices have been pushed.

Count pushes and pops instead of loops. Each index `i` is **pushed exactly once** (the `append` at the end of its own `for` step) and **popped at most once** (after a pop it is gone and is never pushed again). Every iteration of the `while` loop performs exactly one pop. So the total number of `while` iterations over the whole run is at most the number of pushes, which is `n`. The `for` loop does `n` steps of constant work besides the `while`. Total: at most `n` pushes + `n` pops + `n` steps = **`O(n)`**.

This is **amortised analysis** (the "accounting" or "each element enters once and leaves once" argument): some steps are expensive, but the expensive work is paid for by earlier cheap steps, and the sum is linear. The same argument shows that the **queue from two stacks** is `O(1)` amortised per operation (each item moves from the inbox to the outbox at most once), and that the sliding-window **deque** is `O(n)`.

The stack can hold all `n` indices: a non-increasing input like `[5, 4, 3, 2, 1]` never pops, so memory is `O(n)` in the worst case.

Checklist: your answer should mention
- [ ] one `while` loop CAN run about `n` times (an example like a decreasing list followed by a large number)
- [ ] each index is **pushed once** and **popped at most once**
- [ ] each `while` iteration is exactly **one pop**, so the total is at most `n`
- [ ] total time **O(n)**, not `O(n^2)`
- [ ] the name **amortised** analysis
- [ ] another use: **queue from two stacks** or the sliding-window **deque**
- [ ] worst-case stack size `n` for a non-increasing input

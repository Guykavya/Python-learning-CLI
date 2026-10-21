**1. Sometimes expensive.** Most appends just write the new item into a free slot: O(1). But when the block is
full, Python must reserve a bigger block and copy every existing item into it before writing the new one. That
append costs O(n), where `n` is the current length.

**2. Cost table for doubling.**

| append number | grows? | copies | capacity after |
|---|---|---|---|
| 1 | no | 0 | 1 |
| 2 | yes | 1 | 2 |
| 3 | yes | 2 | 4 |
| 4 | no | 0 | 4 |
| 5 | yes | 4 | 8 |
| 6 to 8 | no | 0 | 8 |
| 9 | yes | 8 | 16 |
| ... | | | |
| 2^k + 1 | yes | 2^k | 2^(k+1) |

After `n` appends, the copies are `1 + 2 + 4 + ... + 2^k`, where `2^k < n`. A doubling sum is less than twice
its last term, so the copies total less than `2n`. Adding the `n` writes of the new items themselves, the whole
job costs less than `3n` steps: O(n). Divided over `n` appends, that is less than 3 steps each on average.
"Amortised O(1)" means exactly this: any sequence of `n` appends costs O(n) total, so the average per append is a
constant, even though individual appends vary. (The expensive appends "pay" for themselves because they are
rare: each one is followed by as many cheap appends as it copied.)

**3. Growing by 10.** Then the list grows every 10 appends, copying 10, 20, 30, ..., about `n` items. The total is
`10 * (1 + 2 + ... + n/10)`, about `n^2 / 20`. That is O(n^2) in total, O(n) per append on average. Growing by a
**fixed amount** fails; growing by a **fixed fraction** (doubling, or Python's roughly 12.5%) works, because the
copies form a geometric sum.

**4. Program 2.** `insert(0, x)` has to shift every existing item one place right to make room at the front.
The `i`-th insert shifts `i` items, so the total is `0 + 1 + ... + (n - 1) = n(n - 1)/2`: O(n^2). The measurements
agree: when `n` grows 10 times, append's time grows about 10 times (0.0008 to 0.008 s, linear), while insert's
grows about 90 times (0.015 to 1.38 s), close to the 100 times that `n^2` predicts.

**5. Amortised is an average over a sequence, not a promise for each operation.** One particular append can still
take O(n) time (copying a million items). For a batch job that only cares about the total time, this is
irrelevant. For something that must respond within a fixed time on every single step, such as a game frame or a
real-time controller, one slow append could cause a visible pause.

Key ideas to check: the occasional append copies everything, O(n); doubling copies 1 + 2 + 4 + ... < 2n; total
O(n), amortised O(1) per append; fixed +10 growth gives about n^2/20 copies, O(n^2); insert(0) shifts all items, total
n(n-1)/2, timings grow ~100x for 10x n; amortised bounds the total, not each step.

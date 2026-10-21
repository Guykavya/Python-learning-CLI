**1. Where the factor of 10 comes from.** In a Python `for` loop, every pass is run by the interpreter: fetch the
next item, look up `total`, create a new integer for the sum, store it, check the loop. Each of those is several
machine operations. `sum` is written in C: it walks the list in a tight compiled loop with no interpreter work per
item. Both touch each element once (O(n)), but the cost per element differs by about 10 times. Big-O deliberately
hides this constant.

**2. Why `n log n` is only slightly slower.** `log2(10^6)` is about 20, so in theory sorting does ~20 times more steps.
But the sort is Python's highly optimised C implementation (Timsort), while the set-based check pays interpreter or
hashing costs per element. The two constants partly cancel. As `n` grows, `log n` grows very slowly (it is about 30 at
`n = 10^9`), so the gap between O(n) and O(n log n) never becomes huge in practice. In contests, both usually pass
for `n` up to about 10^6.

**3. Tiny inputs.** Big-O describes how cost grows as `n` gets large. With 5 items, scanning the list is 5 quick
comparisons, about the same as computing a hash and checking one slot. For small, fixed `n`, constants and overheads
decide, and building the set (which costs more than several lookups) may not even pay off.

**4. The rule.** First choose by Big-O whenever `n` can be large: a better growth rate always wins eventually, and at
contest sizes it wins by enormous factors. The nested loop shows it: 10^8 simple steps take 6.5 s, while sorting a
million numbers (about 2 * 10^7 comparisons, in C) takes 0.35 s. At `n = 10^5` the nested loop would need about
10 minutes and the sort 0.03 s. No 10x constant can bridge a factor of 10^4. Only **between solutions with the same
Big-O** (or for small inputs) should you choose by constant factors, and then by measuring, not guessing.

**5. Speeding up a correct O(n) solution.** Replace explicit Python loops by built-ins written in C (`sum`, `max`,
`sorted`, `set`, `str.join`, `list.count`); read all input at once with `sys.stdin.read().split()` instead of many
`input()` calls; build output with one `"\n".join(...)` and a single `print`; avoid repeated attribute lookups or
work inside the loop that could be done once before it.

Key ideas to check: interpreter overhead per pass versus C built-ins explains the 10x; log n is small (about 20), and
Timsort is fast C, so n log n is close to n in practice; for tiny n constants dominate; choose by Big-O first,
constants only among equal Big-O or tiny n; 10^8 steps in 6.5 s versus a sort in 0.35 s; use built-ins, fast input,
one join for output.

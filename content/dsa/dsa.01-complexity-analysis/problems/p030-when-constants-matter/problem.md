# When do constants matter?

Big-O ignores constant factors. These measurements, taken on this machine with `time.perf_counter`, show where that
is fine and where it is not. All lists have `n = 10^6` different random integers.

| task | code | Big-O | time |
|---|---|---|---|
| total | `for x in a: total += x` | O(n) | 0.13 s |
| total | `sum(a)` | O(n) | 0.014 s |
| any repeat? | loop with a set, stop at first repeat | O(n) | 0.45 s |
| any repeat? | `len(set(a)) < n` | O(n) | 0.20 s |
| any repeat? | `sorted(a)`, then compare neighbours | O(n log n) | 1.05 s |
| membership in a 5-item list, 10^6 times | `7 in small_list` | O(5) each | 0.135 s |
| membership in a 5-item set, 10^6 times | `7 in small_set` | O(1) each | 0.126 s |

And from the chapter: a nested loop over `n = 10^4` (10^8 steps) took about 6.5 s, while sorting `10^6` numbers took
about 0.35 s.

In `answer.md`:

1. `sum(a)` and the `for` loop are both O(n), yet one is about 10 times faster. Explain where a constant factor like
   that comes from in Python.
2. The sort-based repeat check is O(n log n), and only about 2 to 5 times slower than the O(n) ones here. Why is
   the gap small? Would it ever become huge as `n` grows?
3. For a 5-item list, `in` costs about the same as on a set. Why does Big-O not help here?
4. Give a rule: when should you choose by Big-O, and when by measuring constant factors? Use the nested-loop versus
   sorting numbers to show that no constant factor can save a worse Big-O for large `n`.
5. Name one thing you could do (without changing the algorithm) to speed up a correct O(n) Python solution that is
   just over the time limit.

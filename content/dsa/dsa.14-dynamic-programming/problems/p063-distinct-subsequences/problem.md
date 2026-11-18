# Distinct subsequences

Write `num_distinct(s, t)` that returns in **how many ways** `t` can be picked out of `s` as a subsequence. Two ways are different when they use a different set of **positions** of `s` (section 15, "Related problems").

## Example

```python
>>> num_distinct("rabbbit", "rabbit")     # which of the three b's is left out
3
>>> num_distinct("babgbag", "bag")
5
>>> num_distinct("abc", "")               # pick nothing: one way
1
>>> num_distinct("ab", "abc")             # t is longer: no way
0
```

For `"babgbag"` and `"bag"`, the five ways use the positions (0, 1, 3), (0, 1, 6), (0, 5, 6), (2, 5, 6) and (4, 5, 6).

## Constraints

- `0 <= len(s) <= 400`, `0 <= len(t) <= 400`, lowercase letters.
- The answer can be huge (`num_distinct("a" * 400, "a" * 200)` has 120 digits). Python integers handle it; do not take it modulo anything.
- `O(len(s) * len(t))` time. A recursion that tries "use this letter or skip it" without a memo is exponential.

## Think about

Let `f(i, j)` be the number of ways to pick `t[:j]` out of `s[:i]`. Look at the last letter of `s[:i]`. You can always **not use** it. When may you **use** it, and what is left to match then? What are `f(i, 0)` and `f(0, j)` for `j > 0`?

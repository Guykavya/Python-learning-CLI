The model answer is shown when you check. The ideas that must appear:

1. A costs up to `q * n` additions (4 * 10^10 here); the worst questions span the whole array.
2. B costs `n` to build and O(1) per question: `n + q` in total (about 4 * 10^5 here).
3. `p[r] - p[l-1]` cancels the first `l - 1` elements; `p[0] = 0` handles `l = 1` with no special case.
4. B uses O(n) extra memory; A is fine for few questions or short ranges.
5. With updates between questions, one change touches up to `n` prefix cells, so plain prefix sums lose their advantage.

A strong answer also gives one tiny worked example, such as `p = 0 3 2 6 7 12` and the sum of positions 2..5 being
`12 - 3 = 9`.

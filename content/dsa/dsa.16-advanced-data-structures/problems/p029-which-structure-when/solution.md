## Approach

Follow the function's branches in order; the first `return` reached is printed.

## Expected output

```text
1. highest price in [l, r), prices fixed: sparse table
2. sales total of [l, r), data fixed: prefix sums
3. distinct items in [l, r), all questions known: Mo's algorithm
4. stock edits one slot, total of [l, r): Fenwick tree
5. sensor edits one reading, lowest in [l, r): segment tree
6. bonus to a range of players, total of [l, r): two Fenwick trees
7. discount on a range of items, cheapest in [l, r): lazy segment tree
8. player joins or leaves, how many scores below x: Fenwick tree
```

## Why

| # | path through `choose` | why the structure fits |
|---|---|---|
| 1 | fixed, `max` is idempotent | sparse table: `O(1)` queries on static data |
| 2 | fixed, `sum` | prefix sums: `O(1)` with subtraction |
| 3 | fixed, not sum/min/max/gcd, offline | Mo's algorithm: add/remove one element is easy, merging halves is not |
| 4 | changes, point update, `sum` | Fenwick tree: sums have an inverse |
| 5 | changes, point update, `min` | segment tree: a minimum cannot be subtracted |
| 6 | changes, range update, `sum` | two Fenwick trees (p021) |
| 7 | changes, range update, `min` | lazy segment tree (range add + range min) |
| 8 | changes, point update, `count` | Fenwick tree over (compressed) scores |

**After you answer.**

2. "How many scores below `x`" is a prefix sum over a count per score. Scores up to 10**9 need **coordinate compression**: read all scores that can ever appear, sort them, and use their ranks as indices (chapter section 12).
3. Distinct values with questions arriving one at a time on fixed data: the function returns "segment tree", but a plain segment tree cannot merge "number of distinct values" of two halves. Online, you would need a persistent structure (beyond this module); if the questions can be read first, the offline Fenwick sweep of chapter section 17 or Mo's algorithm is the answer.

## Another way

Answer the scenarios from the chapter's decision questions directly, then check your answers by running the function; where you disagree with it, decide whether the function or you missed a property (static or not, idempotent, invertible, range update, offline).

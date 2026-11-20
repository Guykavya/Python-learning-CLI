## Hint 1

Draw the perfect heap of 15 items as a tree with 4 rows. In each row, write the **height** of its nodes (how many levels there are below them) and the **depth** (how many above). Row 1 has 1 node, row 2 has 2, row 3 has 4, row 4 has 8. Then compute the two sums: "number of nodes times height" and "number of nodes times depth".

## Hint 2

For question 4, build the series on paper: leaves cost 0 and are `n/2`; the next level is `n/4` nodes that cost at most 1; the next is `n/8` nodes that cost at most 2. Write the first four terms with `n = 1024`: `256*1 + 128*2 + 64*3 + 32*4 + ...`. The terms are `256, 256, 192, 128, 80, 48, ...`: after a few terms they shrink, because the number of nodes halves faster than the cost grows. Add the first ten terms: the total is already close to `n = 1024`, and it never goes much beyond it. The point is that the total is a fixed multiple of `n`, not `n` times `log n`.

For question 5, compare the two sums for 15 items (11 against 34) and then for 1,023 items (1,013 against 8,194).

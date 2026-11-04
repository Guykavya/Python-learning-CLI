## Hint 1

A question over the whole array (`l = 1`, `r = n`) makes `sum` touch all `n` elements. What if every question is like
that? Multiply.

## Hint 2

Building `p` is one addition per element. After that, each question reads two cells and subtracts once. So the total is
"building" plus "questions times a constant".

## Hint 3

For question 3, write `p[r]` and `p[l - 1]` as sums: `a[1] + ... + a[r]` and `a[1] + ... + a[l-1]`. Which terms cancel?
For question 5, think about which cells of `p` contain a changed element `a[i]`.

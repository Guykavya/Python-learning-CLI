## Hint 1

Many questions share most of their days. Instead of adding the same days again and again, can you add every day
once, in advance, and store the results?

## Hint 2

Build a list `before` of length `n + 1` with `before[0] = 0` and `before[k] = before[k - 1] + a[k - 1]`.
Then `before[k]` is the total of the first `k` days.

## Hint 3

Days `l` to `r` are "the first `r` days" minus "the first `l - 1` days": `before[r] - before[l - 1]`.

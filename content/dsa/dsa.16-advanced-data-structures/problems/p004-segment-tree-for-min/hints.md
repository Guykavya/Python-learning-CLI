## Hint 1

Only two things depend on the operation: the **combine** (`min` instead of `+`) and the **identity** returned for "no overlap". The identity must never win a minimum: `math.inf`.

## Hint 2

With `0` as the identity, every partial query that touches an "outside" node returns `min(..., 0)`. For positive data that is 0, which is not in the range at all (chapter section 5, "Why the identity matters").

## Hint 3

Copy the sum tree. Replace every `a + b` of two node values by `min(a, b)`, and the `return 0` of the no-overlap case by `return math.inf`. Fill the list with `math.inf` too.

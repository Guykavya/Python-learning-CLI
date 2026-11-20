## Hint 1

The tree is the same as for sum and min; only the combine (`math.gcd`) and the identity change. `gcd(0, x) = x` for every `x`, so `0` never changes a gcd: it is the identity.

## Hint 2

`gcd(gcd(x, y), z) = gcd(x, gcd(y, z))`: the gcd of a range does not depend on how you group it into blocks, which is exactly what the query does.

## Hint 3

Copy the tree of p003 and replace `+` by `math.gcd`. The list is filled with `0`, and the no-overlap case returns `0`.

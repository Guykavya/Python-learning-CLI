## Hint 1

The first `if` splits on `changes`. Scenarios 1 to 3 have `changes = False`; then only `op` (and for an unknown operation, `offline`) matters.

## Hint 2

Scenario 3 has `op = "distinct"`: not `"sum"`, not in `("min", "max", "gcd")`, and `offline = True`.

## Hint 3

For the changing data, `update == "range"` is tested first; inside it, only a sum goes to the two Fenwick trees. For point updates, `"sum"`, `"count"` and `"xor"` (operations with an inverse) go to the Fenwick tree, the rest to the segment tree.

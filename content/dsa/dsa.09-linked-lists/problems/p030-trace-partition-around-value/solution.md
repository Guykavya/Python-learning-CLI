## Approach

Classify each node in order: `val < 5` goes to the end of the small chain, anything else to the end of the big chain. The printed line comes after the node is added. Finally the small chain's tail is linked to the first big node.

## Expected output

```text
took 3 | small: 3 | big: empty
took 5 | small: 3 | big: 5
took 8 | small: 3 | big: 5 -> 8
took 5 | small: 3 | big: 5 -> 8 -> 5
took 10 | small: 3 | big: 5 -> 8 -> 5 -> 10
took 2 | small: 3 -> 2 | big: 5 -> 8 -> 5 -> 10
took 1 | small: 3 -> 2 -> 1 | big: 5 -> 8 -> 5 -> 10
result: 3 -> 2 -> 1 -> 5 -> 8 -> 5 -> 10
```

## Why

- Small values in arrival order: `3`, `2`, `1`. Big values (`>= 5`) in arrival order: `5`, `8`, `5`, `10`. The result is not sorted; it is only split, with each side in its original order (stable).
- `big_tail.next = None` matters: the last big node is `10`, which in the original list pointed at `2`. Without the cut, the result would run `... -> 10 -> 2 -> 1 -> 5 -> ...`, a cycle (`2 -> 1 -> 5 -> ... -> 10 -> 2`).
- If every value were small, `big.next` would be `None`, and `small_tail.next = big.next` ends the list correctly. The dummies make the empty sides need no special case.

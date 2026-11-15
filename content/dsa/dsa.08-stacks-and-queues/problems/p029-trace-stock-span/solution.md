## Approach

Each pair `(price, span)` stands for a block of `span` consecutive days whose prices are all at most `price`. A new price that is at least as high swallows the whole block in one pop, so we never look at single old days again.

## Expected output

```text
31 1 [(31, 1)]
41 2 [(41, 2)]
48 3 [(48, 3)]
59 4 [(59, 4)]
79 5 [(79, 5)]
20 1 [(79, 5), (20, 1)]
35 2 [(79, 5), (35, 2)]
35 3 [(79, 5), (35, 3)]
60 4 [(79, 5), (60, 4)]
```

## Why

- Rising prices: each one swallows the pair below it, so the span grows by one each day and only one pair is on the stack.
- `20` is lower than `79`: span 1, pushed on top.
- First `35`: swallows `(20, 1)` -> span 2.
- Second `35`: `35 <= 35`, so it swallows `(35, 2)` -> span 3. "At most today's price" includes equal prices, so the comparison is `<=`. With `<` the span would be 1 and the stack would hold two `35` pairs.
- `60`: swallows `(35, 3)` -> span 4; `79` stops it. Counting back: 60, 35, 35, 20 are all at most 60, and 79 is not: 4 days.

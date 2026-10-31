## Hint 1

Work through the specification one sentence at a time. For each sentence ask: "what would a wrong version do?" and write the test that tells the
two apart. Every number in the rules (5000, 1000, 499, 8%, "rounded down", "half up") has an edge: test the value just below it, exactly on it, and just
above it.

## Hint 2

Two helpers pay for themselves: a fixture `inv` with a few items in stock, and a fixture `cart` built with a small price table such as
`{"pen": 150, "book": 1200, "mug": 1000, "lamp": 4000}`. Pick items so that sums land exactly on the borders (lamp + mug = 5000).
For the all-or-nothing rule, put a good item **first** and an out-of-stock item **second**, then check that the first item's stock did not change.
Do not forget the second half of each error: the state must be unchanged.

```
inventory: add up, unknown -> 0, qty 0 and -1 rejected, remove exactly all, remove too much -> OutOfStock and unchanged
cart: merge same sku, qty 0/-1, unknown sku, remove missing, subtotal
discount_cents:  parametrize (4999, 5000, 5019 -> 501) for SAVE10, (999, 1000) for FIVER, None, unknown code
shipping_cents:  0, 1, 4999, 5000;   tax_cents: 0, 1000, 1006, 1007
checkout: whole receipts (exact dicts) at the borders: after-discount 4950 vs 5000; stock taken; cart emptied; failures change nothing; empty cart
```

## Hint 3

Compute each full receipt by hand: for `lamp + book + 2 pens` with `SAVE10`, subtotal 5500, discount 550, taxable 4950, shipping 499 (4950 is below 5000),
tax `(4950 * 8 + 50) // 100 = 396`, total 5845. Comparing the whole receipt dict at once catches wrong shipping, tax and discount together. Then
add the borders: lamp + mug (exactly 5000), with and without `SAVE10`.

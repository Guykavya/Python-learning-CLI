## Approach

| Statement | What happens | Counts after |
|---|---|---|
| 1 | customer 1 is deleted. `CASCADE`: orders 10 and 11 go, and so do their lines 1, 2, 3 (a second cascade). `SET NULL`: tickets 1 and 3 stay, with `customer_id = NULL` | customers 1, orders 1, lines 1, tickets 3, invoices 1 |
| 2 | order 12 is referenced by invoice 1 and the rule is `RESTRICT`: **error**, nothing changes | (error) |
| 3 | the invoice has no children: it is deleted | invoices 0 |
| 4 | no invoice blocks it now; `CASCADE` removes line 4 | orders 0, lines 0 |

The answer was produced by running exactly these statements.

`RESTRICT` is the right rule for invoices: an invoice is a legal record that must not disappear because someone deleted an order. A cascade would silently destroy it.

## Complexity

Not applicable.

## Another way

`ON DELETE NO ACTION` (the default) also refuses, but checks at the end of the statement (or transaction, if deferred); `RESTRICT` refuses at once.

## Why it matters

The `ON DELETE` rule decides what a single `DELETE` can destroy. Choose it per relationship: cascade for parts that mean nothing alone (lines of an order), `SET NULL` for optional links (tickets), `RESTRICT` for records you must keep.

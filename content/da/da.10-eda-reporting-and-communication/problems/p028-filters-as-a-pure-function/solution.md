## Approach

1. Paid customers in any plan and city: 1, 2, 6 -> 3 customers, panel rows 2 + 1 + 2 = 5.
2. Referral, 2-meal, Small: customer 5, who has **no** panel rows -> `None`.
3. Organic or referral, 3-meal, Metro: customers 7 and 8 -> 2 customers, 1 + 1 = 2 rows.
4. An empty channel list -> `None` before any filtering.

## Code

```text
3 5
None
2 2
None
```

## Complexity

Not applicable (a trace problem).

## Another way

Return an empty pair of tables instead of `None` and let the app check `len(pan) == 0`; `None` makes the "nothing to show" case impossible to miss in the calling code.

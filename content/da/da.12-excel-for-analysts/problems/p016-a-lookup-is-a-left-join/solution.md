## Approach

Compare the two mechanisms: first-match (lookup) and all matches (join), and tie them to the totals.

## Code

See `answer.md`.

## Complexity

Not applicable (an explain problem).

## Another way

Check uniqueness with `COUNTIF` in Excel and `validate="m:1"` in pandas **before** the join, so the problem is an error message and not a wrong total.

## Approach

The grain sentence comes before any code. The key tests it. The shape tells you the usual trap: entities change over time,
events repeat per entity, lines repeat the header, snapshots repeat the entity per date, aggregates cannot be taken apart again.

## Code

No code. A way to *test* each claim is `check_grain(df, key, name)` from problem 1.

## Complexity

Not applicable.

## Another way

Write the grain as a comment above each table at load time (`# grain: one row per job`) and test it with
`check_grain`; the comment and the test then disagree loudly the day the table changes.

## Hint 1

For `dflt`, which rows are "up to the current row" when two rows have the same `amount`? Do the peers of the current row count?

## Hint 2

Work the table by groups of equal `amount`: 10 | 20,20 | 30,30 | 40. For `dflt` and `cnt`, every row in a group gets the value at the end of its group.
For `by_rows`, rows are counted strictly one at a time in order (amount, id), so ties are split. `total` ignores order entirely.

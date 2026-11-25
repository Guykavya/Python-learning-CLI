# Check a pasted pivot

Chapter section 8.3. A PivotTable cannot be created or run offline, but **its numbers can be checked**: paste the pivot into a table and compare it with the pandas truth.

Write `check_pivot(expected, pasted, tol=1e-6)` for two DataFrames (rows and columns are labelled; the values are numbers). Normalise every row and column label with `str(label).strip().lower()`, and treat the labels `total` and `grand total` as the same label (`grand total`). Return a **list of strings**, in this order:

1. `row only in expected: <label>` for each row label only in `expected`, sorted;
2. `row only in pasted: <label>` for each row label only in `pasted`, sorted;
3. `column only in expected: <label>` and then `column only in pasted: <label>`, each sorted;
4. for each cell of the **common** rows and columns (rows in the order of `expected`, then columns in the order of `expected`) whose values differ by **more than `tol`** (absolute): `<row> / <column>: expected <e:,.2f>, pasted <g:,.2f>`.

Normalised labels appear in the messages. An empty list means the pivot matches.

## Example

If `North / kitchen` should be `1,200.00` and the pasted pivot has `1,150.50`, the message is `north / kitchen: expected 1,200.00, pasted 1,150.50`.

# Validate and normalise identifiers

Invoice ids were typed by hand into a spreadsheet, so they come in every shape:
`inv-  0042 `, `PO 7`, `Inv_123456`, `ab12`. Before importing them you must check each one and
write it in **one** standard form.

Write `normalise_ids(lines: list[str]) -> list[str]`.

A line is **valid** when, after stripping whitespace from both ends, it is exactly:

1. a prefix of **2 to 4 ASCII letters** (any case),
2. then optional spaces,
3. then **at most one** separator: `-`, `_` or `/`,
4. then optional spaces,
5. then **1 to 6 digits**.

A valid line is normalised as: prefix in UPPER case, then `-`, then the number padded with
leading zeros to **at least 4 digits** (longer numbers are kept as they are).

Return the normalised ids in input order, **skipping** invalid lines and **duplicates** (keep
the first occurrence of each normalised id).

**Example**

```python
normalise_ids(["inv-  0042 ", "PO 7", "Inv_123456", "ab12", "i-42", "inv--42", "INV-42"])
# ['INV-0042', 'PO-0007', 'INV-123456', 'AB-0012']
#  'i-42' has a 1-letter prefix, 'inv--42' has two separators,
#  'INV-42' is the same id as 'INV-0042' after normalising.
```

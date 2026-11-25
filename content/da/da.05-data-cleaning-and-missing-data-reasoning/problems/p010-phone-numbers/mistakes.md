- **`str.lstrip("91")`.** It strips *characters*, not a prefix: `"9123456789".lstrip("91")` removes the first two
  digits and every following 9 or 1. Use a pattern with `^`.
- **Always dropping a leading `91`.** `9123456789` is a valid number that happens to start with `91`.
- **Removing the prefix twice** (`0` then `91`). `0919876543210` has 13 digits; it is not a number with two prefixes.
- **Forgetting `na=False`** in `fullmatch` on a Series with missing values: without it, the Boolean mask contains
  missing values and `where` raises or behaves differently across versions.
- **Validating before cleaning.** `fullmatch` on `98765 43210` fails because of the space; normalise first.
- **Using `match` for validation.** `match` only anchors at the start: `98765432101234` would pass `\d{10}`. Use
  `fullmatch`.
- **Accepting first digits 0-5.** Mobile numbers here start with 6, 7, 8 or 9.

- Expecting `(?<=Rs\.|USD )` to work because each alternative is fixed. The rule is one width for
  the **whole** lookbehind; widths 3 and 4 differ.
- Expecting `(?<=Rs\.|USD)` to fail too. Both alternatives are 3 wide, so it is fine.
- Writing `['250', '40']` for line 5: the three characters before `40` are `SD `, not `USD`.
- Thinking `(?<=\w{3} )` is variable because of the braces. `{3}` is exactly three; only ranges
  like `{1,3}` are variable.
- Writing `['250', '40', '7', '5', '5']` for line 9: the `5` inside `15` has a digit before it, so
  `\b` does not match there.
- Thinking a character class like `[-$]` is two characters wide. A class always matches exactly
  one character.

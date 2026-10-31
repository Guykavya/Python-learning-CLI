- Writing `"\1"` in a normal string. Python turns `\1` into the character with code 1, so the
  pattern looks for that character. Always use raw strings: `r"(\w+)\s+\1"`.
- Leaving out the leading `\b`: `this is` is reported as `is`.
- Leaving out the trailing `\b`: `the theory` is reported as `the`.
- Using a literal space instead of `\s+`: the typo split across two lines is missed.
- Lower-casing the text first and then reporting from the lowered copy: the result should keep
  the original spelling (`The`).
- Returning `m.group(0)` (`'the the'`) instead of `m.group(1)`.

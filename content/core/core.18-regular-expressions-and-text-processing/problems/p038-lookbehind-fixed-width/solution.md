## Walkthrough

The text is `Rs.250 USD 40 $7 -15 5`. Its runs of digits are `250`, `40`, `7`, `15` and `5`.

1. `(?<=\$)\d+`: digits right after a `$`: only `7`.
2. `(?<=USD )\d+`: width 4 (`U`, `S`, `D`, space): `40`.
3. `(?<=Rs\.)\d+`: width 3: `250`.
4. `(?<=Rs\.|USD )\d+`: the alternatives have widths 3 and 4. Not one fixed width, so
   compiling fails: `re.error`.
5. `(?<=Rs\.|USD)\d+`: both alternatives have width 3, so it is allowed. Before `40` the three
   characters are `SD ` (with the space), not `USD`, so only `250`.
6. `(?:(?<=Rs\.)|(?<=USD ))\d+`: the standard work-around. Each lookbehind is fixed width on its
   own; the alternation is **outside** them: `['250', '40']`.
7. `(?<=\w{3} )\d+`: `{3}` is fixed (width 4 with the space). Only `USD ` qualifies: `40`.
8. `(?<=\s+)\d+`: `+` is not a fixed width: `re.error`.
9. `(?<!-)\b\d+`: a negative lookbehind, "not right after `-`". `250`, `40`, `7` and `5` pass.
   `15` is right after `-`. The engine then tries to start at `5` inside `15`, but `\b` fails
   there (between two digits), so no `5` from `15`.
10. `(?<=[-$])\d+`: a character class is one character wide, whatever it contains: `7` and `15`.

## The exact output

```text
(?<=\$)\d+ -> ['7']
(?<=USD )\d+ -> ['40']
(?<=Rs\.)\d+ -> ['250']
(?<=Rs\.|USD )\d+ -> re.error
(?<=Rs\.|USD)\d+ -> ['250']
(?:(?<=Rs\.)|(?<=USD ))\d+ -> ['250', '40']
(?<=\w{3} )\d+ -> ['40']
(?<=\s+)\d+ -> re.error
(?<!-)\b\d+ -> ['250', '40', '7', '5']
(?<=[-$])\d+ -> ['7', '15']
```

**Lesson:** a lookbehind needs one width. To accept several prefixes of different lengths, write
one lookbehind per prefix and put the `|` **outside**: `(?:(?<=Rs\.)|(?<=USD ))`. Or skip the
lookbehind and use a capturing group: `(?:Rs\.|USD )(\d+)`.

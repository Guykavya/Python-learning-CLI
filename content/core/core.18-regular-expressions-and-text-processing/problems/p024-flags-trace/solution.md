## Approach

For each line decide which flags are on, then what `^`, `$`, `.` and `\w` mean with them.

## Line by line

1. No flags: `^` only at index 0, so only `Apple`.
2. MULTILINE: `^` at the start of every line: the first word of each.
3. No flags: `$` only at the end of the string: `tart`.
4. MULTILINE: `$` before every `\n` and at the end: the last word of each line.
5. `^[a-z]` with MULTILINE: only `banana` starts with a small letter.
6. Add IGNORECASE: all three first words.
7. `.` does not match `\n` without DOTALL, so `pie.banana` fails: `None`.
8. With DOTALL the `.` takes the newline: repr shows `'pie\nbanana'`.
9. `"a\nb"` has 3 characters. Without DOTALL `.` skips the newline (2 matches); with it, 3.
10. `(?i)` at the start turns IGNORECASE on for the whole pattern: `Cherry`.
11. `(?m)t$`: lines ending in `t` are `banana split` and `Cherry tart`.
12. Normal (Unicode) `\w` treats `é` and `ï` as letters: two whole words.
13. With ASCII, `é` and `ï` are not word characters, so the words split there: `caf`, `na`, `ve`.
14. `p` was compiled with `re.I | re.M`: the I bit is set, the S bit is not.

## Expected output

```
['Apple']
['Apple', 'banana', 'Cherry']
['tart']
['pie', 'split', 'tart']
['banana']
['Apple', 'banana', 'Cherry']
None
'pie\nbanana'
2 3
['Cherry']
['t', 't']
['café', 'naïve']
['caf', 'na', 've']
True False
```

## Complexity

Every call is linear in the text length.

## Another way

Inline flags can also apply to **part** of a pattern: `(?i:cherry) Tart` matches `CHERRY Tart`
but not `cherry tart`. That is handy when only one word should ignore case.

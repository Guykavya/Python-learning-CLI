## Approach

Take the four strings and ask, for each call, "plain or pattern?".

1. Plain `.`: only `a.b` has a dot, so the result is `['ab', '1+1', 'x2y3', '211']`.
2. Pattern `.`: every character is "any character", so everything is removed: `['', '', '', '']`.
3. Plain `1+1` (three characters in a row): only the string `1+1` contains it: `[False, True, False, False]`.
4. Pattern `1+1` means one or more `1`, then a `1`, i.e. at least two `1`s in a row. `1+1` has two `1`s but a plus sign
   between them, so no; `211` contains `11`, so yes: `[False, False, False, True]`.
5. `\d` counts digits: 0, 2, 2, 3 digits: `[0, 2, 2, 3]`.
6. Digits replaced by `#`: `['a.b', '#+#', 'x#y#', '###']`.
7. Pattern `.` matches in all four non-empty strings (4); plain `.` only in `a.b` (1). The line prints `4 1`.

```text
['ab', '1+1', 'x2y3', '211']
['', '', '', '']
[False, True, False, False]
[False, False, False, True]
[0, 2, 2, 3]
['a.b', '#+#', 'x#y#', '###']
4 1
```

## Complexity

Not applicable. The cost of this confusion is not speed but a silently wrong column.

## Another way

Make the intention explicit: `regex=False` when you search for a literal piece of text, or write `\.` and `\+` in a
pattern. `re.escape(text)` turns any text into a pattern that matches it literally, which is what you need when the text
comes from a user or a file. (In a pattern like `"+1"` that starts with a special character, some pandas versions raise
an error and some do not, depending on the string engine, so this problem avoids it. The lesson is the same: say what
you mean.)

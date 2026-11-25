## Hint 1

For each call first decide: is the first argument plain text or a pattern? Plain text matches exactly those characters
in a row. A pattern uses the special meaning: `.` any one character, `1+` one or more `1`s, `\d` a digit. Then apply it
to the four strings one by one.

## Hint 2

```text
strings:  "a.b"   "1+1"   "x2y3"   "211"
line 1: plain "."        -> remove only the real dot characters
line 2: pattern "."      -> every character matches, so every string becomes ""
line 3: plain "1+1"     -> True only where the three characters 1 + 1 appear in a row
line 4: pattern "1+1"    -> "one or more 1, then a 1" = at least two 1s in a row ("11" or "111" ...)
line 5: count digits in each string
line 6: each digit replaced by #
line 7: pattern "." is True for every non-empty string; plain "." only where a dot appears
```

- Passing `str(int(...) * 2)` as the **replacement string**. It is computed once, before
  `re.sub` runs, and fails because there is no match yet. Pass the function itself, without `()`.
- Returning an `int` from the replacement function. `re.sub` needs a string: `TypeError`.
- Using a plain `\d+`. It changes `mp3` to `mp6` and `2.5` to `4.10`.
- Over-thinking the minus sign. For doubling, `-` can stay outside the match. Adding `-?` to
  the pattern is harmless here but matters for other operations (adding, rounding).
- Using `\b` instead of the lookarounds. `\b` is happy between `.` and `5`, so the decimal `2.5`
  is still split.
- Rejecting every number followed by `.`: then `buy 7.` at the end of a sentence is missed.

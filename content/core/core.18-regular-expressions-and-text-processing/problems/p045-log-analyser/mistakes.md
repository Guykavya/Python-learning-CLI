- Writing a plain space in a `re.VERBOSE` pattern: it is ignored, so the date and time would have
  to be glued together. Use `\x20`, `\ ` or `[ ]` (or `\s+` where the format allows several).
- Using `\w+` for the level: `VERBOSE` and `INFORMATION` would be accepted.
- Using `search` or `match` instead of `fullmatch`: junk at the end of a line (or before a date)
  would be silently ignored.
- `\[(?P<module>.*)\]` with a greedy `.*`: on `[notifications.email] Sent 12 emails: [ok]` the
  module runs to the **last** `]`. Use `[\w.]+` (or `[^\]]+`).
- Forgetting that `(?P<message>...)` is `None` when the optional part is missing, and calling
  `.strip()` on `None`.
- Counting blank lines as unparsed, or numbering lines from 0.
- Counting `CRITICAL` in the top ERROR list, or sorting ties with `most_common` (first-seen order)
  instead of by name.
- Writing `\d{4}` inside an `rf"..."` string: the f-string treats `{4}` as an expression and puts
  the number 4 there, so the pattern becomes `\d4`. Double the braces or do not use an f-string.
- Leaving `WARN` as `WARN`: the summary would then count two different warning levels.

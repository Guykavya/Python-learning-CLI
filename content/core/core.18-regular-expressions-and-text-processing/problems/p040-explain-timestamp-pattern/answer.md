**1. Piece by piece.**

- `\A` the match must start at the very beginning of the string.
- `(?P<year>\d{4})` exactly four digits, any four.
- `-` a literal hyphen (spaces around it are ignored in verbose mode).
- `(?P<month>0[1-9]|1[0-2])` `01` to `09` or `10` to `12`. `\d\d` would also allow `00`, `13`
  or `99`. Splitting the range into alternatives is the regex way of saying "a number from 1 to
  12": a regex compares characters, not numbers. The alternation stays inside the group, so it
  does not split the whole pattern.
- `(?P<day>0[1-9]|[12]\d|3[01])` `01`–`09`, `10`–`29`, `30`–`31`.
- `[T\x20]` one `T` or one space.
- `(?P<hour>[01]\d|2[0-3])` `00`–`19` or `20`–`23`, so `24` is rejected.
- `:` and `(?P<minute>[0-5]\d)` `00`–`59`.
- `(?: : (?P<second>[0-5]\d) (?: \. (?P<fraction>\d{1,6}) )? )?` a non-capturing optional
  block: either nothing, or `:ss`, optionally followed by `.` and 1 to 6 digits. The fraction is
  nested **inside** because it only makes sense after seconds: `09:15.5` must be rejected. `\.` is
  escaped, so it is a real dot.
- `(?P<tz> Z | [+-] (?:[01]\d|2[0-3]) :? [0-5]\d )?` an optional time zone: `Z`, or a sign, hours
  `00`–`23`, an optional colon, minutes. So `+05:30` and `+0530` both work, glued directly to the
  time.
- `\Z` the match must end at the very end of the string.

**2. Verbose details.** With `re.VERBOSE`, whitespace in the pattern is ignored (outside a
character class) and `#` starts a comment. That is why `\d{4}) - (?P<month>` is fine: the spaces
are layout, not part of the pattern. Inside `[...]` Python actually keeps a plain space, but
`\x20` (the character code of a space) makes the intent obvious to a reader, and keeps working if
someone later moves it outside a class. A literal space outside a class must always be written as
`\x20`, `\ ` or `[ ]`, or it silently disappears.

**3. The eight inputs.**

- `2025-03-01T09:15` matches; `second`, `fraction` and `tz` are `None`.
- `2025-03-01 09:15:02.5+05:30` matches (space separator); every group is filled:
  `fraction='5'`, `tz='+05:30'`.
- `2025-02-31T23:59:59Z` **matches**, `fraction` is `None`, `tz='Z'`.
- `2025-03-01T24:00` fails at the hour: `2[0-3]` does not allow `24`.
- `2025-03-01T09:15.5` fails: after the minutes the optional seconds block needs `:`. It is
  skipped, then the time zone cannot start with `.`, and `\Z` is not at `.`.
- `2025-3-01T09:15` fails at the month: `3` is one digit, the month needs two.
- `'2025-03-01T09:15:02Z\n'` fails at `\Z`: a newline is left over.
- `2025-03-01 09:15:02 +0530` fails: the time zone must follow the time directly; the space before
  `+` is not allowed.

**4. Limits.** `2025-02-31` (31 February) is accepted: the day part only knows "01 to 31", not
which month has how many days, and leap years are worse. Do the shape check with the regex, then
the meaning check in code: convert the groups with `int()` and build
`datetime(year, month, day, ...)`, which raises `ValueError` for impossible dates. Or use
`datetime.fromisoformat(s)` directly.

**5. Anchors.** `$` matches at the end **or just before a final newline**, so `^...$` would
accept `'2025-03-01T09:15:02Z\n'`. `\Z` means only the true end of the string. (`\A` and `^`
are the same without `re.MULTILINE`, but `\A` can never be changed by a flag.) `fullmatch`
would do the same job as the two anchors.

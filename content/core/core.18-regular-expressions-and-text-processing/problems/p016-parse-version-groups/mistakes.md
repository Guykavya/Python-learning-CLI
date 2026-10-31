- Using `re.match` or `re.search`. Both accept `1.2.3.4` and `1.2.3-beta` because a prefix or a
  piece of the string fits. Validation means `re.fullmatch` (or `^...$` with care).
- Writing `.` instead of `\.`. The dot is a metacharacter: `1x2x3` would pass.
- Returning `m.groups()` directly. It is a tuple of **strings**: `('1', '2', '3')`, not `(1, 2, 3)`.
- Putting the `v` inside a group, `([vV]?\d+)`. Then the first part is `'v1'` and `int('v1')` crashes.
- Using `\d*` instead of `\d+`, which lets `1..3` through with an empty middle part.
- Forgetting to strip, so a line read from a file with its `\n` never matches.

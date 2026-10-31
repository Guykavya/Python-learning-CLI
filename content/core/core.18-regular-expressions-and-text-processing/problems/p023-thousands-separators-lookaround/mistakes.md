- Leaving out `$` in the lookahead. Then every gap with three digits somewhere ahead gets a
  comma: `1,2,3,4,567`.
- Leaving out the lookbehind. `123` becomes `,123` and `-123` becomes `-,123`.
- Using `\B` instead of `(?<=\d)`. It works for these inputs, but it relies on `-` being a
  non-word character; `(?<=\d)` says exactly what you mean.
- Matching three digits and replacing with `\1,` (consuming them). Matching goes left to right,
  so the groups come out from the **left**: `123,456,7`.
- For Indian grouping, writing `(?:\d\d)+\d{3}`. The `+` needs at least one pair, so the comma
  before the last three digits is lost: `12345` stays `12345`.

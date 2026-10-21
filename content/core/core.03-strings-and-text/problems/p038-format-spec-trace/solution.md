## Walkthrough

| Code | Output | Why |
|---|---|---|
| `{x:10.1f}` | `[    1234.5]` | 6 characters right-aligned in 10 |
| `{x:<10,.2f}` | `[1,234.50  ]` | 8 characters with comma, left-aligned |
| `{n:^7}` | `[  42   ]` | 5 spaces: 2 left, 3 right |
| `{n:*>6}` | `[****42]` | fill `*`, right-aligned |
| `{-n:06}` | `[-00042]` | zeros go after the sign |
| `{n:+}`, `{n: }` | `[+42] [ 42]` | `+` always signs; space signs negatives and pads positives |
| `{n:b} {n:#o} {n:X}` | `101010 0o52 2A` | bases, with a prefix only for `#` |
| `{0.0625:.1%}` | `6.2%` | 6.25 rounds half to even |
| `{x:.2e}` | `1.23e+03` | 1.2345 rounded to 2 decimals |
| `{'format':.3}`, `{'ab':>{n // 10}}` | `[for] [  ab]` | precision cuts a string; nested width 4 |
| `{n=}, {x / 10 = :.0f}` | `n=42, x / 10 = 123` | the `=` form keeps the spaces you typed |

## The surprising one

`0.0625` is exactly representable in binary, so `6.25` is a true tie, and ties round to even: `6.2`. Formatting uses the same rule as `round()`.

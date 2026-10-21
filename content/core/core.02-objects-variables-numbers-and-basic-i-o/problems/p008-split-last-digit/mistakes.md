- Using `/` instead of `//`: `1234 / 10` is `123.4`, a float.
- Writing `n % 10 // 10` for the second digit. That is `4 // 10`, which is `0`. Order matters.
- Expecting this to work on negative numbers. `-1234 % 10` is `6`, not `4`, because `%`
  follows the sign of the divisor. Use `abs(n)` first if negatives are possible.

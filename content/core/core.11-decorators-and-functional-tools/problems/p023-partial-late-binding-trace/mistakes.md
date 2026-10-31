- Expecting `[2, 4, 8]` from the lambdas. A closure stores the variable, not its value at the
  time the lambda was created.
- Expecting `lambdas[0](2)` to still be 8 after `e = 10`. The lambda reads `e` again on every call.
- Thinking `partial` also reads `e` late. `partial(...)` is an ordinary call, so its arguments
  are evaluated right away.
- Thinking a keyword given at call time is an error because `exp` is already set. It just
  overrides the stored one.
- Writing `cube_of_3(2)` as `2 ** 3 = 8`. `partial(power, 3)` fills the first parameter, `base`.

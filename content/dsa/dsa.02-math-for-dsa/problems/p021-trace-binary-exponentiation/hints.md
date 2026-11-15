## Hint 1

Do the first pass carefully. `base = 3`, `exp = 13`, `result = 1`. Is 13 odd? Then `result` becomes `1 * 3`. The new
`base` is `3 * 3`, and the new `exp` is `13 // 2`.

## Hint 2

The printed line is the state **before** the pass changes anything. So the first printed line is always
`base exp 1` (with `base` already reduced modulo `mod`). The state printed on line 2 is what pass 1 left behind.

## Hint 3

For the last call, `base = 10 % 1 = 0`. What is `x % 1` for every `x`? Then ask what the loop does with a base of 0.

## Hint 1

For each `t`, the `if`/`elif`/`else` chain prints exactly one line. The two separate `if`s
after it are independent: each may print or not.

## Hint 2

40 is `> 30`, so it is `hot`. Is it also `> 20`? Does that matter for the chain? Does it
matter for the separate `if t > 20`?

## Hint 3

`code == "a" or "c"` is `(code == "a") or "c"`. What is the truthiness of `"c"`?

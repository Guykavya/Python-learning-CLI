## Hint 1

Is `"   "` truthy or falsy? What about `"   ".strip()`?

## Hint 2

Strip first and keep the result in a variable. Then `if not text:` means "nothing left".

## Hint 3

`text.endswith("!")` tells you whether to add the `!`. A conditional expression can pick
between `""` and `"!"`.

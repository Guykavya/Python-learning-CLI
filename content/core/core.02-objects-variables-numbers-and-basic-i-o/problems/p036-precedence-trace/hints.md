## Hint 1

From tightest to loosest: `**`, unary `-`, `* / // %`, `+ -`, `<< >>`, `&`, `^`, `|`,
comparisons, `not`, `and`, `or`.

## Hint 2

`**` groups from the **right**: `2 ** 3 ** 2` is `2 ** (3 ** 2)`. Every other arithmetic operator groups from the left.

## Hint 3

Comparisons chain: `a > b == c` means `a > b and b == c`. It does not mean `(a > b) == c`.

## Hint 1

First call: `i = 0`, `j = 5`, so the first sum is `1 + 11 = 12`. Is that bigger or smaller than 10? Which pointer moves?

## Hint 2

The `found` line is printed and then `return (i, j)` hands back a tuple; `print` shows it as `(2, 3)`. When the loop
ends without a match, the function returns `None`, and `print(None)` prints `None`.

## Hint 3

Second call: the sums are `2 + 14`, then `2 + 9`, then `5 + 9`. After the third step `i` and `j` are both 1.

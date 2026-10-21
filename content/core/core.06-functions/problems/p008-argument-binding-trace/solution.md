## Walkthrough

| Call | a | b | c |
|---|---|---|---|
| `order(1)` | 1 | 2 (default) | 3 (default) |
| `order(1, 5)` | 1 | 5 | 3 (default) |
| `order(1, c=9)` | 1 | 2 (default) | 9 |
| `order(c=1, a=2)` | 2 | 2 (default) | 1 |
| `order(7, 8, 9)` | 7 | 8 | 9 |

For `tag`, the defaults are `"["`, `"]"` and an empty `sep`. `tag("hi", sep=" ")` puts a space
on each side of the text, inside the brackets. In the last call every argument is a keyword, in
an unusual order, and binding matches them by name.

## The exact output

```text
a = 1 b = 2 c = 3
a = 1 b = 5 c = 3
a = 1 b = 2 c = 9
a = 2 b = 2 c = 1
a = 7 b = 8 c = 9
[hi]
<hi>
[ hi ]
{hi}
(-x-)
```

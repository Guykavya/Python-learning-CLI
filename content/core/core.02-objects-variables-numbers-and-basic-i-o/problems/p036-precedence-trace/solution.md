## Walkthrough

| Expression | Grouped | Result |
|---|---|---|
| `-2 ** 2` | `-(2 ** 2)` | `-4` |
| `2 ** 3 ** 2` | `2 ** 9` | `512` |
| `2 + 3 * 4 ** 2` | `2 + (3 * 16)` | `50` |
| `10 - 4 - 3` | `(10 - 4) - 3` | `3` |
| `2 ** -1` | the `-` binds to the `1` on the right | `0.5` (a negative power gives a float) |
| `not 1 == 2` | `not (1 == 2)` | `True` |
| `1 + 2 == 3 and 4 > 5` | `(3 == 3) and (4 > 5)` | `False` |
| `True + True * 3` | `1 + (1 * 3)` | `4` |
| `6 & 3 \| 8` | `(6 & 3) \| 8` = `2 \| 8` | `10` |
| `1 << 2 + 1` | `1 << 3` | `8` |
| `7 // 2 * 2` | `(7 // 2) * 2` = `3 * 2` | `6` |
| `-7 // 2 * 2` | `(-7 // 2) * 2` = `-4 * 2` | `-8` |
| `1 < 2 < 3 == 3` | `1 < 2 and 2 < 3 and 3 == 3` | `True` |
| `3 > 2 == True` | `3 > 2 and 2 == True` | `False`, because `2 == True` is `2 == 1` |

## The rule

When unsure, add brackets. They cost nothing and make your intent clear to the next reader.

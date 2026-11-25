# Derivatives by the rules

Chapter section 6.4. Write `derivative_of(name)` that returns the **derivative function** (by hand, no numerical tricks) for these six functions:

| name | f(x) | f'(x) |
|---|---|---|
| `"poly"` | `x^3 - 2x` | |
| `"exp2x"` | `exp(2x)` | |
| `"log"` | `log(x)` for `x > 0` | |
| `"sigmoid"` | `1 / (1 + exp(-x))` | |
| `"product"` | `x * sin(x)` | |
| `"chain"` | `sin(x^2)` | |

For an unknown name raise `KeyError`. The test compares your derivatives with a numerical derivative at 20 points.

## Example

```text
derivative_of("poly")(2.0)   ->  10.0        (3 x^2 - 2 at x = 2)
derivative_of("log")(4.0)    ->  0.25
```

## Hint 1

`floor` always goes **down** (towards minus infinity), `ceil` always goes **up**, `trunc` (and
`int()`) cut off the fraction, which means going **towards zero**. For `-2.5`, which way is
"down"? Which of the three is what `round_down_to` needs?

## Hint 2

`math.ceil(n / per_page)` looks right, but `/` makes a float, and a float has only about 16
significant digits: `float(10**17 + 1)` is `1e17`. Can you do a ceiling division with `//`
only? (`//` floors. What is `-(-10 // 3)`?)

## Hint 3

```
floor_ceil_trunc: return floor(x), ceil(x), trunc(x)
pages_needed:     validate; return -(-n_items // per_page)
round_down_to:    validate; return floor(x / step) * step
close_enough:     return isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
```
`isclose` with only `rel_tol` compares the difference to a fraction of the bigger value; next to
`0.0` that fraction is `0`, so nothing is ever close to zero without `abs_tol`.

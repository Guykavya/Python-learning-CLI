## Hint 1

Start with the functions you already wrote in problems 1, 2, 4, 9, 10, 12, 15, 18, 20, 27, 33, 41, 47, 55, 56 and 58, and adapt the signatures to the table. The new pieces are `t_cdf` and `t_ppf`.

## Hint 2

`t_cdf(x, df)`: the density is `c (1 + t^2 / df)^(-(df+1)/2)` with `c = exp(lgamma((df+1)/2) - lgamma(df/2)) / sqrt(df pi)`; integrate it from 0 to `|x|` with the trapezoid rule on 2001 points and add 0.5 (use the sign of `x`). `t_ppf` is a bisection on `t_cdf` between -200 and 200.

## Hint 3

The functions that call each other: `mean_ci` needs `t_ppf` needs `t_cdf`; `welch_t` needs `t_cdf`. Write and test them in that order.

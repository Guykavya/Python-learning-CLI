## Hint 1

For `y = x^2` on -3..3 the products `(x - mean_x)(y - mean_y)` come in matching positive and negative pairs. For the other two, compute `Sxy`, `Sxx`, `Syy` with the means 3 and 12 (second case) and 3 and 12.4 (third case).

## Hint 2

```text
case 1: x symmetric around 0, y = x^2 -> sum of x * (y - 4) = 0 -> r = 0.000
case 2: dx = -2..2, dy = -10,-8,-6,-4,28 -> Sxy = 80, Sxx = 10, Syy = 1000 -> r = 80 / sqrt(10 * 1000) = 0.800 ; the ranks are 1..5 on both sides -> 1.000
case 3: y = 2,4,8,16,32, mean 12.4, Sxy = 72, Syy = 595.2 -> r = 72 / sqrt(10 * 595.2) = 0.933 ; ranks identical -> 1.000
```

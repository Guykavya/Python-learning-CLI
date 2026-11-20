## Hint 1

Program 1: three nested loops of 150 = `150**3`. Program 2: `10**5 * 10**5`. Compare each with `2 * 10**7`.

## Hint 2

Program 3: the inner `while` doubles `j` until it reaches `n`: about `log2(n)` steps per `i`. Program 4: `n + (n-1) + ... + 1 = n(n+1)/2`.

## Hint 3

Program 5 (sieve) inner steps sum to about `n * ln ln n`, which is a few million for `n = 10**6`; the outer loop adds `10**6`. Program 6: `j` takes `n / i` values for every `i`, so the total is `n * (1 + 1/2 + 1/3 + ... + 1/n)`, about `n * ln n`.

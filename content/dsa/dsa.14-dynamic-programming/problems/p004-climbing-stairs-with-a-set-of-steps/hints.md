## Hint 1

`f(i)` = the number of move sequences that end exactly on step `i`. Group them by their **last** move `s`: the part before it is any sequence that ends on step `i - s`. So `f(i)` is a sum over the steps. Which steps are allowed in that sum? What is `f(0)`?

## Hint 2

This is `coin_sequences` from chapter section 7 (amounts outside, steps inside), because order matters. Take `% (10**9 + 7)` after every addition.

## Hint 3

```
f = [0] * (n + 1)
f[0] = 1
for i in 1..n:
    for s in steps:
        if s <= i:
            f[i] = (f[i] + f[i - s]) % M
return f[n]
```

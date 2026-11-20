## Hint 1

`f(i)` = the number of ways to decode the first `i` characters `s[:i]`. The last piece is either one digit, `s[i-1]`, or two digits, `s[i-2:i]`. If the one-digit piece is valid, each decoding of `s[:i-1]` extends to one of `s[:i]`. The same for two digits with `s[:i-2]`. When is each piece valid?

## Hint 2

One digit is valid if it is not `"0"`. Two digits are valid if `10 <= int(s[i-2:i]) <= 26` (this also rejects `"06"`, which is 6 as a number). Add the counts of the valid choices; `f(0) = 1`.

## Hint 3

```
f = [0] * (n + 1); f[0] = 1
for i in 1..n:
    if s[i-1] != "0":                         f[i] += f[i-1]
    if i >= 2 and 10 <= int(s[i-2:i]) <= 26:  f[i] += f[i-2]
return f[n]
```

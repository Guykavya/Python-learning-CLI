## Hint 1

Fill in this table by hand (each sum is the previous sum plus or minus `n`):

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| sum | 1 | -1 | ? | ? | ? | ? | ? | ? |

Now look only at the even `n` columns. Then only at the odd ones. What do you notice?

## Hint 2

Group the terms in pairs: `(1 - 2) + (3 - 4) + ...`. Each pair is `-1`. For even `n` there are `n / 2`
pairs. For odd `n`, there are `(n - 1) / 2` pairs and one extra `+n` at the end.

## Hint 3

```
read n
if n is even: answer = -(n // 2)
else:         answer = (n + 1) // 2
print answer
```

Use `//`, not `/`. `/` gives a float, and floats cannot hold every whole number up to 10^18 exactly.

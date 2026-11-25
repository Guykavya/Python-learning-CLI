## Hint 1

What shape does `a[:, None, :]` have, and `b[None, :, :]`? Predict the shape of their difference with the rules of Ch. 11.2. Which axis holds the coordinates, and which axis must you sum over?

## Hint 2

```text
a, b = float arrays;  if a.shape[1] != b.shape[1]: raise ValueError
diff = a[:, None, :] - b[None, :, :]        # (n, m, d)
return sqrt((diff ** 2).sum(axis=-1))       # (n, m)
```

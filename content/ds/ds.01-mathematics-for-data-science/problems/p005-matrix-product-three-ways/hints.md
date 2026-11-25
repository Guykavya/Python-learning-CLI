## Hint 1

How many rows does `C` have, and how many columns? For one entry `C[i][j]`, which `n` numbers do you multiply and add?

## Hint 2

```text
check A.shape[1] == B.shape[0]
C = zeros((m, p))
for i in range(m):
    for j in range(p):
        for k in range(n): C[i][j] += A[i][k] * B[k][j]
```

## Approach

`[1, 0] -> [2, 1]/sqrt(5)`, then multiply again and normalise; the entries creep towards `0.707`.

## Answer

```text
step 1: 0.894 0.447
step 2: 0.781 0.625
step 3: 0.733 0.680
2.997
```

## Another way

After 50 steps the vector is `[0.707, 0.707]` and the eigenvalue is `3.000`.

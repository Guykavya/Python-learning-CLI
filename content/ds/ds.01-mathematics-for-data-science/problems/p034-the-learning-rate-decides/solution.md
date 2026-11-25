## Approach

Each step multiplies `w` by `1 - 2 lr`: 0.8, 0, -1, -1.2.

## Answer

```text
lr=0.1: 0.8000 0.6400 0.5120 0.4096
lr=0.5: 0.0000 0.0000 0.0000 0.0000
lr=1.0: -1.0000 1.0000 -1.0000 1.0000
lr=1.1: -1.2000 1.4400 -1.7280 2.0736
```

## Another way

Convergence needs `|1 - 2 lr| < 1`, that is `0 < lr < 1`; for a general bowl the limit is `2 / (largest Hessian eigenvalue)`.

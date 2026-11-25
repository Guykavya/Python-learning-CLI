## Approach

`k = 0` gives `p = 0`, `se = 0`: Wald is a single point. Wilson keeps `z^2 / 4n^2` under the root, so it has width.

## Answer

```text
Wald: (0.000, 0.000) width 0.000
Wilson: (0.000, 0.161) width 0.161
```

## Another way

The 'rule of three' says that with 0 successes in `n` trials the 95% upper limit is about `3 / n` (here 0.15), close to Wilson's 0.161.

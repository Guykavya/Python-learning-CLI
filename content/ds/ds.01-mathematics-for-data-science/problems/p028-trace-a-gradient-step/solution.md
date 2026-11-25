## Approach

Two updates: `0 -> 0.6 -> 1.08`. The values of `f` fall: `9 -> 5.76 -> 3.6864`.

## Answer

```text
step 1: w=0.6000 f=5.7600
step 2: w=1.0800 f=3.6864
```

## Another way

Each step shrinks the distance to 3 by the factor `1 - 2 lr = 0.8`; with `lr = 1.0` the factor is `-1` and `w` would jump between 0 and 6 forever.

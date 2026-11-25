## Approach

`h = 0.1`: error 0.1, `large`. `h = 1e-5`: error 1e-5, `medium`. `h = 1e-8`: error about 1e-8, `small`. `h = 1e-15`: `1 + h` rounds to a nearby double, the quotient is about 2.22, error 0.22, `large`.

## Answer

```text
h=1e-01: large
h=1e-05: medium
h=1e-08: small
h=1e-15: large
```

## Another way

Central differences have truncation error about `h^2`, so their best `h` is near `1e-5`.

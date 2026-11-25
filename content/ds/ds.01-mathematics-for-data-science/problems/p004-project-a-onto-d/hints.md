## Hint 1

If `d` had length 1, the shadow would be `(a . d) * d`. What do you divide by when `d` is longer?

## Hint 2

```text
scale = (a . d) / (d . d)
return scale * d
```
`d . d` is the squared length of `d`.

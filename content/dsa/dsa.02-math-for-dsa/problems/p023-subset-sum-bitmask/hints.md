## Hint 1

How do you turn `mask` into a subset? Test bit `i` with `(mask >> i) & 1`. The sum of the subset is the sum of the
`a[i]` with that bit set.

## Hint 2

Doing that for every mask costs `18 * 262144`, which is about 4.7 million steps. It works, but there is a faster way.
`mask & (mask - 1)` is the same subset without its lowest element. If you stored the sum of that smaller mask earlier,
the sum of `mask` is that sum plus one element.

## Hint 3

```
sums = [0] * (1 << n)
for mask in 1 .. (1 << n) - 1:
    low = mask & -mask                  # the lowest set bit, as a number
    i = low.bit_length() - 1            # its position
    sums[mask] = sums[mask ^ low] + a[i]
answer = how many sums equal t
```

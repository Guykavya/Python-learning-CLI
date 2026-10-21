# Powers of two with bit tricks

Read a positive whole number `n` (it can be very large). Print three lines:

1. `True` if `n` is a power of two (1, 2, 4, 8, ...), else `False`
2. how many bits `n` needs in binary (`n.bit_length()`)
3. the largest power of two that is less than or equal to `n`

**Example**

Input:
```
40
```
Output:
```
False
6
32
```

Hint about the first line: a power of two has exactly one 1 bit. Look at what `n - 1` looks like in binary.

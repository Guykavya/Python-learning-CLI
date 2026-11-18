## Hint 1

`sorted(freq)` is `['a', 'b', 'c', 'd', 'e', 'r']`, so the starting entries are:

```text
(3, 0, 'a')  (1, 1, 'b')  (2, 2, 'c')  (1, 3, 'd')  (3, 4, 'e')  (2, 5, 'r')
```

The first two pops are the two entries of weight 1. Which one is `t1` (left)?

## Hint 2

After round 1 the heap holds `a(3,0) c(2,2) e(3,4) r(2,5)` and the new tree `bd` with `(2, 6)`. Three entries weigh 2: compare their tie numbers 2, 5 and 6. In round 3, the entries of weight 2 and 3 are left over: `bd(2, 6)` is the only weight 2, and of the two weight-3 letters, `a` has the smaller tie number.

## Hint 3

The final tree is `((b, d), a)` on the left and `(e, (c, r))` on the right:

```text
              (12)
            0/    \1
          (5)      (7)
        0/  \1   0/   \1
      (2)    a   e    (4)
    0/  \1           0/  \1
    b    d           c    r
```

Read each code from the root. The cost is the sum of `weight * code length`, which also equals the sum of all join weights.

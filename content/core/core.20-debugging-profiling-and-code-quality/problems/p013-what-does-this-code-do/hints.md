## Hint 1

Run it by hand on `[2, 4, 6, 8, 10]` with `k = 2` and write down `i`, `w` and `r` at the
start of each loop step. Which slice of `xs` does `w` add up to each time? How many windows of
2 neighbours does a list of 5 values have?

## Hint 2

```
start:  w = sum(xs[0:2]) = 6
i=2:    append 6/2;   w = 6 + xs[2] - xs[0] = 10   (window [4, 6])
i=3:    append 10/2;  w = 10 + 8 - 4 = 14          (window [6, 8])
i=4:    append 14/2;  w = 14 + 10 - 6 = 18         (window [8, 10])
end:    w = 18 is never appended  ->  ?
```

Now try `k = 0` and `k = 5` the same way.

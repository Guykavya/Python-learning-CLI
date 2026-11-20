## Hint 1

Write the total for an order `d1, d2, ..., dn`: job 2 waits `d1`, job 3 waits `d1 + d2`, and so on. How many times is `d1` counted in the total? And `dn`? Which job should therefore be the shortest?

## Hint 2

`d1` is counted `n - 1` times, `d2` is counted `n - 2` times, ..., `dn` never. To make the total small, the job counted most often should be the shortest: sort ascending. Then add up the waits with a running `elapsed`, adding it to the total **before** adding the job's own duration.

## Hint 3

```
wait = 0; elapsed = 0
for d in sorted(durations):
    wait += elapsed
    elapsed += d
return wait
```

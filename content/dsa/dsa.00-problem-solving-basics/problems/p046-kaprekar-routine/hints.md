## Hint 1

If you know that `3087` contains one 8, one 7, one 3 and one 0, can you write the big number without sorting anything?
Going through the digits from 9 down to 0 and writing each one as many times as it appears gives `8730`.
How would you find "how many 8s" using `% 10` and `// 10`?

## Hint 2

To count digit `d` in `x`: copy `x` to `m`, then 4 times: if `m % 10 == d`, add 1 to the count; then `m //= 10`.
Doing it exactly 4 times (not `while m > 0`) also counts the leading zeros of a number like `999` (which is `0999`).

To build numbers digit by digit: `big = big * 10 + d` adds `d` on the right. For `small`, digits come in decreasing
order too, so add each one on the **left** instead: `small = small + d * place`, with `place` going 1, 10, 100, 1000.

## Hint 3

```
read x
if x % 1111 == 0: print invalid  (1111, 2222, ..., 9999 are exactly the same-digit numbers)
else:
    steps = 0
    repeat:
        big = 0, small = 0, place = 1
        for d from 9 down to 0:
            count how many of the 4 digits of x equal d
            repeat count times: big = big*10 + d; small = small + d*place; place *= 10
        diff = big - small, steps += 1, print the line with :04d
        x = diff
        stop if diff == 6174
    print steps
```

Check the stop rule before the loop body or after? The input `6174` must still print one step.

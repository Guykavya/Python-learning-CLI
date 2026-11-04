## Hint 1

Do not start with the dispatcher. Write `P` (prefix sums) and the six command functions first, each taking integers and
returning a string, and test them on the example log `3 1 4 1 5 9 2 6`. Which three commands are just differences of
two prefix values?

## Hint 2

The patterns, one per command:

```
sum l r        -> P[r] - P[l - 1]
best k         -> max of P[i + k] - P[i] over i = 0..n-k
above k t      -> count of P[i + k] - P[i] >= t * k        (integers only, no averages)
maxsub b       -> Kadane on a[i] - b, best starts at the first value (the answer may be negative)
longest_le S   -> variable window: add a[right]; while total > S and left <= right: remove a[left]
maxwin k       -> monotonic deque of indices (pop smaller-or-equal from the back, drop the front when <= i - k)
```

## Hint 3

The dispatcher, with all checks before any conversion:

```
ARITY = {"sum": 2, "best": 1, "maxsub": 1, "longest_le": 1, "above": 2, "maxwin": 1}
parts = line.split()
if no parts or parts[0] not in ARITY: error
if len(parts) - 1 != ARITY[name]: error
if any argument is not  optional "-" + digits: error
convert to int, call the function (it does its own 1 <= k <= n / 1 <= l <= r <= n checks)
```

Collect the output lines in a list and print them with one `"\n".join(...)` at the end: 200000 separate `print` calls
are slower.

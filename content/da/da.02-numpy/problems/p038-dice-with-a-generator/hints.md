## Hint 1

How do you draw `n` dice rolls from a Generator (Ch. 13.1)? Is the upper bound of `rng.integers` included or excluded?

## Hint 2

Counting how often each small non-negative integer appears is what `np.bincount` does. For rolls 1..6 it returns 7 counts (it counts 0s too). How do you make sure there are always 7 even if no 6 was rolled, and how do you drop the count of 0s?

## Hint 3

```text
rolls = rng.integers(1, 7, size=n)
counts = bincount(rolls, minlength=7)    # positions 0..6
return counts[1:]                        # faces 1..6
```

## Approach

The mean of the observed values is the only number needed. `fillna(m)` returns a new Series and leaves `s` unchanged.
The spread shrinks because the filled values sit exactly at the centre: they add to the number of values but nothing
to the sum of squared distances from the mean.

## Code

```python
def fill_with_mean(s):
    filled = s.fillna(s.mean())
    return filled, float(s.std()), float(filled.std())
```

## Complexity

O(n).

## Another way

Fill with random draws from the observed values (`rng.choice`) to keep the spread; the price is randomness and the need
for a seed. In the chapter's MCAR example, filling 23 percent with the mean cut the standard deviation from 18,729 to
16,486 and the share above 50,000 from 16.3 to 12.7 percent.

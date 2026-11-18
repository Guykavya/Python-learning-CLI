## Approach

Chapter section 7. Every kilogram of a denser item is worth more than every kilogram of a thinner one, so fill the bag with the densest item first, then the next, and take only a fraction of the item that no longer fits whole.

```python
def fractional_knapsack(items, capacity):
    total = 0.0
    room = capacity
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        if room <= 0:
            break
        part = min(weight, room)              # the whole pile, or whatever still fits
        total += value * part / weight
        room -= part
    return total
```

Why it is safe (exchange argument): if a best bag holds some kilograms of a thinner item `b` while part of the densest item `a` is left outside, swap `d` kilograms of `b` for `d` kilograms of `a`. The weight stays the same and the value changes by `d * (density(a) - density(b)) >= 0`. The swap is legal **because** fractions are allowed (p013 shows what happens without them).

## Complexity

`O(n log n)` for the sort, `O(n)` for the sweep.

## Another way

Avoid floating-point keys by comparing densities with cross-multiplication, or use `fractions.Fraction(value, weight)` as the key and `Fraction` for the total, converting with `float(...)` at the end. For huge `n` with a small capacity there is an `O(n)` method based on selecting the median density (quickselect, dsa.05), but sorting is what interviews and the chapter expect.

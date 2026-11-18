## Hint 1

Because fractions are allowed, think one **kilogram** at a time. Which item's kilogram is worth the most? That item should be used first, as much as possible. The number to sort by is the **density** `value / weight`.

## Hint 2

Sort by density, highest first. Keep `room`, the space left. For each item take `part = min(weight, room)` kilograms, worth `value * part / weight`, and subtract `part` from `room`. Once `room` is 0, nothing more fits. Start the total at `0.0` so the result is a float.

## Hint 3

```
total = 0.0; room = capacity
for (value, weight) in items sorted by value/weight, descending:
    if room <= 0: break
    part = min(weight, room)
    total += value * part / weight
    room -= part
return total
```

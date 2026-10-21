## Hint 1

Where should `smallest` and `largest` start? Why is starting them at 0 wrong for `[-2, -8]`?

## Hint 2

Handle the empty list first, with an early return. Then start both at `numbers[0]`.

## Hint 3

```
if list is empty: return None, None
smallest = largest = numbers[0]
for n in numbers:
    if n < smallest: smallest = n
    if n > largest: largest = n
return smallest, largest
```

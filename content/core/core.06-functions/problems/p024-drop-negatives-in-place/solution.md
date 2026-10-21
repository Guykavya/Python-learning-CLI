## Approach

Two steps: compute the survivors as a new list, then copy them into the caller's list with slice
assignment `numbers[:] = ...`, which mutates the existing object. Building the new list first
avoids the remove-while-looping bug.

## Code

```python
def drop_negatives(numbers):
    """Remove every negative number from numbers, in place. Return None."""
    numbers[:] = [n for n in numbers if n >= 0]
```

## Complexity

O(n) time, O(n) extra space for the temporary list.

## Another way

A two-pointer loop that copies each non-negative item forward to position `write`, then
`del numbers[write:]`. It uses O(1) extra space:
```python
write = 0
for n in numbers:
    if n >= 0:
        numbers[write] = n
        write += 1
del numbers[write:]
```

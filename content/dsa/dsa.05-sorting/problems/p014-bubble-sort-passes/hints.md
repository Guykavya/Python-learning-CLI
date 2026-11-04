## Hint 1

How does the loop know it is finished? What would a pass with no swaps tell you about the list?

## Hint 2

Use a flag `swapped = False` before each pass, set it to `True` on a swap, and stop when the flag is still `False` after the pass. Count the pass before checking the flag.

## Hint 3

```
passes = swaps = 0
while True:
    passes += 1; swapped = False
    for i in range(n - 1):
        if a[i] > a[i+1]: swap; swaps += 1; swapped = True
    if not swapped: break
```

## Approach

The leftmost digits weigh the most. Among numbers of the same length, the smaller one is the one with the smaller digit at the first position where they differ. So whenever a digit is followed by a smaller one, removing it makes the number smaller, and earlier removals beat later ones. An increasing stack applies this rule in one pass. If removals are left, the remaining digits never decrease, so the largest ones are at the end: remove from the end. Finally strip leading zeros.

## Code

```python
def remove_k_digits(num, k):
    stack = []
    for d in num:
        while k and stack and stack[-1] > d:
            stack.pop()
            k -= 1
        stack.append(d)
    if k:
        stack = stack[:-k]              # still removals left: drop the largest, at the end
    return "".join(stack).lstrip("0") or "0"
```

## Complexity

`O(n)` time: each digit is pushed once and popped at most once. `O(n)` memory.

## Another way

Repeat `k` times: scan for the first `i` with `num[i] > num[i + 1]` (or the last digit if there is none) and delete it. It makes the same choices one at a time, but each round costs `O(n)`, so the total is `O(n * k)`. The stack avoids rescanning from the start after each removal.

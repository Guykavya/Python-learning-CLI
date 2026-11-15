## Approach

The function `digit_square_sum` turns every number into the next one, so the numbers form a chain, exactly like nodes and `next`. Every chain of this kind ends in a cycle (see below). Floyd's fast and slow pointers find that cycle in `O(1)` memory. The number is happy when the cycle is `1 -> 1`, so check whether `fast` reached `1`.

## Why it works

The sequence cannot grow forever. A number with `d` digits has a digit-square sum of at most `81 d`. For `d >= 4`, `81 d` is far smaller than the number itself (a 4-digit number is at least 1000, but its sum is at most 324), so large numbers shrink quickly, and after a few steps every value stays below 1000. A sequence that stays inside a finite set of values must repeat a value, and from the first repeat on it goes round the same cycle forever. So the chain of numbers is a linked list **with a cycle**: either the cycle `1 -> 1` (happy) or another cycle (for this map it is always `4 -> 16 -> 37 -> 58 -> 89 -> 145 -> 42 -> 20 -> 4`). Floyd's method finds a cycle in any such chain; when `fast` is `1`, it stays `1`, so stopping there is safe.

## Code

```python
def digit_square_sum(n):
    total = 0
    while n > 0:
        n, d = divmod(n, 10)
        total += d * d
    return total


def is_happy(n):
    slow = n
    fast = digit_square_sum(n)
    while fast != 1 and slow != fast:
        slow = digit_square_sum(slow)                     # one step
        fast = digit_square_sum(digit_square_sum(fast))   # two steps
    return fast == 1
```

## Complexity

The number of steps before the sequence enters its cycle is small (the values drop below 1000 within a few steps, and the cycles are short), so the run time is tiny: `O(log n)` for the first step and a bounded number of steps after that. `O(1)` extra memory.

## Another way

Keep a `set` of seen numbers and stop on a repeat: simple, and fine here because the sequence is short. The two-pointer version shows that Floyd's method works on **any** "next" function, which is the key idea of problem 22.

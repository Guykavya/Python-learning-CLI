## Approach

Scan left to right with a stack of kept digits (chapter section 12). When the next digit is **smaller** than the top, the top sits in a more important place than a smaller digit could, so deleting it makes the number smaller no matter what comes later: pop it, as long as removals remain. Equal digits are **not** popped: deleting one of two equal neighbours changes nothing now, and the removal is better spent later. If removals are left at the end, the stack is non-decreasing, so the biggest digits are at the right end: cut them there.

```python
def remove_k_digits(num, k):
    stack = []
    for d in num:
        while k and stack and stack[-1] > d:
            stack.pop()
            k -= 1
        stack.append(d)
    if k:
        stack = stack[:-k]               # remaining removals come off the right end
    return "".join(stack).lstrip("0") or "0"
```

Digits are compared as characters: `"0" < "1" < ... < "9"`, the same order as their values.

## Complexity

Each digit is pushed once and popped at most once: `O(n)` time, `O(n)` space.

## Another way

Repeat `k` times: delete the first digit that is bigger than the next one (or the last digit if there is none). It is the same greedy one step at a time, easier to see, but `O(n k)`: too slow for `n = k / 2 = 50,000`.

```python
def remove_k_digits(num, k):
    digits = list(num)
    for _ in range(k):
        i = 0
        while i + 1 < len(digits) and digits[i] <= digits[i + 1]:
            i += 1
        del digits[i]
    return "".join(digits).lstrip("0") or "0"
```

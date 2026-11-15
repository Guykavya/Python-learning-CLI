## Hint 1

Compare `"1432219"` with each digit removed once. Removing the `4` (it is larger than the `3` after it) gives the smallest result. Why is the first "peak" the right digit to remove?

## Hint 2

```
for d in num:
    while k and stack and stack[-1] > d: stack.pop(); k -= 1
    stack.append(d)
drop the last k digits if k is still > 0
result = "".join(stack).lstrip("0") or "0"
```

## Hint 1

Compare `"14..."` and `"13..."` after deleting one digit from `"143..."`: deleting the 4 puts the smaller 3 into the more important place. In general: find the first place where a digit is bigger than the one after it, and delete it. Doing that `k` times is correct but `O(n k)`. How can a stack do all the deletions in one pass?

## Hint 2

Keep the digits you plan to keep on a stack. Before pushing a new digit `d`, pop the top while removals are left and the top is **strictly bigger** than `d`. At the end the stack is non-decreasing; if removals are still left, cut them from the **right** end (the biggest digits sit there). Finally strip leading zeros, and use `"0"` for an empty result.

## Hint 3

```
stack = []
for d in num:
    while k > 0 and stack and stack[-1] > d:
        stack.pop(); k -= 1
    stack.append(d)
if k > 0: stack = stack[:-k]
result = "".join(stack).lstrip("0")
return result or "0"
```

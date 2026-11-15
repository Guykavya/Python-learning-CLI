## Hint 1

After you push `"a"`, `"b"`, `"c"` onto `stack = []`, the list is `["a", "b", "c"]`. Which character does `stack.pop()` return first?

## Hint 2

Collect the popped characters in a second list and join it at the end. Keep popping while the stack is not empty.

## Hint 3

```
stack = []
for ch in s: stack.append(ch)
out = []
while stack: out.append(stack.pop())
return "".join(out)
```

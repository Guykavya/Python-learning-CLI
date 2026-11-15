## Hint 1

After processing a prefix of `s`, the stack holds the reduced form of that prefix. A new character can only cancel with **one** character: which one?

## Hint 2

```
for ch in s:
    if stack and stack[-1] == ch: stack.pop(); pairs += 1
    else: stack.append(ch)
return ("".join(stack), pairs)
```

## Hint 1

Start from the chapter's `calculate2` (terms on a stack; apply the operator that came **before** the number; `*` and `/` change the top term). It already handles unary minus at the start: `op` begins as `"+"` and `number` as 0, so `-5` becomes `0 - 5`. What is missing is only the brackets.

## Hint 2

Make the scan a function `parse(i)` that evaluates from position `i` until it reaches a `)` or the end, and returns `(value, position of that ")")`. When it meets `(`, it calls itself: `number, i = parse(i + 1)`. The bracket's value is then used exactly like a number that was just read.

## Hint 3

```
s = s.replace(" ", "")
def parse(i):
    stack, number, op = [], 0, "+"
    while True:
        ch = s[i] if i < len(s) else ")"      # the end acts like a ")"
        if digit: number = number * 10 + int(ch)
        elif ch == "(": number, i = parse(i + 1)
        else:
            apply op to number (push, push negative, multiply top, trunc-divide top)
            if ch == ")": return sum(stack), i
            op, number = ch, 0
        i += 1
```

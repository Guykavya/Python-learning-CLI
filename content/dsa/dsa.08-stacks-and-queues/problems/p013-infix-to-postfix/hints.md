## Hint 1

Give each operator a number: `PREC = {"+": 1, "-": 1, "*": 2, "/": 2}`. A `(` on the stack must stop the popping loop. How can you make the loop stop at it without a special case? (Is `"("` in `PREC`?)

## Hint 2

```
for t in tokens:
    if t.isdigit(): out.append(t)
    elif t in PREC:
        while ops and ops[-1] in PREC and PREC[ops[-1]] >= PREC[t]:
            out.append(ops.pop())
        ops.append(t)
    elif t == "(": ops.append(t)
    else:
        while ops[-1] != "(": out.append(ops.pop())
        ops.pop()
while ops: out.append(ops.pop())
```

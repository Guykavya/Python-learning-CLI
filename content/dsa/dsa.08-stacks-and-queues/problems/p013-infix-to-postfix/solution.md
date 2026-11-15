## Approach

Numbers go straight to the output, because in postfix the operands keep their left-to-right order. Operators wait on a stack until we know nothing with stronger binding still needs to act before them. A new operator first releases every waiting operator that binds at least as strongly (equal precedence leaves first: left associativity). Brackets create a "floor" on the stack: nothing below a `(` may leave until its `)` arrives.

## Code

```python
PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def to_postfix(tokens):
    out, ops = [], []
    for t in tokens:
        if t.isdigit():
            out.append(t)
        elif t in PREC:
            while ops and ops[-1] in PREC and PREC[ops[-1]] >= PREC[t]:
                out.append(ops.pop())
            ops.append(t)
        elif t == "(":
            ops.append(t)
        else:                                  # ")"
            while ops[-1] != "(":
                out.append(ops.pop())
            ops.pop()                          # discard the "("
    while ops:
        out.append(ops.pop())
    return out
```

## Complexity

`O(n)` time: every token is appended to the output or pushed and popped once. `O(n)` memory.

## Another way

Recursive descent (dsa.07): one function per precedence level. `expr` reads `term (+|- term)*`, `term` reads `factor (*|/ factor)*`, and `factor` is a number or `( expr )`. Each function appends its operator to the output **after** both operands, which produces postfix. The shunting-yard stack does the same job without recursion, so it has no depth limit.

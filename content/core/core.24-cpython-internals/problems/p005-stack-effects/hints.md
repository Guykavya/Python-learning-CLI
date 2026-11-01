## Hint 1

Before each instruction runs, how many values must already be on the stack? If you write that
number down for each op in a small dict, how can one `if` check every underflow? Use
`enumerate` to know the offset. For `max_depth`, when can the stack size change?

## Hint 2

```
NEEDS = {"PUSH": 0, "POP": 1, "DUP": 1, "SWAP": 2, "ADD": 2, "MUL": 2}

stack = [], deepest = 0
for offset, (op, arg) in enumerate(ops):
    if op not in NEEDS: raise ValueError(... op ...)
    if len(stack) < NEEDS[op]: raise StackUnderflow(f"{op} at offset {offset} ...")
    PUSH: append arg | POP: pop | DUP: append stack[-1]
    SWAP: swap stack[-1] and stack[-2]
    ADD/MUL: b = pop(); a = pop(); append(a op b)
    deepest = max(deepest, len(stack))
```

Write one helper that returns both the stack and `deepest`, and let the two public functions
call it.

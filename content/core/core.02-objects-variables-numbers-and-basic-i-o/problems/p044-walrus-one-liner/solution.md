## Approach

The walrus operator is an **assignment expression**: it binds a name and also produces the value.
Arguments are evaluated left to right, so each later argument can use names bound earlier.

## Code

```python
print((n := int(input())), (sq := n * n), sq % 7, sq > 100, sep=" | ")
```

## Why the brackets

Inside a function call, `n := ...` as a bare argument is not allowed in some places and confusing
in all of them, so wrap each walrus in brackets. At statement level, `n := 5` alone is a
`SyntaxError`; you must write `n = 5` or `(n := 5)`.

## When to use it in real code

This one-liner is a puzzle. In real programs, plain assignment is clearer here. The walrus is
useful when you need a value both for a test and afterwards, for example in a `while` loop
condition (core.04): `while (line := input()) != "quit":`.

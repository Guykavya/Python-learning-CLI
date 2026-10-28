## Approach

Left operand first, except when the right operand's class is a subclass that overrides the reflected method. `NotImplemented` always means "let the other side try"; only after both decline does the `TypeError` appear.

## Output

```text
A.add
A+
B.radd
B r+
A.add
A+
A.add
A+
D.add
C.radd
C r+
A.radd
A r+
D.add
error: unsupported operand type(s) for +: 'D' and 'int'
```

## Complexity

Not applicable.

## Another way

Remove the `__radd__` from `B` and run again: the subclass rule only applies to classes that **override** the reflected method, so `A() + B()` would then use `A.__add__`.

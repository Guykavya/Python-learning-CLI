## Hint 1

For each object ask the three questions in order: does the class define `__bool__`? If not, does it define `__len__`? Only if neither, the object is true. Which classes above fall into which case?

## Hint 2

Careful with `print(Bag(4) and "second")`: `and` returns the first falsy operand, or the last operand if all are truthy. `or` returns the first truthy one, or the last. Neither returns a plain `True` or `False` unless the operands were those. `any` and `all` also use the truthiness rules for each item.

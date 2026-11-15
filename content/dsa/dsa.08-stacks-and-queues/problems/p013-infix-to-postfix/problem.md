# Infix to postfix (shunting-yard)

Write `to_postfix(tokens)`. `tokens` is a list of strings for a normal (**infix**) expression: non-negative integers, the operators `+ - * /` and the brackets `(` `)`. Return the **postfix** form as a list of strings: the same numbers and operators, no brackets.

Rules (chapter section 6, "From infix to postfix: the shunting-yard method"):

- `*` and `/` bind tighter than `+` and `-`;
- operators of equal precedence work **left to right**: `8 - 3 - 2` is `(8 - 3) - 2`, so its postfix is `8 3 - 2 -`;
- brackets override everything.

Use an output list and an **operator stack**:

- number: append it to the output;
- operator: while the top of the stack is an operator with **higher or equal** precedence, move it to the output; then push the new operator;
- `(`: push it; `)`: move operators to the output until the `(`, then throw the `(` away;
- at the end, move everything left on the stack to the output.

## Example

```python
>>> to_postfix(["3", "+", "4", "*", "2"])
['3', '4', '2', '*', '+']
>>> to_postfix(["(", "3", "+", "4", ")", "*", "2"])
['3', '4', '+', '2', '*']
>>> to_postfix(["8", "-", "3", "-", "2"])
['8', '3', '-', '2', '-']
>>> to_postfix(["3", "+", "4", "*", "2", "/", "(", "1", "-", "5", ")"])
['3', '4', '2', '*', '1', '5', '-', '/', '+']
```

## How it is tested

Besides fixed examples, the tests build 1,500 random valid expressions (numbers 0 to 20, nested brackets), evaluate your postfix with **exact fractions** (so `/` is true division, `7 / 2 = 7/2`), and compare with Python's own `eval` of the infix text using the same exact fractions. Expressions that divide by zero are skipped. A wrong precedence or a wrong associativity changes the value, so the test finds it.

## Constraints

- The expression is valid; `1 <= len(tokens) <= 10**4`.

## Think about

Why `>=` and not `>` in the "while the top has higher or equal precedence" rule? Which example above breaks with `>`?

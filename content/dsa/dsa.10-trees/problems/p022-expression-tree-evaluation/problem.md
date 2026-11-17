# Expression tree evaluation

An arithmetic expression is a tree (chapter section 4): a **leaf** holds a number, and every other node holds one of the strings `"+"`, `"-"`, `"*"`, `"/"` and has **two** children, its left and right operands. Write `evaluate(root)` that returns the value of the expression. `"/"` is true division (`7 / 2` is `3.5`). The left operand is the first one: `"-"` with children `10` and `4` is `10 - 4 = 6`.

Numbers can be negative, and a leaf is a node **without children**. The tree is never empty and never divides by zero.

## Example

```python
>>> evaluate(build(["*", "+", 2, 3, 4]))          # (3 + 4) * 2
14
>>> evaluate(build(["-", 10, 4]))
6
>>> evaluate(build(["/", 7, 2]))
3.5
>>> evaluate(build([-5]))
-5
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few hundred nodes. `O(n)` time.

## Think about

Which traversal order is this? Why must both operands be known before the operator can be applied?

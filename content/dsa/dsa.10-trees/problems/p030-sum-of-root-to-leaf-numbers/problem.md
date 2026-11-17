# Sum of root-to-leaf numbers

Every node holds one digit, `0` to `9`. A path from the root down to a leaf spells a number: the path `1 -> 2 -> 3` is `123`. Write `sum_numbers(root)` that returns the sum of the numbers of **all** root-to-leaf paths. A leaf is a node with no children. An empty tree gives `0`.

## Example

```python
>>> sum_numbers(build([1, 2, 3]))           # 12 + 13
25
>>> sum_numbers(build([4, 9, 0, 5, 1]))     # 495 + 491 + 40
1026
>>> sum_numbers(build([7]))
7
>>> sum_numbers(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few hundred nodes, depth below the recursion limit. `O(n)` time. The numbers fit in Python integers.

## Think about

How do you extend a number by one digit? (`123` with the next digit `4` gives `1234`: multiply by 10, add the digit.) The number so far travels **down** as a parameter; the sums travel **up** as return values.

# Course schedule II

As in p033: there are `num_courses` courses `0 .. num_courses-1`, and a pair `[a, b]` in `prerequisites` means "take `b` **before** `a`".

Write `find_order(num_courses, prerequisites)`. Return a list with all courses in an order in which they can be taken, or `[]` if that is impossible. If several orders work, return any of them: the tests check your order.

Now the direction of the edges matters. `[a, b]` is an edge `b -> a`. Turn it the wrong way and you get an order that is exactly backwards.

## Example

```python
>>> find_order(2, [[1, 0]])
[0, 1]
>>> find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])
[0, 1, 2, 3]                     # [0, 2, 1, 3] is also correct
>>> find_order(2, [[1, 0], [0, 1]])
[]
>>> find_order(3, [])
[0, 1, 2]                        # any order
```

## Constraints

- `1 <= num_courses <= 10**5`, `0 <= len(prerequisites) <= 10**5`. No recursion.

## Think about

Your order is a topological order of which graph: the one with edges `b -> a` or the one with edges `a -> b`? What would the order of the other graph mean for a student?

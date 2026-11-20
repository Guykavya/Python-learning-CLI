## Hint 1

Write down the inorder list of the first example: the tree `[1, 3, None, None, 2]` has the inorder `[3, 2, 1]`, and the sorted order would be `[1, 2, 3]`. The second example, `[3, 1, 4, None, None, 2]`, has the inorder `[1, 3, 2, 4]`. A pair of neighbours `a, b` in this list where `a > b` is a **descent**. How many descents does each list have? Try one more by hand: take `[1, 2, 3, 4, 5, 6]` and swap `2` and `5`, then swap `3` and `4`: count the descents for each.

## Hint 2

If the two swapped values are **neighbours** in the sorted order, the damaged list has exactly **one** descent, and the two wrong values are the two sides of that descent. If they are **far apart**, there are exactly **two** descents. The first wrong value is the **larger** value of the **first** descent; the second wrong value is the **smaller** value of the **last** descent. In `[1, 5, 3, 4, 2, 6]` (2 and 5 swapped) the descents are `(5, 3)` and `(4, 2)`: first = `5`, second = `2`. With one descent `(3, 2)`: first = `3`, second = `2`.

## Hint 3

```
walk the tree inorder (iterative with a stack, or recursive), keeping `prev` = the previous node
first = second = None
for each node `cur` in inorder:
    if prev is not None and prev.val > cur.val:     # a descent
        if first is None: first = prev              # larger side of the FIRST descent
        second = cur                                # smaller side of the latest descent
    prev = cur
swap first.val and second.val
```

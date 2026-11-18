# Candy distribution

Children stand in a line; `ratings[i]` is the rating of child `i`. You give out candies so that:

1. every child gets **at least one** candy;
2. a child with a **higher** rating than a **neighbour** (the child just left or just right of them) gets **more** candies than that neighbour.

Write `min_candies(ratings)` that returns the **smallest total** number of candies.

Equal ratings put **no** rule on the two children: `[2, 2]` needs only `1 + 1 = 2` candies.

This problem is **not** worked in the chapter. The hints teach the method: two greedy passes, one from each side.

## Example

```python
>>> min_candies([1, 0, 2])         # 2, 1, 2
5
>>> min_candies([1, 2, 2])         # 1, 2, 1
4
>>> min_candies([1, 3, 4, 5, 2])   # 1, 2, 3, 4, 1
11
>>> min_candies([5, 4, 3, 2, 1])   # 5, 4, 3, 2, 1
15
```

## Constraints

- `1 <= len(ratings) <= 2 * 10**4`, `0 <= ratings[i] <= 2 * 10**4`.

## Think about

Each child has two rules, one for each neighbour. What if you satisfy only the "left neighbour" rules first, in one pass, and then only the "right neighbour" rules, in a second pass? How do you combine them so the second pass does not break the first?

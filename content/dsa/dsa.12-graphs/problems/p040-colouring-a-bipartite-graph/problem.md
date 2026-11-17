# Colouring a bipartite graph

`n` people (numbered `0 .. n-1`) must be split into **two groups**. `dislikes` is a list of pairs `(a, b)`: `a` and `b` refuse to be in the same group. (This is LeetCode's "possible bipartition" story.)

Write `two_colour(n, dislikes)`. Return a list `group` of length `n` with `group[i]` equal to `0` or `1`, such that for every pair `(a, b)` in `dislikes`, `group[a] != group[b]`. If that is impossible, return `None`.

Model it first: people are vertices, every dislike is an undirected edge, and a valid split is exactly a two-colouring of the graph (chapter section 8). The answer is not unique (swapping the two groups of a piece gives another answer), so the tests **check** your list instead of comparing it.

Rules:

- People without any dislike can go to either group, but they must get `0` or `1`, not something else.
- A pair `(a, a)` (someone who dislikes themself) makes it impossible.
- The same pair can be listed twice, in either order.

## Example

```python
>>> two_colour(4, [(0, 1), (0, 2), (1, 3)])
[0, 1, 1, 0]                 # [1, 0, 0, 1] is just as good
>>> two_colour(3, [(0, 1), (1, 2), (2, 0)])
None                         # three people who all dislike each other
>>> two_colour(3, [])
[0, 0, 0]                    # any list of 0s and 1s
```

## Constraints

- `1 <= n <= 10**5`, `0 <= len(dislikes) <= 2 * 10**5`. No recursion.

## Think about

If the answer is `None`, there is a reason you could show to the people: a group of them that dislike each other in a circle. What is special about the length of that circle?

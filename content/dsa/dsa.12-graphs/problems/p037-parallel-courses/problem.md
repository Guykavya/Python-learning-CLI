# Parallel courses (longest chain)

There are `n` courses `0 .. n-1`. A relation `(u, v)` means "`u` must be **finished** before `v` can start". In one semester you can take **any number** of courses, as long as all their prerequisites were finished in **earlier** semesters.

Write `min_semesters(n, relations)`. Return the smallest number of semesters needed to take all courses, or `-1` if it is impossible (the relations contain a cycle).

The answer is the number of **rounds** of Kahn's algorithm (chapter section 7, "The smallest order, and rounds"): in round 1 take every course with in-degree 0; removing them frees the courses for round 2; and so on. It is also the number of courses on the **longest chain** `u1 -> u2 -> ... -> uk`.

## Example

```python
>>> min_semesters(3, [(0, 2), (1, 2)])           # 0 and 1 together, then 2
2
>>> min_semesters(3, [(0, 1), (1, 2), (0, 2)])   # the chain 0 -> 1 -> 2 decides
3
>>> min_semesters(3, [(0, 1), (1, 2), (2, 0)])
-1
>>> min_semesters(4, [])
1
```

## Constraints

- `1 <= n <= 10**5`, `0 <= len(relations) <= 2 * 10**5`. The same relation can be listed twice. `O(n + E)` time, no recursion.

## Think about

In the second example, course 2 can be "reached" from course 0 in one step. Why does it still need semester 3? Why does a BFS distance from the starting courses give the wrong answer here?

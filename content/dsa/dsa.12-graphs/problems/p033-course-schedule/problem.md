# Course schedule

There are `num_courses` courses, numbered `0 .. num_courses-1`. `prerequisites` is a list of pairs `[a, b]`: to take course `a` you must **first** take course `b`.

Write `can_finish(num_courses, prerequisites)`. Return `True` if there is some order in which you can take all courses, `False` otherwise.

This is a word problem; turn it into a graph first (chapter section 18 shows the habit):

- what are the vertices, and what is an edge? **Careful with the direction**: `[a, b]` says `b` comes first, so the edge goes `b -> a`;
- "can I take them all?" is "does the graph have a topological order?", which is "does it have **no** directed cycle?".

Kahn's algorithm (chapter section 7) answers it directly: if all courses get taken, the answer is `True`.

## Example

```python
>>> can_finish(2, [[1, 0]])                  # take 0, then 1
True
>>> can_finish(2, [[1, 0], [0, 1]])          # each waits for the other
False
>>> can_finish(4, [[1, 0], [2, 0], [3, 1], [3, 2]])
True
>>> can_finish(1, [[0, 0]])                  # a course that needs itself
False
```

## Constraints

- `1 <= num_courses <= 10**5`, `0 <= len(prerequisites) <= 10**5`. A chain of 100,000 courses is in the tests: no recursion.

## Think about

Does the direction of the edges matter for **this** question (can all be finished)? Does it matter for the next problem, which asks for the order?

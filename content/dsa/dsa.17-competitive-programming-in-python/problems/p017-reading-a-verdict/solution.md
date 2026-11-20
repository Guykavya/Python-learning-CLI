## Approach

| Report | Reasoning | Cause |
|---|---|---|
| 1 | The value `3` is the same as `3.00`; only the text differs. Print with `f"{x:.2f}"`. | F |
| 2 | Test 2 is the smallest input: a special case your code mishandles. | B |
| 3 | `2 * 10**5` squared is `4 * 10**10` steps; no way to pass in CPython. | C |
| 4 | `RecursionError` on a path graph: iterative DFS (section 8). | D |
| 5 | `5000 * 5000 = 2.5 * 10**7` list entries, hundreds of megabytes. | E |
| 6 | Each unordered pair counted twice: the formula or idea is wrong. | A |

Answer:

```text
1: F
2: B
3: C
4: D
5: E
6: A
```

## What to do first

1: look at the statement's output format. 2: write the smallest input by hand and trace it. 3: find the quadratic loop and the structure that replaces it (sort, hash map, prefix sums). 4: write the DFS with an explicit stack. 5: replace the table by two rows, or by a dictionary of the cells you use. 6: trace the sample by hand.

Reports 2 and 6 are found by a stress test with a brute force; 1 and 3 to 5 are not (they do not give a different answer on small inputs).

## Complexity

Not applicable: this is a reading skill. In a contest you do it in under a minute.

## Another way

Keep a checklist file with these six causes, and run through it in order on every non-accepted submission.

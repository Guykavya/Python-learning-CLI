## Approach

One tuple key handles all three rules: `(dept, -salary, name)`. Departments ascend, negative
salaries ascend (so real salaries descend), and names break any remaining ties.

## Code

```python
rows = []
for _ in range(int(input())):
    name, dept, salary = input().split()
    rows.append((dept, -int(salary), name))
rows.sort()
for dept, neg, name in rows:
    print(dept, name, -neg)
```

## Complexity

O(n log n).

## Another way: sort three times

Stability lets you sort by the **least** important key first: by name, then by salary with
`reverse=True`, then by department. Each later sort keeps the earlier order for ties. You need
`key=` functions for that, which become easy with `lambda` in core.06.

## Walkthrough

1. `id=\d+` has no groups: whole matches `['id=7', 'id=42']` (`x=10` does not start with `id`).
2. `id=(\d+)` has one group: only the digits `['7', '42']`.
3. `(\w+)=(\d+)` has two groups: a tuple per match, `[('id', '7'), ('x', '10'), ('id', '42')]`.
4. No `z=` anywhere: `[]`.
5. `pairs[1]` is `('x', '10')`, so `pairs[1][0]` is `x`, and there are 3 pairs.
6. `(a)|(b)` on `"ab"`: the first match is `a` (group 2 did not take part, so `''`), the second is `b` (group 1 empty): `[('a', ''), ('', 'b')]`.
7. `\d*` on `"a12"`: at index 0 it matches zero digits (empty match), then `12` from index 1, then one more empty match at the end: `['', '12', '']`.
8. `(\d)+` matches `123` and `45`, but the group is repeated and keeps its last repetition: `['3', '5']`.
9. `((\d)\d)` has two groups: the outer one is the two digits, the inner one the first digit: `[('12', '1'), ('34', '3')]`.

## The exact output

```text
['id=7', 'id=42']
['7', '42']
[('id', '7'), ('x', '10'), ('id', '42')]
[]
x 3
[('a', ''), ('', 'b')]
['', '12', '']
['3', '5']
[('12', '1'), ('34', '3')]
```

**Lesson:** add brackets to a `findall` pattern and its result changes shape. If you need the
whole match **and** groups, use `re.finditer` and read `m.group(0)`, `m.group(1)`, ...

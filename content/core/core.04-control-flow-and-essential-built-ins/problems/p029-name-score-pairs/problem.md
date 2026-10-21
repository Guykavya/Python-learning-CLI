# Names and scores with zip

Read a line of names and a line of whole-number scores, both separated by spaces.

- If the counts differ, print `Mismatch: N names, S scores` and nothing else.
- Otherwise print `name: score` for each pair, in order, and finally
  `Average: <average with 1 decimal>`. If both lines are empty, print `No data`.

**Example**

Input:
```
Asha Ravi Meena
82 91 77
```
Output:
```
Asha: 82
Ravi: 91
Meena: 77
Average: 83.3
```

Use `zip` to walk the two lines together.

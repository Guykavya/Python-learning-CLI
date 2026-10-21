# Keys, values and items

Read `n` (at least 1), then `n` lines of `name score` (score is an integer). A repeated name
replaces the earlier score. Print:

```
Names: <names in insertion order>
Scores: <scores in the same order>
Total: <sum of scores>
Best: <name with the highest score> (<score>)
```

If several names share the highest score, use the one that comes **first** in the dict.

**Example**

Input:
```
3
Asha 82
Ravi 91
Meena 77
```
Output:
```
Names: Asha Ravi Meena
Scores: 82 91 77
Total: 250
Best: Ravi (91)
```

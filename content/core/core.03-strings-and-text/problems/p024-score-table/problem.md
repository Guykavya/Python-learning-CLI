# A small score table

Read three lines, each holding a student name and a score separated by a comma, like `Asha, 87`. There may be spaces around the name and the score. Print an aligned table:

```
Name         Score
------------------
Asha            87
Ravi            92
Meena            9
------------------
Average       62.7
```

Rules:

- Names are left-aligned in width 12. Scores and the average are right-aligned in width 6.
- The header uses the same widths.
- The separator is 18 dashes.
- The average has exactly 1 decimal.

**Example input**

```
Asha, 87
  Ravi ,92
Meena,9
```

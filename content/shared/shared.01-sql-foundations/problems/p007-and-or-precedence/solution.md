## Approach

Evaluate each row against the grouped condition.

| row | category | price | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|
| Quiet Rivers | fiction | 12.50 | yes | yes | no | no |
| Iron Garden | fiction | 9.99 | yes | yes | no | no |
| Data Basics | tech | 39.00 | yes | yes | no | yes |
| SQL in Practice | tech | 45.50 | no | no | no | yes |
| Cooking Light | cooking | 18.00 | no | no | no | yes |
| Night Train | mystery | 9.99 | no | no | yes | yes |

## Code

```
Quiet Rivers
Iron Garden
Data Basics
---
Quiet Rivers
Iron Garden
Data Basics
---
Night Train
---
Data Basics
SQL in Practice
Cooking Light
Night Train
```

(with `---` separators exactly as in `expected.txt`.)

## Complexity

Each row is tested once per query. Precedence is decided when the query is parsed, not per row.

## Another way / portable SQL

Always write parentheses when you mix `AND` and `OR`; the rules are the same in all major databases, but readers forget them. De Morgan's law: `NOT (a AND b)` equals `(NOT a) OR (NOT b)`.

## Hint 1

For query 1, put the invisible parentheses in first. Which two conditions are grouped by `AND`?
Then list which rows satisfy the left side of the `OR` and which satisfy the right side.

## Hint 2

```
Q1: category='fiction'  OR  (category='tech' AND price<40)
Q2: (fiction OR tech)   AND  price<40
Q3: (NOT fiction)       AND  price<15
Q4: NOT (fiction AND price<15)
```

Check each row of the table against each version in turn. Q3 and Q4 are not the same.

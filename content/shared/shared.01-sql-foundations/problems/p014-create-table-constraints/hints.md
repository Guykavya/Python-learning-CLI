## Hint 1

For each column, list the rules in the table above. Which rules go after the type in the column definition? Which rule needs a condition in parentheses? A `CHECK` on a NULL value: does it reject the row? (Think about three-valued logic.)

## Hint 2

```
CREATE TABLE members (
  member_id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name  TEXT NOT NULL,
  age   INTEGER CHECK (age >= 13),
  plan  TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro'))
);
```

Finish the SQL and end each statement with `;`.

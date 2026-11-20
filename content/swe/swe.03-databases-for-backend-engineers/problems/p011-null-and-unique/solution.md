## Approach

| Insert | Why |
|---|---|
| 1 | first `'a@x.com'` |
| 2 | `NULL`: no value to compare |
| 3 | a second `NULL`: `NULL = NULL` is unknown, not true, so `UNIQUE` sees no duplicate (SQLite and PostgreSQL both allow many `NULL`s) |
| 4 | the exact text again: duplicate, refused |
| 5 | `'A@x.com'` differs by case; text comparison is case-sensitive by default |
| 6 | `''` is a value, the first one |
| 7 | `''` again: duplicate, refused |

(Checked by running the inserts.)

## Complexity

Not applicable.

## Another way

To forbid duplicates regardless of case use `email TEXT COLLATE NOCASE UNIQUE`, or an index on `lower(email)`. To forbid several missing values, make the column `NOT NULL`.

## Why it matters

"Optional but unique" columns (a phone number, an external id) rely on this rule. An application that stores `''` instead of `NULL` for "missing" breaks it on the second row.

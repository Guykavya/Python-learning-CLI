# CREATE TABLE with constraints

A good table rejects bad data **by itself**. Constraints are rules the database checks on every `INSERT`/`UPDATE`:
`PRIMARY KEY` (unique row id), `NOT NULL`, `UNIQUE`, `CHECK (condition)` and `DEFAULT value`.

Write a `SCRIPT` (SQL text with one or more statements, run by `executescript`) that creates the table `members`:

| column | type | rules |
|---|---|---|
| `member_id` | INTEGER | primary key |
| `email` | TEXT | required, no two members may share an email |
| `name` | TEXT | required |
| `age` | INTEGER | optional (may be NULL), but if present it must be at least 13 |
| `plan` | TEXT | required, default `'free'`, must be `'free'` or `'pro'` |

The tests insert good and bad rows and check which ones the database accepts. Do not insert any rows yourself.

**Example.** `CREATE TABLE pets (pet_id INTEGER PRIMARY KEY, name TEXT NOT NULL, legs INTEGER CHECK (legs >= 0));`

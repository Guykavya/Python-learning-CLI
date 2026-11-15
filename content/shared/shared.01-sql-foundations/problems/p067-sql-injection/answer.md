# Model answer

**1. What went wrong.** The f-string pastes the user's text into the SQL string *before* the database sees it. The name `ada' --` contains a closing quote and the SQL comment marker `--`.
The final text is `... WHERE name = 'ada' --' AND password = 'anything'`. The quote ends the string literal early, and `--` turns the rest of the line (the whole password check) into a comment.
So the database ran `WHERE name = 'ada'` and logged the attacker in as ada without the password. The third call is the same idea: `' OR '1'='1` adds an always-true condition, so every row matches.
The input was meant to be *data* but became *code*.

**2. Why `?` is safe.** With placeholders, the SQL text is fixed: `... WHERE name = ? AND password = ?`. The database parses it first and builds a plan; the values arrive afterwards through a separate channel and are bound
into the slots as plain values. The text `ada' --` is compared as a whole string with the `name` column; no user text is ever parsed as SQL. No row has that name, so the result is `[]`.

**3. The `column` helper.** It does not work as intended. A placeholder stands for a *value*, and the structure of the statement (which table, which column, which keyword) is fixed when it is parsed.
`SELECT ? FROM books` returns the text `'title'` for every row, and `ORDER BY ?` sorts by a constant, so nothing is ordered. Table and column names cannot be parameters.
Use an allow-list: `if column not in {"title", "price", "published"}: raise ValueError`, then put the checked name into the SQL text yourself, and keep `n` as a parameter (`LIMIT ?`).

**4. Other defences.** Least privilege (the application's database user can only do what it needs; no `DROP`, no access to unrelated tables), validation of input types (convert `n` to `int`), using an ORM or query builder that always parameterises, and keeping error messages from the database away from users.

| call | SQL text sent | rows |
|---|---|---|
| f-string, `ada' --` | `... name = 'ada' --' AND ...` | 1 (attack works) |
| `?`, `ada' --` | `... name = ? AND password = ?` + values | 0 |

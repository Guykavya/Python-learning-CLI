# NULL and UNIQUE

Chapter section 4.3. A table has a `UNIQUE` column:

```sql
CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE);
```

These seven inserts run in order. A refused insert changes nothing, and the next one still runs.

```text
1. INSERT INTO users VALUES (1, 'a@x.com');
2. INSERT INTO users VALUES (2, NULL);
3. INSERT INTO users VALUES (3, NULL);
4. INSERT INTO users VALUES (4, 'a@x.com');
5. INSERT INTO users VALUES (5, 'A@x.com');
6. INSERT INTO users VALUES (6, '');
7. INSERT INTO users VALUES (7, '');
```

For each insert write `ok` if it succeeds or `error` if the database refuses it:

```text
1: ok
```

Do not run it.

## After you answer

1. Why can two `NULL`s coexist? What does `NULL = NULL` evaluate to?
2. Is `'a@x.com'` the same as `'A@x.com'` for `UNIQUE`? How would you make e-mail comparison case-insensitive?
3. Is the empty string `''` the same as `NULL` for `UNIQUE`?

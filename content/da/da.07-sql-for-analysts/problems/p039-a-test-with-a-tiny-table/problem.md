# A test with a tiny table

Chapter section 10.3. The strongest test of a query is a table **so small that you can compute the answer by hand**. Wrap the
retention query in a function that takes its tables and a cutoff, then call it on a fixture with a known answer.

This problem has two parts, and the second part is the lesson.

**Part 1.** Write

```python
def retention_on(con, users, events, cutoff):
    ...
```

`users` and `events` are DataFrames (as in the chapter), `cutoff` is a date string such as `'2025-04-01'`. Register the tables on
`con` and return a **list of tuples** `(cohort_month, k, active_users, cohort_size)`, sorted by `cohort_month` then `k`, where:

- the cohort of a user is the month of `signup_at`; a user is active in a month if they have a `login` in it;
- only logins **before `cutoff`** count;
- `k = date_diff('month', cohort_month, active_month)`; `active_users` counts **distinct** users; `cohort_size` counts **all** users of the cohort.

(`cohort_month` may come back as a date or as text `'YYYY-MM-DD'`; both are accepted.)

**Part 2.** Write

```python
def tiny_case():
    ...
```

returning `(users_df, events_df, expected_rows)`: a table of **at most 5 users and 12 events** whose answer for cutoff
`'2025-07-01'` you counted by hand, and `expected_rows` in the same format as above. The test will check that your hand count is
right, and then run **three deliberately broken versions** of the query on your table. A good tiny table makes **all three fail**:

1. a query that counts **login rows** instead of distinct users;
2. a query that uses "the n-th active month" as `k` instead of the months since sign-up;
3. a query that takes the **cohort size** from the users who were active, so users who never logged in vanish from the size.

Think which users you need: one who logs in twice in a month, one who skips a month, one who never logs in.

```python
# users_df columns: user_id, signup_at, channel, country      events_df columns: event_id, user_id, event_time, event_type
```

## Example

For `users = [(1, 2025-01-05), (2, 2025-01-20)]` and logins of user 1 on 5 Jan and 3 Feb, user 2 on 20 Jan, with cutoff `2025-04-01`,
`retention_on` returns `[('2025-01-01', 0, 2, 2), ('2025-01-01', 1, 1, 2)]`.

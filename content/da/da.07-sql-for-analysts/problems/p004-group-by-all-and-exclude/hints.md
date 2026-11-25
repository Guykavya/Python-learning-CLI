## Hint 1

Start from a CTE that is just `events` without its id column. Which keyword removes a column from `*`? Then think about the final `SELECT`: it lists three plain columns and one aggregate. What can you write after `GROUP BY` so that you do not repeat the three names?

## Hint 2

```text
WITH e AS (SELECT * EXCLUDE (event_id) FROM events)
SELECT u.channel, u.country, e.event_type, count(*) AS events
FROM e JOIN users u USING (user_id)
GROUP BY ALL
```

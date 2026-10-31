## Hint 1

Write the four London door entries `00:30 BST`, `01:30 BST`, `01:30 GMT` and `01:15 GMT` for the
night of 27 October 2024 as the teammate would store them. Which two rows look identical? In what
order would `ORDER BY` put them? Now convert each to UTC: what changes?

## Hint 2

For question 2, recall the chapter: a naive datetime passed to `.astimezone()` is read as the
computer's local time. Where does your code run: on your laptop or on a server? For question 3,
name the exact functions: `datetime.now(timezone.utc)`, `replace(tzinfo=ZoneInfo(...))`,
`astimezone(...)`, `isoformat()`.

## Hint 3

For question 4: the UTC value is computed with the DST rules known *today*. What if the rules
change before the appointment? What must you keep so that you can compute the right UTC instant
again later?

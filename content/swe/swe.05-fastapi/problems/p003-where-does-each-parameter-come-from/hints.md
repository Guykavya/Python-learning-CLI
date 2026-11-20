## Hint 1

For each parameter ask the section 3.1 question: is its name in the path? If yes it comes from the path; otherwise a simple type comes from the query string. Then ask: can this text be converted to the declared type? `int` accepts `"-3"` but not `"abc"` or `"2.5"`. `bool` accepts `true/false`, `1/0`, `yes/no`, `on/off`.

## Hint 2

Errors are **collected**, not stopped at the first one: a request with two bad values gives two entries, path parameters first. Before validation comes **routing**: if the URL does not match the pattern `/users/{user_id}/posts` at all, no parameter is read. And a plain `str` query parameter sent twice keeps only one of the values (the last).

## Hint 3

```text
1  -3 is a valid int (no constraint)          -> 200, defaults for the rest
2  limit "3" -> 3, draft "yes" -> True         -> 200
3  draft "0" -> False, tag "py"                -> 200
4  limit "abc"                                 -> 422 query.limit
5  user_id "abc" AND draft "maybe"             -> 422 path.user_id query.draft
6  empty segment: the route does not match     -> 404
7  tag twice, plain str                        -> 200 with the last value
8  limit "2.5": not a whole number             -> 422 query.limit
```

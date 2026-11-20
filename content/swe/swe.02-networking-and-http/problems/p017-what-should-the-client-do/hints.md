## Hint 1

Start with the table as code: a chain of `if` checks on `status`. Which header names need a case-insensitive lookup?

## Hint 2

`Retry-After` has two forms. Digits only: a number of seconds. Otherwise try to read it as a date; if `parsedate_to_datetime` raises `ValueError` or `TypeError`, the value is garbage.

## Hint 3

```text
headers = {name.lower(): value ...}
2xx or 304 -> use
redirect + location -> follow:...
429/503: seconds = parse retry-after; wait:<seconds> if usable else retry
408/500/502/504 -> retry;  401 -> log-in;  400/404/... -> fix-request;  else give-up
date: seconds = max(0, ceil((when - now).total_seconds()))
```

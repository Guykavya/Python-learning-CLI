## Approach

Specific literal cases first, then guarded ranges, then the wildcard. `match` checks top to
bottom, so 404 is caught before the general 4xx case.

## Code

```python
code = int(input())
match code:
    case 200:
        text = "OK"
    case 201:
        text = "Created"
    case 204:
        text = "No Content"
    case 301 | 302 | 307 | 308:
        text = "Redirect"
    case 401 | 403:
        text = "Not Allowed"
    case 404:
        text = "Not Found"
    case n if 400 <= n <= 499:
        text = "Client Error"
    case n if 500 <= n <= 599:
        text = "Server Error"
    case _:
        text = "Unknown"
print(f"{code} {text}")
```

## Why order matters

If the 4xx guard came before `case 404:`, 404 would print `Client Error`. Same rule as an
`elif` chain: specific first.

## Another way

An `if`/`elif` chain with `in (301, 302, 307, 308)` works too. `match` reads more like the
table in the problem.

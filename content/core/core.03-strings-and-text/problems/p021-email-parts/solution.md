## Code

```python
user, at, domain = input().strip().partition("@")
domain = domain.lower()
print(f"User: {user}")
print(f"Domain: {domain}")
print(f"Masked: {user[0]}***@{domain}")
```

## Why `partition`

It cuts once and always gives three parts, so unpacking is safe. `split("@")` also works here because there is exactly one `@`, but `partition` states the intent ("cut at this point") more clearly.

## Another way

`at_pos = email.index("@")`, then `email[:at_pos]` and `email[at_pos + 1:]`. Using `index` instead of `find` means a missing `@` raises an error instead of slicing at -1.

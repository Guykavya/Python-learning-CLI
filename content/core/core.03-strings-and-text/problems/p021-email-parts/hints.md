## Hint 1

You need to cut the address once, at the `@`. Which method gives you the parts before and after a separator?

## Hint 2

`user, at, domain = email.strip().partition("@")`. Then `domain.lower()`, and `user[0]` for the first character.

## Hint 3

```
user, at, domain = input().strip().partition("@")
domain = domain.lower()
print("User:", user)
print("Domain:", domain)
print(f"Masked: {user[0]}***@{domain}")
```

## Hint 1

What are the four checks, and which of them need the text **stripped** first? Which one must not be stripped?

## Hint 2

Compile two regular expressions at the top of the file and use `.fullmatch(...)` so the whole string must match. For the email, "no spaces and no extra @" is `[^@\s]+@[^@\s]+\.[^@\s]+`. Use `form.get("key", "")`.

## Hint 3

```text
clean = {"username": str(get("username")).strip(), "email": str(get("email")).strip()}
errors = {}
if not USERNAME.fullmatch(clean["username"]): errors["username"] = message
if not EMAIL.fullmatch(clean["email"]):       errors["email"] = message
if len(password) < 10:                        errors["password"] = message
if confirm != password:                       errors["confirm"] = message
return clean, errors
```

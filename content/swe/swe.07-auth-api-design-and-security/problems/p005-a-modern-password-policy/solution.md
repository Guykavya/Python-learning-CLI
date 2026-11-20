## Approach

```python
def check_password_policy(password: str, username: str = "", breached=frozenset()) -> list[str]:
    problems = []
    if len(password) < 12:
        problems.append("too_short")
    if len(password) > 256:
        problems.append("too_long")
    if password.lower() in breached:
        problems.append("breached")
    if username and username.lower() in password.lower():
        problems.append("contains_username")
    if password and len(set(password)) == 1:
        problems.append("one_character")
    return problems
```

Each rule is independent, so the function is five plain `if`s and the user sees **all** problems at once instead of fixing them one by one.

What the policy leaves out is the lesson (chapter 2.4): no demand for capitals, digits or symbols, no forced password change every 90 days. Those rules push people towards `Password1!`. Length and a breached-password list stop far more real attacks. The maximum length is not for the user's sake: it protects your server, because hashing is slow on purpose and a huge "password" would be a denial-of-service request.

In a real system the `breached` set comes from a list of leaked passwords (or the Have I Been Pwned range API, which needs only the first five characters of a hash).

## Complexity

`O(length of the password)` for the length, lower-casing and `set` steps; the breached lookup is `O(1)` on average for a `set`.

## Another way

Use a library such as `zxcvbn`, which scores how guessable a password is (dictionary words, keyboard patterns, dates) instead of fixed rules. It is better at catching `qwertyuiop12`-style choices, but harder to explain to a user and to test, so many teams use "length + breached list" first.

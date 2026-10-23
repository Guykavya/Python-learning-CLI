# find_user and greeting

A small user directory is a dict from user id to name: `{"u1": "Asha", "u2": "Ravi"}`.
Write three annotated functions in `solution.py`.

1. `find_user(users: dict[str, str], user_id: str) -> str | None` returns the name, or `None`
   if the id is not in the directory.
2. `greeting(users: dict[str, str], user_id: str) -> str` returns `"Hello, <name>!"`, or
   `"Hello, guest!"` when the user does not exist.
3. `shout_name(users: dict[str, str], user_id: str) -> str | None` returns the name in capital
   letters, or `None` when the user does not exist.

Use `find_user` inside the other two. **An empty name is still a name**: if `users` has
`"u3": ""`, then `find_user` returns `""` (not `None`) and `greeting` gives `"Hello, !"`.
That is why you must check `is None` and not `if not name`.

**Examples**

```python
users = {"u1": "Asha", "u3": ""}
find_user(users, "u1")      # "Asha"
find_user(users, "u9")      # None
greeting(users, "u1")       # "Hello, Asha!"
greeting(users, "u9")       # "Hello, guest!"
greeting(users, "u3")       # "Hello, !"
shout_name(users, "u1")     # "ASHA"
shout_name(users, "u9")     # None
```

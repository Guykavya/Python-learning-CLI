## Approach

`dict.get` returns `None` for a missing key, so `find_user` is a one-liner whose natural type is `str | None`.

In the other two functions the result of `find_user` must be checked before use. mypy would flag `name.upper()` on a `str | None` with `Item "None" of "str | None" has no attribute "upper"`. The early-return guard `if name is None: return ...` narrows `name` to `str` for the rest of the function. The check must be `is None`, not `if not name`, because an empty string is a real name here.

## Code

```python
def find_user(users: dict[str, str], user_id: str) -> str | None:
    return users.get(user_id)


def greeting(users: dict[str, str], user_id: str) -> str:
    name = find_user(users, user_id)
    if name is None:
        return "Hello, guest!"
    return "Hello, " + name + "!"


def shout_name(users: dict[str, str], user_id: str) -> str | None:
    name = find_user(users, user_id)
    if name is None:
        return None
    return name.upper()
```

## Complexity

O(1) dict lookup, plus O(len(name)) for building or upper-casing the string.

## Another way

`greeting` can be written as `return "Hello, " + users.get(user_id, "guest") + "!"`: giving `dict.get` a default means the `None` never appears. Use that when a default value exists. The guard version is the general pattern for when the "missing" case needs different handling.

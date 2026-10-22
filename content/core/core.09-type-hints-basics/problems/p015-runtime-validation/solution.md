## Approach

The hints are promises made by the caller; nothing enforces them. So the functions check at runtime. In `set_age` the type check comes first, because comparing a `str` with a number (`"21" < 0`) would raise a confusing `TypeError` of its own. `bool` must be rejected explicitly, since `isinstance(True, int)` is `True`.

`require_str_list` checks the container, then each item. A runtime check cannot "look inside" `list[str]` for free: it has to loop over the items. After the checks, mypy knows (from the `isinstance` narrowing) that `values` is a `list`, but the item types are only proven by the loop, which is why the declared return type is trusted here.

## Code

```python
def set_age(age: int) -> int:
    if isinstance(age, bool) or not isinstance(age, int):
        raise TypeError("age must be an int")
    if age < 0 or age > 150:
        raise ValueError("age must be between 0 and 150")
    return age


def require_str_list(values: object) -> list[str]:
    if not isinstance(values, list):
        raise TypeError("expected a list")
    result: list[str] = []
    for item in values:
        if not isinstance(item, str):
            raise TypeError("every item must be a str")
        result.append(item)
    return result
```

## Complexity

`set_age` is O(1). `require_str_list` is O(n). (This version returns an equal, new list; the tests compare with `==`.)

## Another way

`all(isinstance(item, str) for item in values)` replaces the loop. Libraries such as pydantic, which you may meet later, perform exactly this kind of checking automatically from the hints.

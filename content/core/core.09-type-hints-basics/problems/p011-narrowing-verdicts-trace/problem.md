# Does mypy accept this None handling?

`get_name` returns `str | None`. Eight functions use its result in different ways. mypy checks
the line marked with a letter in each one.

```python
def get_name(users: dict[str, str], key: str) -> str | None:
    return users.get(key)


def f1(users: dict[str, str]) -> int:
    name = get_name(users, "a")
    return len(name)                        # A


def f2(users: dict[str, str]) -> int:
    name = get_name(users, "a")
    if name is None:
        return 0
    return len(name)                        # B


def f3(users: dict[str, str]) -> int:
    name = get_name(users, "a")
    if name:
        return len(name)                    # C
    return 0


def f4(users: dict[str, str]) -> str:
    name = get_name(users, "a")
    return name.upper() if name else "?"    # D


def f5(users: dict[str, str]) -> str:
    name = get_name(users, "a")
    return name or "?"                      # E


def f6(users: dict[str, str]) -> str:
    return get_name(users, "a")             # F


def f7(users: dict[str, str]) -> str:
    name = get_name(users, "a")
    if name is not None:
        print("found")
    return name                             # G


def f8(users: dict[str, str]) -> str:
    name = get_name(users, "a")
    assert name is not None
    return name                             # H
```

For each letter, decide whether mypy reports an error on that line (`error`) or accepts it (`ok`).
Write one line per letter, in order, in the form `A: ok` or `B: error`.

Write your answer in `answer.txt`.

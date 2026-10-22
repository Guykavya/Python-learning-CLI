# Which narrowing patterns does mypy accept?

Twelve small functions, each with one line marked with a letter. For each letter decide whether
mypy reports an error on that line (`error`) or accepts it (`ok`).

```python
def clean_a(values: list[str | None]) -> list[str]:
    result: list[str] = []
    for v in values:
        result.append(v)                          # A
    return result


def clean_b(values: list[str | None]) -> list[str]:
    result: list[str] = []
    for v in values:
        if v is None:
            continue
        result.append(v)                          # B
    return result


def clean_c(values: list[str | None]) -> list[str]:
    return [v for v in values if v is not None]   # C


def clean_d(values: list[str | None]) -> list[str]:
    return [v for v in values]                    # D


def lookup_e(table: dict[str, str], key: str) -> str:
    if key in table:
        return table.get(key)                     # E
    return ""


def lookup_f(table: dict[str, str], key: str) -> str:
    if key in table:
        return table[key]                         # F
    return ""


def pick(a: str | None, b: str | None) -> str:
    if a is None and b is None:
        return ""
    if a is not None:
        return a                                  # G
    return b                                      # H


def shorten(text: str | None) -> str:
    if text is None:
        text = "default"
    return text.upper()                           # I


def total(values: list[int | None]) -> int:
    t = 0
    for v in values:
        t += v                                    # J
    return t


def parse(text: str) -> int | str:
    if text.isdigit():
        return int(text)
    return text


def use_k(text: str) -> int:
    r = parse(text)
    if isinstance(r, str):
        return 0
    return r + 1                                  # K


def use_l(text: str) -> int:
    return parse(text) + 1                        # L
```

Write one line per letter, in order, in the form `A: ok` or `B: error`.

Write your answer in `answer.txt`.

Tip: mypy narrows a type using the checks it can **see** (`is None`, `isinstance`, `in` is *not*
one of them for `dict.get`). It does not combine facts from two separate `if` statements.

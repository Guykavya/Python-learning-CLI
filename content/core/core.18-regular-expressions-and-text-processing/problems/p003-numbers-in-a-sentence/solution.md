## Approach

A number is "maybe a minus, then one or more digits": `-?[0-9]+`.

- `-?` : the `?` makes the minus optional (zero or one).
- `[0-9]+` : one or more digits. The `+` is greedy, so it takes the whole run.

`re.findall` returns the matched **strings**; convert each with `int()`. `int("-2")` and
`int("007")` both work.

## Code

```python
import re


def numbers(s: str) -> list[int]:
    return [int(text) for text in re.findall(r"-?[0-9]+", s)]
```

## Complexity

O(n) for a string of length n.

## Another way

`\d` instead of `[0-9]` gives the same result for normal text. `\d` also matches digits from
other scripts (such as `४`), and `int()` can convert those, so it would not crash, but `[0-9]`
states exactly what the task asks for.

Without regex you would walk the string character by character, collecting digits into a buffer
and checking the character before each run for a `-`. That is about fifteen lines instead of one.

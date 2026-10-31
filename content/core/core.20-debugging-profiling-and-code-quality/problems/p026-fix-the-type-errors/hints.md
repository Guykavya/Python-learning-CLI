## Hint 1

Read each error as "the value is X but you promised Y". On line 9 the dictionary holds
`raw.strip()`: what type is that? On line 15, the docstring says `best` may return `None`: so
which promise is wrong, the code or the annotation?

## Hint 2

Convert the score where it is stored, change the return annotation of `best` to `str | None`, and
check for `None` before using the value (mypy then knows `top` is a `str` below the check).

```
scores[name.strip()] = int(raw)          # int() ignores surrounding spaces
def best(scores: dict[str, int]) -> str | None:
...
top = best(scores)
if top is None:
    return "no scores"
return f"best: {top.upper()}, ..."
```

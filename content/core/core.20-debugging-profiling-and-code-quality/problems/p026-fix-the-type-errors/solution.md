## Approach

Treat each mypy line as a bug report and ask "which side is lying, the code or the annotation?"

1. **Line 9, `got dict[str, str]`.** mypy saw `scores[...] = raw.strip()`, a `str`, so it inferred
   `dict[str, str]`. The annotation (`int` scores) is what the program needs, so the **code** is
   wrong: store `int(raw)`. This was a real bug: `max` compared strings, and `"9" > "10"`.
2. **Line 15, `got None, expected str`.** The docstring and the code agree that `best` can
   return `None`, so the **annotation** is wrong: `-> str | None`.
3. Fixing 2 makes mypy look again at every caller. `report` called `top.upper()` on a value that
   can be `None`: the crash `report([])` had all along. Check `if top is None` first; after that
   check mypy **narrows** `top` to `str`.

## Code

```python
def parse_scores(lines: list[str]) -> dict[str, int]:
    scores: dict[str, int] = {}
    for line in lines:
        if ":" not in line:
            continue
        name, raw = line.split(":", 1)
        scores[name.strip()] = int(raw)
    return scores


def best(scores: dict[str, int]) -> str | None:
    if not scores:
        return None
    return max(scores, key=lambda name: scores[name])


def report(lines: list[str]) -> str:
    scores = parse_scores(lines)
    top = best(scores)
    if top is None:
        return "no scores"
    return f"best: {top.upper()}, average: {average(scores):.1f}"
```

`mypy --strict` on this version: `Success: no issues found in 1 source file` (real run, mypy 2.4.0).

## Complexity

Unchanged: O(n) for n lines. Type hints cost nothing at run time.

## Another way

Annotate the empty dictionary (`scores: dict[str, int] = {}`) **first**. Then mypy reports the
bad assignment on the line where it happens (line 8, `Incompatible types in assignment`), which
is closer to the cause than the `return` line. Annotating empty containers is a good habit for
exactly that reason.

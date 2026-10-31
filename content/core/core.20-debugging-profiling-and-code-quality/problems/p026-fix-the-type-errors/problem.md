# Fix the type errors

`starter.py` has type hints, and the program "mostly works". A teammate ran the type checker
before merging it:

```text
$ mypy --strict solution.py
solution.py:9: error: Incompatible return value type (got "dict[str, str]", expected "dict[str, int]")  [return-value]
solution.py:15: error: Incompatible return value type (got "None", expected "str")  [return-value]
Found 2 errors in 1 file (checked 1 source file)
```

(Real output of mypy 2.4.0. You do not need mypy installed for this problem; the tests check
behaviour and the annotations, not mypy itself.)

Each error is a **real bug**, not a style complaint:

```python
def parse_scores(lines: list[str]) -> dict[str, int]:
    """'name: score' lines -> {name: score}. Lines without a ':' are skipped."""
    scores = {}
    for line in lines:
        if ":" not in line:
            continue
        name, raw = line.split(":", 1)
        scores[name.strip()] = raw.strip()
    return scores


def best(scores: dict[str, int]) -> str:
    """Name with the highest score, or None when there are no scores."""
    if not scores:
        return None
    return max(scores, key=lambda name: scores[name])


def average(scores: dict[str, int]) -> float:
    """Mean score; 0.0 when there are no scores."""
    if not scores:
        return 0.0
    return sum(scores.values()) / len(scores)


def report(lines: list[str]) -> str:
    scores = parse_scores(lines)
    top = best(scores)
    return f"best: {top.upper()}, average: {average(scores):.1f}"
```

Copy `starter.py` to `solution.py` and fix it so that mypy would report no errors **and** the
functions behave as their docstrings promise:

- `parse_scores` returns `int` scores (`"ann: 7"` gives `{"ann": 7}`), still annotated
  `-> dict[str, int]`.
- `best` keeps its job but its return annotation must tell the truth: it can return `None`.
- When you fix `best`'s annotation, mypy finds the next problem. This is the real output after
  that one change:

  ```text
  solution.py:29: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
  ```

  Fix it: `report` returns the string `"no scores"` when there are no scores.
- `average` and the format of `report` stay as they are.

Do not silence the checker with `# type: ignore` or `Any`; fix the cause.

**Example**

```python
parse_scores(["ann: 7", "no colon here", "bo:10"])
# {'ann': 7, 'bo': 10}
best({"a": 9, "b": 10})
# 'b'          (the starter says 'a': it compares the strings "9" and "10")
report(["ann: 7", "bo: 10"])
# 'best: BO, average: 8.5'
report([])
# 'no scores'  (the starter crashes with AttributeError)
```

# Final: constants that must not change

`starter.py` is a small retry-settings module. The names in capitals are meant to be constants,
but nothing says so. Copy it to `solution.py` and mark them with `Final`, so a type checker
reports any later reassignment.

Add these annotations (keep the values):

| Name | Annotation |
|---|---|
| `MAX_RETRIES` | `Final` (let the checker infer `int`) or `Final[int]` |
| `API_URL` | `Final[str]` |
| `BASE_DELAY` | `Final[float]` |
| `MAX_DELAY` | `Final[float]` |
| `ALLOWED_METHODS` | `Final` or `Final[tuple[str, ...]]` |
| `Config.DEFAULT_PORT` (class attribute) | `Final[int]` |

Also annotate the function: `retry_delay(attempt: int) -> float`.

`retry_delay(attempt)` returns `min(BASE_DELAY * 2 ** attempt, MAX_DELAY)`, and raises
`ValueError` when `attempt` is negative.

The tests read the annotations at runtime (`__annotations__`, `get_type_hints`), run the function,
and also check with `ast` that your module never assigns to a `Final` name a second time.
They do not need mypy, but `python -m mypy solution.py` should be clean.

**Example**

```python
retry_delay(0)    # 0.5
retry_delay(3)    # 4.0
retry_delay(10)   # 8.0   (capped by MAX_DELAY)
```

**Remember**: `Final` is only a promise to the type checker. Python itself will still let you
rebind the name when the program runs.

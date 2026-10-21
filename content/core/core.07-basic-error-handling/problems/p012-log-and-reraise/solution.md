## Approach

Catch `KeyError`, do the one extra job (append to the log), and re-raise the same exception with a
bare `raise`. The caller sees exactly the error it would have seen without the `try`, with the
original traceback.

## Code

```python
def load_score(scores, name, log):
    """Return scores[name]. On KeyError, log 'missing score: <name>' and re-raise."""
    try:
        return scores[name]
    except KeyError:
        log.append(f"missing score: {name}")
        raise
```

## Complexity

O(1).

## Another way

`except KeyError as e: ...; raise e` also re-raises the same object, but adds the `raise e` line to
the traceback. A bare `raise` is the idiom. Creating a new `KeyError(name)` would lose the original
traceback.

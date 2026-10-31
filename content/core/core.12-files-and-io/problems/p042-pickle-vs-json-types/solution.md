## Approach

`pickle` files are binary, so use `"wb"` and `"rb"`. For `json_loses`, do the whole trip and compare. A tuple becomes
a list, an `int` key becomes a `str` key, so the result differs from the original. A set or bytes value makes
`json.dumps` raise `TypeError`, and we count that as "loses".

## Code

```python
import json
import pickle


def save_pickle(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def json_loses(obj):
    try:
        back = json.loads(json.dumps(obj))
    except TypeError:
        return True
    return back != obj
```

## Complexity

O(size of the object).

## Another way

Check for the types directly (`isinstance(x, (set, tuple, bytes))`, `int` keys) with a recursive function. It is
more work and easy to get wrong, so the round-trip test is the safer check.

## Approach

`.npz` is a zip of `.npy` files, one per named array, and each `.npy` keeps the exact dtype and shape (Ch. 18.1). `np.savez` takes the arrays as keyword arguments, so `**arrays` passes the names straight through. Given a file *name*, `savez` appends `.npz` if it is missing; given an open file object it writes exactly there, so the function opens the path itself.

Loading is lazy: `np.load` returns an `NpzFile` that reads each array on access and keeps the file open. Reading every array inside `with np.load(path) as data:` gives a plain dict of in-memory arrays and closes the file. With the default `allow_pickle=False`, accessing an object array raises `ValueError`, which is the safe behaviour: pickled data can execute code when it is loaded. Refusing object arrays already at saving time gives a clearer message, at the place where the mistake happens.

## Code

```python
import numpy as np


def save_dataset(path, **arrays):
    if not arrays:
        raise ValueError("give at least one array to save")
    converted = {}
    for name, value in arrays.items():
        a = np.asarray(value)
        if a.dtype == object:
            raise ValueError(f"array {name!r} has dtype object: it cannot be saved without pickle")
        converted[name] = a
    with open(path, "wb") as f:
        np.savez(f, **converted)


def load_dataset(path):
    with np.load(path) as data:
        return {name: data[name] for name in data.files}
```

## Complexity

O(total size) for both: the bytes are written and read once.

## Another way

`np.savez_compressed` has the same interface and makes smaller files for repetitive data at the cost of a little time (Ch. 18.1 showed 594 against 434 bytes for a small bundle). For a table with columns of different types and missing values, pandas with Parquet (da.03) is the usual choice; `.npz` is for arrays.

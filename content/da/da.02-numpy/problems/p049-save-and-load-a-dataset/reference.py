import numpy as np


def save_dataset(path, **arrays):
    """Write the named arrays to one .npz file exactly at path."""
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
    """Read every array of the .npz file at path into a dict; never allow pickle."""
    with np.load(path) as data:
        return {name: data[name] for name in data.files}

# Save and load a dataset

Chapter section 18.1 (`.npy` and `.npz`). Write two functions that store several named arrays in one `.npz` file and read them back.

## `save_dataset(path, **arrays)`

- `path` is a `str` or `pathlib.Path`. Write the file **exactly at `path`**, whatever its suffix. (Careful: `np.savez("data.bin", ...)` silently writes `data.bin.npz`. Opening the file yourself with `open(path, "wb")` and passing the file object to `np.savez` avoids that.)
- Each keyword becomes one array in the archive under that name: `save_dataset(p, prices=a, ids=b)`.
- Raise `ValueError` if no arrays are given, and if any array has dtype `object` (it could only be stored with pickle, see below): the message names that array.

## `load_dataset(path)`

- Return a plain `dict` from name to array, with every array fully read into memory, and **close the file** (use `with np.load(path) as data:`).
- Never pass `allow_pickle=True`: loading pickled objects can run arbitrary code. A file that contains an object array must make `load_dataset` raise `ValueError` (NumPy does this for you when `allow_pickle` stays `False`).

The round trip keeps names, shapes and dtypes exactly (`float32` stays `float32`, strings stay strings, 0-d arrays stay 0-d).

## Example

```python
import numpy as np
from pathlib import Path

p = Path("survey.data")
save_dataset(p, scores=np.array([1.5, 2.0], dtype=np.float32), names=np.array(["a", "b"]))
p.exists()            # True   (not survey.data.npz)
d = load_dataset(p)
sorted(d)             # ['names', 'scores']
d["scores"].dtype     # dtype('float32')
```

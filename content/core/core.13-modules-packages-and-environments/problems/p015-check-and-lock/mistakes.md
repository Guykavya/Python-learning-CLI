- Looking up `installed[name]` without normalising: `"flask"` is not a key of `{"Flask": ...}`.
- Comparing versions as strings, so `4.10.1` looks older than `4.9`.
- Locking a name as soon as one of its lines passes. With `numpy>=1.26` and `numpy<2`, both must pass.
- Writing `numpy==...` twice in the lock when the name appears on two lines.
- Locking every installed package. Here only required names are locked (a real `pip freeze` lock pins
  everything, which is a different, also valid, design).
- Printing problems instead of returning them. A function that returns data can be tested and reused.

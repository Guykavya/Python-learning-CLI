# A reproducibility manifest

Chapter section 18. A result is reproducible when you can say **exactly** which data, which seed, which settings and which Python produced it. Write `manifest(values, seed, params)` returning a dict:

| key | value |
|---|---|
| `"sha256"` | the SHA-256 hex digest of the **canonical JSON** of `values`: `json.dumps(values, sort_keys=True, separators=(",", ":"), allow_nan=False)` encoded as UTF-8 |
| `"seed"` | `seed` |
| `"params"` | a **copy** of `params` (a later change to the caller's dict must not change the manifest) |
| `"python"` | the Python version string, `platform.python_version()` |
| `"n"` | `len(values)` |

`values` can be a list of numbers or a list of dicts (records). The manifest must be JSON-serialisable (`json.dumps(manifest(...))` works). The same inputs give the same hash; **key order inside records does not change the hash** (that is what `sort_keys=True` is for); changing any value changes it. `NaN` or infinity in `values` raises `ValueError` (it is not valid JSON and a hash of it would not be portable).

## Example

```python
manifest([1, 2, 3], seed=42, params={"bins": 10})["sha256"]
# the SHA-256 of the text "[1,2,3]"
```

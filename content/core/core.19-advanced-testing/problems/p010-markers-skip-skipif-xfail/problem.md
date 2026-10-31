# Markers: skip, skipif, xfail

A red test run that always has the same three red tests teaches everyone to ignore red. Markers
let you say **why** a test does not count right now:

| Marker | Meaning |
|---|---|
| `@pytest.mark.skip(reason=...)` | never run this test (placeholder, broken environment) |
| `@pytest.mark.skipif(condition, reason=...)` | skip only when the condition is true (wrong OS, old Python) |
| `@pytest.mark.xfail(reason=..., strict=True)` | the test is **expected to fail** (a known bug). It is reported as `xfailed`; with `strict=True` an unexpected pass is a failure |
| `@pytest.mark.slow` (any name you invent) | a label; select or deselect with `pytest -m slow` / `-m "not slow"` |

`starter.py` has five tests, three of which currently fail. **Do not change what any test does.**
Add markers so that a normal run on the checker's Python 3 gives:

| Test | Outcome |
|---|---|
| `test_slugify_basic` | passed |
| `test_slugify_accents` (known bug) | xfailed, with `strict=True` |
| `test_needs_python_4` (only possible on Python 4) | skipped, because of a **condition** |
| `test_not_written_yet` | skipped (placeholder) |
| `test_sum_of_a_million` | passed, and marked `slow` so `pytest -m "not slow"` leaves it out |

Every skip, skipif and xfail needs a `reason=`.

**How this is checked.** Your `solution.py` is run with real pytest (twice: normally and with
`-m "not slow"`) and the checker reads the report and your decorators.

**Example**

```python
@pytest.mark.skipif(sys.platform == "win32", reason="uses POSIX permissions")
def test_chmod(): ...
```

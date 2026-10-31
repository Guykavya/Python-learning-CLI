## Approach

Choose by **why** the test cannot pass: a bug (`xfail`), the environment (`skipif`), a
placeholder (`skip`). Slow tests get a label (`slow`) that you can filter on.

## Code

```python
@pytest.mark.xfail(reason="accents are not removed yet", strict=True)
def test_slugify_accents(): ...

@pytest.mark.skipif(sys.version_info < (4, 0), reason="needs Python 4")
def test_needs_python_4(): ...

@pytest.mark.skip(reason="not written yet")
def test_not_written_yet(): ...

@pytest.mark.slow
def test_sum_of_a_million(): ...
```

## Cost

A skipped test costs nothing, an xfail test still runs (it just may fail), and a deselected
test (`-m "not slow"`) is not even collected into the run.

## Another way

Register `slow` in `pytest.ini` (`markers = slow: takes more than a second`) and run with
`--strict-markers`, so a typo like `@pytest.mark.slwo` is an error instead of silently doing
nothing. `pytest.skip("reason")` inside a test body skips at run time, and `pytest.importorskip("numpy")`
skips when a library is missing.

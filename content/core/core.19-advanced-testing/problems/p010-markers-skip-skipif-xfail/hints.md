## Hint 1

Sort the five tests into four groups: healthy, **known bug** (should pass someday), **not
possible here** (depends on the environment), **not written** (placeholder). Which marker fits
each?

## Hint 2

`skipif` takes the condition as its first argument: it should be true exactly when the test
cannot work. A custom marker needs no registration for the checker to select it. The strict flag
goes inside xfail.

```
@pytest.mark.xfail(reason="...", strict=True)
@pytest.mark.skipif(sys.version_info < (4, 0), reason="needs Python 4")
@pytest.mark.skip(reason="not written yet")
@pytest.mark.slow
```

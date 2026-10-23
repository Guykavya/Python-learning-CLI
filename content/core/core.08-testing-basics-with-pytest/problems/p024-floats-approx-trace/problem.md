# Comparing floats in tests

Floats are stored in binary, so many decimal numbers are not exact (chapter 2). That is a trap
in tests: `assert a + b == 0.3` can fail for a correct function. `pytest.approx(x)` makes an
object that is "equal" to any number close to `x`: by default within a **relative** tolerance of
`1e-6` (one millionth of the expected value) or an absolute tolerance of `1e-12` (whichever is
larger). You can set your own with `rel=` or `abs=`.

Predict **exactly** what this program prints:

```python
import pytest

print(0.1 + 0.2 == 0.3)
print(0.1 + 0.2)
print(abs((0.1 + 0.2) - 0.3) < 1e-9)
print(0.1 + 0.2 == pytest.approx(0.3))
print(pytest.approx(0.3) == 0.1 + 0.2)
print(1.0 == pytest.approx(1.0001))
print(1.0 == pytest.approx(1.0001, abs=0.001))
print(100 == pytest.approx(100.00001))
print(round(0.1 + 0.2, 2) == 0.3)
print(3 * 0.1 == 0.3)
print(10 / 4 == 2.5)
print(0 == pytest.approx(1e-12))
```

Write your answer in `answer.txt`, one line per printed line. Floats print as Python prints them.

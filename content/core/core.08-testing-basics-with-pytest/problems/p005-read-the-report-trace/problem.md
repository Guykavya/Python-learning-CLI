# Read the failure report

This is `test_discount.py`:

```python
def apply_discount(price, percent):
    return price - price * percent / 100


def test_discount_ten_percent():
    assert apply_discount(200, 10) == 180


def test_discount_zero():
    assert apply_discount(50, 0) == 50


def test_discount_full():
    assert apply_discount(80, 100) == 8
```

and this is what `python -m pytest -q` printed (the time is machine-specific):

```text
..F                                                                      [100%]
=================================== FAILURES ===================================
______________________________ test_discount_full ______________________________

    def test_discount_full():
>       assert apply_discount(80, 100) == 8
E       assert 0.0 == 8
E        +  where 0.0 = apply_discount(80, 100)

test_discount.py:14: AssertionError
=========================== short test summary info ============================
FAILED test_discount.py::test_discount_full - assert 0.0 == 8
1 failed, 2 passed in 0.01s
```

Answer these four questions in `answer.txt`, **exactly** in this form, one per line:

```text
failed test: <name of the failing test>
line: <line number of the failing assert in test_discount.py>
function returned: <the value apply_discount gave>
test expected: <the value written in the test>
```

Then add a fifth line, `wrong one: test` or `wrong one: function`, saying which of the two is
wrong (do the arithmetic yourself: what is 100 percent off 80?).

# What do these asserts do?

An `assert` that fails raises `AssertionError` with the message after the comma. Predict
**exactly** what this program prints. (When Python compiles `t3` it prints a `SyntaxWarning` on
standard error. It is not part of the answer. The warning is a hint about what is wrong with `t3`.)

```python
def run(label, test):
    try:
        test()
    except AssertionError as e:
        print(label, "FAILED:", e)
    else:
        print(label, "passed")


def t1():
    assert 2 + 2 == 4


def t2():
    assert "abc".upper() == "abc", "upper changes the case"


def t3():
    assert (1 == 2, "this never fails")


def t4():
    assert [], "an empty list is falsy"


def t5():
    assert len("abc") == 3, "length"
    assert 0.1 + 0.2 == 0.3, "float sum"


def t6():
    x = 5
    assert x > 3 and x < 5, f"x was {x}"


def t7():
    assert not "", "an empty string is falsy"


def t8():
    assert [1, 2] == [1, 2], "equal"
    assert [1, 2] is [1, 2], "same object"


def t9():
    assert abs(0.1 + 0.2 - 0.3) < 1e-9, "close enough"


for number, func in enumerate([t1, t2, t3, t4, t5, t6, t7, t8, t9], start=1):
    run(number, func)
```

Write your answer in `answer.txt`, one line per printed line.

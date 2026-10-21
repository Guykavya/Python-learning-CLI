from solution import apply_twice


def add_three(n):
    return n + 3


def test_add_three():
    assert apply_twice(add_three, 10) == 16, "add_three(add_three(10)) is 16. Apply func to the RESULT of the first call."


def test_builtins_and_methods():
    assert apply_twice(str.upper, "hi") == "HI"
    assert apply_twice(abs, -7) == 7


def test_called_twice():
    calls = []
    def record(x):
        calls.append(x)
        return x * 2
    assert apply_twice(record, 5) == 20
    assert calls == [5, 10], f"func should be called with 5, then with 10; it was called with {calls}."


def test_lambda():
    assert apply_twice(lambda s: s + "!", "hey") == "hey!!"

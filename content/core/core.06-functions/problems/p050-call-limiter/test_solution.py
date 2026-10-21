from solution import limit_calls


def greet(name, punct="!"):
    return "Hi " + name + punct


def test_example():
    g = limit_calls(greet, 2)
    assert g("Asha") == "Hi Asha!"
    assert g("Ravi", punct="?") == "Hi Ravi?", "Forward keyword arguments too: func(*args, **kwargs)."
    assert g("Meena") is None, "After max_calls calls, return None."
    assert g("Kiran") is None


def test_func_not_called_after_limit():
    calls = []
    def record(x):
        calls.append(x)
        return x
    r = limit_calls(record, 1)
    r(1)
    r(2)
    r(3)
    assert calls == [1], f"func must not run after the limit; it ran with {calls}."


def test_zero_limit():
    calls = []
    r = limit_calls(calls.append, 0)
    assert r(5) is None and calls == []


def test_independent_wrappers():
    a = limit_calls(greet, 1)
    b = limit_calls(greet, 1)
    a("x")
    assert b("y") == "Hi y!", "Each wrapper needs its own count."


def test_no_arguments():
    r = limit_calls(lambda: 42, 1)
    assert r() == 42 and r() is None

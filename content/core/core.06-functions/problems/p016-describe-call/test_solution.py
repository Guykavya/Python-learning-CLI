from solution import describe_call


def add(a, b):
    return a + b


def test_positional():
    assert describe_call(add, 2, 3) == "add(2, 3) -> 5", (
        "Forward with func(*args, **kwargs) and show positional args with repr.")


def test_keyword_and_repr():
    assert describe_call(add, "a", b="b") == "add('a', b='b') -> 'ab'", (
        "Show strings with repr (quotes), and keywords as name=repr(value).")


def test_builtins():
    assert describe_call(len, [1, 2]) == "len([1, 2]) -> 2"
    assert describe_call(sorted, [3, 1], reverse=True) == "sorted([3, 1], reverse=True) -> [3, 1]"


def test_no_arguments():
    def answer():
        return 42
    assert describe_call(answer) == "answer() -> 42", "No arguments: empty parentheses."


def test_keyword_order_kept():
    def f(**kw):
        return None
    assert describe_call(f, z=1, a=2) == "f(z=1, a=2) -> None", "Keep keywords in the order passed; do not sort."


def test_called_exactly_once():
    calls = []
    def record(x):
        calls.append(x)
        return len(calls)
    out = describe_call(record, "go")
    assert calls == ["go"], f"func must be called exactly once, but it was called {len(calls)} times."
    assert out == "record('go') -> 1"


def test_forwards_not_packed():
    def two(a, b=0):
        return (a, b)
    assert describe_call(two, 1, b=2) == "two(1, b=2) -> (1, 2)", (
        "The function received the wrong arguments. Use func(*args, **kwargs), with the stars.")

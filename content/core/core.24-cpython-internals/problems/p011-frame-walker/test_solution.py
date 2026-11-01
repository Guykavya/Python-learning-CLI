from solution import call_chain


def outer(**kw):
    return middle(**kw)


def middle(**kw):
    return inner(**kw)


def inner(**kw):
    return call_chain(**kw)


class Greeter:
    def hello(self, **kw):
        return call_chain(**kw)


def make_nested():
    def nested():
        return call_chain(stop="test_qualified_names", qualified=True)
    return nested


MODULE_SOURCE = """
def outer():
    return middle()

def middle():
    return inner()

def inner():
    return call_chain()

result = outer()
"""


def test_starts_with_the_caller():
    names = inner(stop="test_starts_with_the_caller")
    assert names == ["inner"], (
        "Start with the function that called call_chain (frame 1), not call_chain itself (frame 0)."
    )


def test_walks_outwards():
    names = outer(stop="test_walks_outwards")
    assert names == ["inner", "middle", "outer"], "Follow f_back from inner to middle to outer, innermost first."


def test_stop_frame_not_included():
    names = outer(stop="middle")
    assert names == ["inner"], "Stop BEFORE the frame named stop; do not include it."


def test_without_stop_goes_past_the_test():
    names = outer()
    assert names[:4] == ["inner", "middle", "outer", "test_without_stop_goes_past_the_test"], (
        "Without stop, keep walking: the test function is the next caller."
    )
    assert "<module>" not in names, "Never include a frame named '<module>'."


def test_stops_at_module_level():
    namespace = {"call_chain": call_chain}
    exec(compile(MODULE_SOURCE, "<demo>", "exec"), namespace)
    assert namespace["result"] == ["inner", "middle", "outer"], (
        "Code run at module level has a frame named '<module>'. Stop before it (the test function above it is not included)."
    )


def test_method_names():
    names = Greeter().hello(stop="test_method_names")
    assert names == ["hello"], "co_name of a method is just the method name."
    names = Greeter().hello(stop="test_method_names", qualified=True)
    assert names == ["Greeter.hello"], "With qualified=True use f_code.co_qualname, which includes the class."


def test_qualified_names():
    names = make_nested()()
    assert names == ["make_nested.<locals>.nested"], (
        "co_qualname of a nested function includes the enclosing function and '<locals>'."
    )
    names = outer(stop="test_qualified_names", qualified=True)
    assert names == ["inner", "middle", "outer"], "Module-level functions have co_qualname equal to co_name."


def test_returns_a_list():
    assert isinstance(inner(stop="test_returns_a_list"), list), "Return a list of strings."

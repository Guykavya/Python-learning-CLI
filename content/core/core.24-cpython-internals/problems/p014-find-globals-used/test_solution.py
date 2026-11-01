import math

from solution import globals_used, undefined_globals

RATE = 0.2
counter = 0


def price(item):
    return round(item.cost * (1 + RATE) + math.sqrt(4), 2)


def report(items):
    def line(i):
        return f"{i.name}: {price(i)}"
    return [lenn(items)] + [line(i) for i in items]  # noqa: F821 (lenn is a deliberate typo)


def deep():
    def middle():
        return lambda x: helper_one(x) + sum(helper_two(y) for y in x)  # noqa: F821
    return middle


def shadows_builtin():
    len = 3
    return len + 1


def uses_closure():
    base = 10
    def add(x):
        return x + base
    return add


def bump():
    global counter
    counter += 1
    return counter


def repeated(xs):
    return len(xs) + len(xs) + max(xs) + max(xs)


def no_globals(a, b):
    return a * b


def comprehension_user(xs):
    return [abs(x) for x in xs]


def test_attributes_are_not_globals():
    got = globals_used(price)
    assert got == ["RATE", "math", "round"], (
        f"Got {got}. Only LOAD_GLOBAL names count. 'cost' and 'sqrt' are attribute names: they are in "
        "co_names, but they are loaded with LOAD_ATTR, not LOAD_GLOBAL."
    )


def test_sorted_and_unique():
    got = globals_used(repeated)
    assert got == ["len", "max"], f"Got {got}. Return each name once, sorted (use a set, then sorted())."
    assert isinstance(got, list), "Return a list."


def test_no_globals():
    assert globals_used(no_globals) == [], "a * b uses only parameters (LOAD_FAST), so no globals."


def test_local_that_shadows_a_builtin():
    assert globals_used(shadows_builtin) == [], (
        "len is assigned inside the function, so it is a local (LOAD_FAST/STORE_FAST), not the builtin."
    )


def test_closure_variables_are_not_globals():
    assert globals_used(uses_closure) == [], (
        "base is a closure variable of add (LOAD_DEREF), not a global. Only LOAD_GLOBAL counts."
    )


def test_global_statement():
    assert globals_used(bump) == ["counter"], (
        "`global counter; counter += 1` reads counter with LOAD_GLOBAL (and writes it with STORE_GLOBAL)."
    )


def test_nested_function_is_included():
    got = globals_used(report)
    assert got == ["lenn", "price"], (
        f"Got {got}. 'price' is read only inside the inner function line(), whose code object is in "
        "report.__code__.co_consts. Look inside nested code objects too."
    )


def test_any_depth():
    got = globals_used(deep)
    assert got == ["helper_one", "helper_two", "sum"], (
        f"Got {got}. deep -> middle -> lambda -> generator expression: four code objects. "
        "Recurse into co_consts of every nested code object, not just one level."
    )


def test_comprehension():
    assert globals_used(comprehension_user) == ["abs"], (
        "abs is used inside a list comprehension. (Before 3.12 a comprehension had its own code object, "
        "so this needs the nested search on 3.11.)"
    )


def test_undefined_globals():
    assert undefined_globals(report) == ["lenn"], (
        "price is a module global (in func.__globals__), lenn is not defined anywhere: only lenn is reported."
    )


def test_builtins_and_module_globals_are_defined():
    assert undefined_globals(price) == [], (
        "round is a builtin, RATE and math are module globals: none is undefined. "
        "Check both func.__globals__ and the builtins module (import builtins; vars(builtins))."
    )
    assert undefined_globals(repeated) == [], "len and max are builtins."


def test_undefined_in_nested_code():
    assert undefined_globals(deep) == ["helper_one", "helper_two"], (
        "sum is a builtin; helper_one and helper_two are defined nowhere."
    )

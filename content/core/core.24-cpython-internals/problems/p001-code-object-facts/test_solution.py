from solution import code_facts

RATE = 0.18


def price_with_tax(price, qty):
    subtotal = price * qty
    tax = subtotal * RATE
    return round(subtotal + tax, 2)


def greet(name, greeting="Hello", *extra, loud=False, **options):
    text = greeting + ", " + name
    if loud:
        text = text.upper()
    return text + "!"


def collect(items):
    out = []
    for item in items:
        out.append(str(item))
    return out


def seconds(days):
    return days * 86400 * 1.5


def nothing():
    pass


def blank_or_zero(flag):
    return "" if flag else 0.0


def test_returns_exactly_five_keys():
    facts = code_facts(price_with_tax)
    assert isinstance(facts, dict), "code_facts must return a dict."
    assert set(facts) == {"name", "argcount", "locals", "names", "constants"}, (
        "Use exactly the keys name, argcount, locals, names, constants."
    )


def test_name():
    assert code_facts(price_with_tax)["name"] == "price_with_tax", "name comes from co_name."
    assert code_facts(lambda x: x)["name"] == "<lambda>", "A lambda's code object is named '<lambda>'."


def test_argcount_counts_only_positional_parameters():
    assert code_facts(price_with_tax)["argcount"] == 2, "price and qty are two positional parameters."
    assert code_facts(greet)["argcount"] == 2, (
        "co_argcount counts name and greeting only: *extra, the keyword-only loud and **options are not included."
    )
    assert code_facts(nothing)["argcount"] == 0, "A function without parameters has co_argcount 0."


def test_locals_include_parameters_and_are_sorted():
    assert code_facts(price_with_tax)["locals"] == ["price", "qty", "subtotal", "tax"], (
        "locals is sorted(co_varnames): parameters AND variables assigned in the body."
    )
    assert code_facts(greet)["locals"] == ["extra", "greeting", "loud", "name", "options", "text"], (
        "*args, keyword-only and **kwargs parameters are local variables too; they are all in co_varnames."
    )
    assert code_facts(collect)["locals"] == ["item", "items", "out"], "The loop variable item is a local."


def test_names_hold_globals_builtins_and_attributes():
    assert code_facts(price_with_tax)["names"] == ["RATE", "round"], (
        "names is sorted(co_names): the global RATE and the built-in round. Did you use co_varnames by mistake?"
    )
    assert code_facts(collect)["names"] == ["append", "str"], (
        "Attribute names such as append also live in co_names, next to built-ins like str."
    )
    assert code_facts(greet)["names"] == ["upper"], "greet only uses the attribute name upper from co_names."


def test_constants_without_none():
    consts = code_facts(greet)["constants"]
    assert isinstance(consts, list), "constants must be a list."
    assert None not in consts, "Leave None out of constants; whether it is in co_consts depends on the version."
    assert ", " in consts and "!" in consts, "The string literals in the body are in co_consts."
    assert "Hello" not in consts, (
        "Default values are evaluated when def runs and stored in greet.__defaults__, not in greet's co_consts."
    )
    nums = code_facts(seconds)["constants"]
    assert 86400 in nums and 1.5 in nums, "Number literals like 86400 and 1.5 are constants of the function."
    assert code_facts(nothing)["constants"] == [], "A function whose body is pass has no constants except None."


def test_constants_keep_original_order():
    consts = code_facts(greet)["constants"]
    expected = [c for c in greet.__code__.co_consts if c is not None]
    assert consts == expected, "Keep co_consts order; only remove the None items."


def test_falsy_constants_are_kept():
    consts = code_facts(blank_or_zero)["constants"]
    assert "" in consts and 0.0 in consts, (
        "Only None is removed. Filter with 'c is not None', not 'if c': '' and 0.0 are falsy but real constants."
    )

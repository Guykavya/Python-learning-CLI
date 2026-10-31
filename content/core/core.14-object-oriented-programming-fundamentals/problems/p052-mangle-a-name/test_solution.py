import pytest

from solution import mangle


def real_python(class_name, attr):
    """Ask Python itself: define the class with one attribute and see which new key it stores."""
    namespace = {}
    exec(f"class {class_name}:\n    pass\n", namespace)
    before = set(vars(namespace[class_name]))
    exec(f"class {class_name}:\n    {attr} = 1\n", namespace)
    after = set(vars(namespace[class_name]))
    new = after - before
    return new.pop() if new else attr  # a dunder like __init__ may replace an existing key


def check(class_name, attr, want, why):
    assert want == real_python(class_name, attr), "test data error"
    got = mangle(class_name, attr)
    assert got == want, f"mangle({class_name!r}, {attr!r}) should be {want!r}, got {got!r}. {why}"


def test_simple_private_name():
    check("Account", "__pin", "_Account__pin", "Two leading underscores: add '_' + class name in front.")


def test_single_underscore_unchanged():
    check("Account", "_pin", "_pin", "One leading underscore is only a convention. Python does not rename it.")
    check("Account", "pin", "pin", "A normal name is never changed.")


def test_dunder_unchanged():
    check("Account", "__init__", "__init__", "Names that also END with two underscores (dunders) are not mangled.")
    check("Account", "__secret__", "__secret__", "Ends with __, so it is not mangled even if it is not a real dunder.")


def test_one_trailing_underscore_is_mangled():
    check("Account", "__pin_", "_Account__pin_", "Only TWO trailing underscores stop mangling. One is not enough.")


def test_leading_underscores_of_class_removed():
    check("_Secret", "__key", "_Secret__key", "Strip the leading underscores of the class name: _Secret -> Secret.")
    check("__Meta", "__key", "_Meta__key", "Strip ALL leading underscores of the class name: __Meta -> Meta.")


def test_three_underscores():
    check("Account", "___x", "_Account___x", "___x starts with __ and does not end with __, so it is mangled.")
    check("__Meta", "___x", "_Meta___x", "Strip the class underscores, keep the attribute as it is.")


def test_class_only_underscores():
    check("___", "__x", "__x", "If the class name is only underscores, nothing is left after stripping: no mangling.")
    check("_", "__x", "__x", "Class name '_' is only underscores too.")


def test_just_two_underscores():
    check("Account", "__", "__", "'__' starts with __ but also ends with __: not mangled.")


def test_class_name_with_inner_underscores():
    check("My_Class_", "__v", "_My_Class___v", "Only LEADING underscores are stripped. Inner and trailing ones stay.")
    check("_a_", "__v", "_a___v", "Use lstrip('_'), not strip('_').")


@pytest.mark.parametrize("class_name, attr", [("Point", "__x"), ("P2", "__x2"), ("Ü", "__wert"), ("A", "__a__b")])
def test_more_cases_against_python(class_name, attr):
    check(class_name, attr, real_python(class_name, attr), "Your result differs from what Python stores.")


@pytest.mark.parametrize("class_name, attr, bad", [("my-class", "__x", "my-class"), ("A", "__x y", "__x y"),
                                                   ("", "__x", ""), ("1st", "__x", "1st"), ("A", "", "")])
def test_not_identifiers(class_name, attr, bad):
    with pytest.raises(ValueError) as info:
        mangle(class_name, attr)
    assert str(info.value) == f"not an identifier: {bad!r}", f"The message is f\"not an identifier: {{text!r}}\" for the first bad name. Got {str(info.value)!r}."


def test_class_checked_first():
    with pytest.raises(ValueError, match="not an identifier: 'a b'"):
        mangle("a b", "c d")

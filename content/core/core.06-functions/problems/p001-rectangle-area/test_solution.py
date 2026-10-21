from solution import rectangle_area


def test_returns_area():
    assert rectangle_area(3, 4) == 12, (
        "rectangle_area(3, 4) should RETURN 12. If you printed it, the caller got None.")


def test_floats_and_zero():
    assert rectangle_area(2.5, 2) == 5.0, "Multiply width by height; floats work the same way."
    assert rectangle_area(0, 7) == 0, "A rectangle with width 0 has area 0."


def test_does_not_print(capsys):
    rectangle_area(5, 5)
    assert capsys.readouterr().out == "", (
        "The function printed something. Return the value and let the caller decide to print.")


def test_has_docstring():
    doc = rectangle_area.__doc__
    assert doc is not None and doc.strip(), (
        "Add a docstring: a string literal as the FIRST statement of the body. "
        "A # comment does not count.")

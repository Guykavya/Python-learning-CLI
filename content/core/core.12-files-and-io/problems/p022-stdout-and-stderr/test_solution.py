from solution import sum_numbers


def test_example(capsys):
    result = sum_numbers(["1", "x", "5"])
    out, err = capsys.readouterr()
    assert result == 6, "Return the total as well."
    assert out == "total: 6\n", "stdout must have only the line 'total: 6'. Warnings do not belong there."
    assert err == "warning: skipping 'x'\n", "Print the warning to stderr: print(..., file=sys.stderr), with the item in quotes."


def test_no_warnings(capsys):
    assert sum_numbers(["10", " 20 ", "-5"]) == 25, "int() accepts spaces and a minus sign."
    out, err = capsys.readouterr()
    assert out == "total: 25\n" and err == "", "No bad items: stderr must stay empty."


def test_many_bad_items_in_order(capsys):
    sum_numbers(["a", "2", "3.5", ""])
    out, err = capsys.readouterr()
    assert err == "warning: skipping 'a'\nwarning: skipping '3.5'\nwarning: skipping ''\n", "One warning per bad item, in order. '3.5' is not a whole number."
    assert out == "total: 2\n", "Only the good items are added."


def test_empty(capsys):
    assert sum_numbers([]) == 0, "No items gives 0."
    out, err = capsys.readouterr()
    assert out == "total: 0\n" and err == "", "Still print the total line."

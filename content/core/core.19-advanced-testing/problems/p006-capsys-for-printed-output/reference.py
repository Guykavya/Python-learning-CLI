from target import print_report


def test_one_sale_exact_text(capsys):
    print_report([("tea", 2.5)])
    assert capsys.readouterr().out == "tea: 2.50\nTOTAL: 2.50\n", "One line per sale, then TOTAL, two decimals."


def test_lines_are_sorted_by_name(capsys):
    print_report([("tea", 1.0), ("cake", 9.0), ("apple", 5.0)])
    lines = capsys.readouterr().out.splitlines()
    assert lines[:3] == ["apple: 5.00", "cake: 9.00", "tea: 1.00"], "Sort by NAME, not by amount or input order."


def test_total_is_the_sum_of_all(capsys):
    print_report([("a", 1.25), ("b", 2.5), ("c", 4)])
    assert capsys.readouterr().out.splitlines()[-1] == "TOTAL: 7.75", "TOTAL is the sum of every amount."


def test_amounts_use_two_decimals(capsys):
    print_report([("a", 4.5), ("b", 3)])
    out = capsys.readouterr().out
    assert "a: 4.50" in out and "b: 3.00" in out, "Format every amount with two decimals."
    assert out.splitlines()[-1] == "TOTAL: 7.50", "The total also has two decimals."


def test_empty_report(capsys):
    print_report([])
    assert capsys.readouterr().out == "No sales\n", "An empty list prints exactly 'No sales'."


def test_everything_goes_to_stdout(capsys):
    print_report([("a", 1)])
    captured = capsys.readouterr()
    assert captured.err == "", "Nothing should be written to stderr."
    assert captured.out.endswith("TOTAL: 1.00\n"), "TOTAL must be printed on stdout."

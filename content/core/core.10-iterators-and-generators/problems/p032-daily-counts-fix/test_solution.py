from solution import count_by_day


def test_sorted_logs():
    lines = ["2026-10-05 login ann", "2026-10-05 login bob", "2026-10-06 login cy"]
    assert count_by_day(lines) == {"2026-10-05": 2, "2026-10-06": 1}, "Count the lines of each date."


def test_merged_logs():
    lines = [
        "2026-10-05 login ann",
        "2026-10-06 login bob",
        "",
        "2026-10-05 login cy",
        "2026-10-05 login dev",
    ]
    assert count_by_day(lines) == {"2026-10-05": 3, "2026-10-06": 1}, "Merged logs are NOT sorted. groupby only joins NEIGHBOURS, so 2026-10-05 forms two groups and the second count replaces the first."


def test_many_switches():
    lines = ["2026-01-01 a", "2026-01-02 b"] * 4
    assert count_by_day(lines) == {"2026-01-01": 4, "2026-01-02": 4}, "Dates alternate: every date must be totalled over the WHOLE input, not only its last run."


def test_blank_lines_skipped():
    assert count_by_day(["", "   ", "2026-02-02 x", "\n"]) == {"2026-02-02": 1}, "Blank lines (also only spaces or a newline) do not count."


def test_empty():
    assert count_by_day([]) == {}, "No lines give an empty dict."


def test_generator_input():
    gen = (line for line in ["2026-03-01 a", "2026-03-02 b", "2026-03-01 c"])
    assert count_by_day(gen) == {"2026-03-01": 2, "2026-03-02": 1}, "lines can be a generator (read only once), and here the dates are not in order: 2026-03-01 must be totalled over both runs."

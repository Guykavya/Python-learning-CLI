from target import clamp


def test_below_the_range():
    assert clamp(-5, 0, 10) == 0, "A value below low must become low."


def test_above_the_range():
    assert clamp(15, 0, 10) == 10, "A value above high must become high."


def test_inside_the_range():
    assert clamp(5, 0, 10) == 5, "A value inside the range must stay unchanged."


def test_on_the_edges():
    assert clamp(0, 0, 10) == 0, "x equal to low is inside the range."
    assert clamp(10, 0, 10) == 10, "x equal to high is inside the range."


def test_negative_range():
    assert clamp(-5, -10, -1) == -5, "Negative numbers inside a negative range stay unchanged."
    assert clamp(-20, -10, -1) == -10, "Negative values below the range become low."

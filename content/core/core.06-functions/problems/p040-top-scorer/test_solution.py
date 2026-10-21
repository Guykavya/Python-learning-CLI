from solution import top_scorer


def test_example():
    assert top_scorer({"Ravi": 40, "Asha": 55, "Meena": 50}) == "Asha", "Return the NAME with the highest score."


def test_tie_alphabetical():
    assert top_scorer({"zoya": 60, "kiran": 60, "anu": 10}) == "kiran", (
        "Tie on 60: return the alphabetically first name, 'kiran', not the first in the dict.")
    assert top_scorer({"b": 5, "c": 5, "a": 5}) == "a"


def test_one_and_negative():
    assert top_scorer({"solo": -3}) == "solo"
    assert top_scorer({"x": -5, "y": -2}) == "y"


def test_empty():
    assert top_scorer({}) is None, "An empty dict has no top scorer: return None."


def test_dict_unchanged():
    d = {"a": 1, "b": 2}
    top_scorer(d)
    assert d == {"a": 1, "b": 2}

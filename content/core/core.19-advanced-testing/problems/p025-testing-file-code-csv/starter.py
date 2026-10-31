# Save the code from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py -p no:cacheprovider
import pytest

from target import summarise


def test_one_category(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("category,amount\nfood,10\n")
    assert summarise(path) == {"food": 10.0}

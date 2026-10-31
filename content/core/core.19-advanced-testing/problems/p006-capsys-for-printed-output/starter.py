# Save the code from problem.md as target.py in this folder, then run:
#     python -m pytest solution.py
from target import print_report


def test_one_sale(capsys):
    print_report([("tea", 2.5)])
    assert "tea" in capsys.readouterr().out
